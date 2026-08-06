# V2 pilot quality gate

Run: `v2_pilot_20260805_193500`

| check | result |
|---|---|
| attack_validation_passed | PASS |
| records_990 | PASS |
| all_10_conditions_99 | PASS |
| parse_errors_zero | PASS |
| single_prompt_hash | PASS |
| single_model_id | PASS |
| vision_backend | PASS |
| payload_ids_present_for_attacks | PASS |

Overall: **PASS**.

Main and ablation inference must not start when this gate fails. Human review remains unfilled.
