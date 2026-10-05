import csv
import os
from decimal import Decimal

# Root project paths
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(project_root, "data")
output_dir = os.path.join(project_root, "output")

os.makedirs(output_dir, exist_ok=True)

tickets_path = os.path.join(data_dir, "tickets.csv")
dup_recon_path = os.path.join(output_dir, "duplicate_reconciliation.csv")

def run_clean_dataset_pipeline():
    with open(tickets_path, "r", encoding="utf-8") as f:
        tickets_raw = list(csv.DictReader(f))

    for idx, r in enumerate(tickets_raw, 1):
        r['_orig_row_num'] = idx

    tickets_by_id = {}
    for r in tickets_raw:
        tid = r['ticket_id']
        if tid not in tickets_by_id:
            tickets_by_id[tid] = []
        tickets_by_id[tid].append(r)

    clean_tickets = []
    dedup_audit = []
    norm_audit = []

    for tid in sorted(tickets_by_id.keys()):
        rows = tickets_by_id[tid]
        
        if len(rows) == 2:
            hd_row = next(r for r in rows if r['source_system'] == 'helpdesk')
            leg_row = next(r for r in rows if r['source_system'] == 'legacy_fd')
            
            dedup_audit.append({
                'ticket_id': tid,
                'source_system': 'helpdesk',
                'original_row_reference': hd_row['_orig_row_num'],
                'retained_or_excluded': 'RETAINED',
                'duplicate_classification': 'DUPLICATE_PAIRED_AUTHORITATIVE',
                'decision_reason': 'Retained helpdesk copy as authoritative source for duplicate ticket_id',
                'original_refund_amount': hd_row['refund_amount_inr'],
                'normalized_refund_amount': hd_row['refund_amount_inr']
            })
            
            dedup_audit.append({
                'ticket_id': tid,
                'source_system': 'legacy_fd',
                'original_row_reference': leg_row['_orig_row_num'],
                'retained_or_excluded': 'EXCLUDED',
                'duplicate_classification': 'DUPLICATE_PAIRED_REDUNDANT',
                'decision_reason': 'Excluded legacy_fd migration copy in favor of authoritative helpdesk copy',
                'original_refund_amount': leg_row['refund_amount_inr'],
                'normalized_refund_amount': f"{Decimal(leg_row['refund_amount_inr'])/100:.2f}" if leg_row['refund_amount_inr'] != '' else ''
            })
            
            retained_tickets_for_id = [hd_row]
            
        else:
            single_row = rows[0]
            retained_tickets_for_id = [single_row]
            
            dedup_audit.append({
                'ticket_id': tid,
                'source_system': single_row['source_system'],
                'original_row_reference': single_row['_orig_row_num'],
                'retained_or_excluded': 'RETAINED',
                'duplicate_classification': 'UNIQUE_TICKET',
                'decision_reason': 'Retained single unique ticket record',
                'original_refund_amount': single_row['refund_amount_inr'],
                'normalized_refund_amount': (
                    f"{Decimal(single_row['refund_amount_inr'])/100:.2f}"
                    if single_row['source_system'] == 'legacy_fd' and single_row['refund_amount_inr'] != ''
                    else single_row['refund_amount_inr']
                )
            })

        for r in retained_tickets_for_id:
            src = r['source_system']
            orig_ref = r['refund_amount_inr']
            
            if src == 'helpdesk':
                if orig_ref != '':
                    norm_ref = f"{Decimal(orig_ref):.2f}"
                    norm_rule = 'HELPDESK_INR_UNCHANGED'
                    val_status = 'VALIDATED'
                else:
                    norm_ref = ''
                    norm_rule = 'NO_REFUND_AMOUNT'
                    val_status = 'VALIDATED_NULL'
            else:
                if orig_ref != '':
                    norm_ref = f"{Decimal(orig_ref)/Decimal(100):.2f}"
                    norm_rule = 'LEGACY_FD_PAISE_DIVIDED_BY_100'
                    val_status = 'VALIDATED_CONVERTED'
                else:
                    norm_ref = ''
                    norm_rule = 'NO_REFUND_AMOUNT'
                    val_status = 'VALIDATED_NULL'

            norm_audit.append({
                'ticket_id': r['ticket_id'],
                'source_system': src,
                'original_refund_amount': orig_ref,
                'normalized_refund_amount': norm_ref,
                'normalization_rule': norm_rule,
                'validation_status': val_status
            })

            flags = []
            if r['order_id'] == '':
                flags.append('MISSING_ORDER_ID')
            if norm_ref != '' and Decimal(norm_ref) > 0 and r['replacement_issued'] == 'Y':
                flags.append('REFUND_AND_REPLACEMENT_CONFLICT')
            if r['csat_score'] == '':
                flags.append('MISSING_CSAT_SCORE')
            if r['resolved_at'] == '' and r['status'] in ('resolved', 'closed'):
                flags.append('RESOLVED_WITHOUT_TIMESTAMP')
            if r['refund_reason_code'] == 'GW-OTHER':
                flags.append('DEFAULT_REASON_CODE')
                if norm_ref != '' and Decimal(norm_ref) > Decimal('500.00'):
                    flags.append('GOODWILL_EXCEEDS_500_CAP')
                
            has_flag = 'Y' if flags else 'N'

            clean_row = {
                'ticket_id': r['ticket_id'],
                'created_at': r['created_at'],
                'first_response_at': r['first_response_at'],
                'resolved_at': r['resolved_at'],
                'status': r['status'],
                'channel': r['channel'],
                'customer_id': r['customer_id'],
                'order_id': r['order_id'],
                'product_sku': r['product_sku'],
                'category': r['category'],
                'priority': r['priority'],
                'assigned_team': r['assigned_team'],
                'agent_id': r['agent_id'],
                'transfers': r['transfers'],
                'csat_score': r['csat_score'],
                'refund_amount_original': orig_ref,
                'refund_amount_inr_normalized': norm_ref,
                'normalization_rule': norm_rule,
                'refund_reason_code': r['refund_reason_code'],
                'replacement_issued': r['replacement_issued'],
                'customer_message': r['customer_message'],
                'agent_notes': r['agent_notes'],
                'source_system': src,
                'quality_flags': ";".join(flags),
                'has_quality_flag': has_flag,
                'original_row_reference': r['_orig_row_num']
            }
            clean_tickets.append(clean_row)

    clean_tickets_path = os.path.join(output_dir, "clean_tickets.csv")
    clean_fieldnames = list(clean_tickets[0].keys())

    with open(clean_tickets_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=clean_fieldnames)
        writer.writeheader()
        writer.writerows(clean_tickets)

    return len(clean_tickets)

if __name__ == "__main__":
    count = run_clean_dataset_pipeline()
    print(f"Clean dataset built: {count} rows")
