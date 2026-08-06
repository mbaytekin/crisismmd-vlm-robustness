# V2 pilot results

Run: `v2_pilot_20260805_193500`; parsed predictions: 990 / 990

| condition | accuracy | macro F1 | balanced accuracy | ASR (success/clean-correct) | severity drop | severe under-triage | critical under-triage | benign effect |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 0.495 | 0.469 | 0.495 | NA | NA | NA | NA | NA |
| benign_image | 0.495 | 0.469 | 0.495 | 0.020 (1/49) | -0.030303030303030304 | 0.21212121212121213 | 0.06060606060606061 | 0.051 (5/99) |
| benign_text | 0.485 | 0.459 | 0.485 | 0.041 (2/49) | 0.010101010101010102 | 0.21212121212121213 | 0.06060606060606061 | 0.030 (3/99) |
| benign_joint | 0.485 | 0.452 | 0.485 | 0.061 (3/49) | -0.0707070707070707 | 0.18181818181818182 | 0.030303030303030304 | 0.081 (8/99) |
| direct_image | 0.465 | 0.416 | 0.465 | 0.429 (21/49) | 0.6464646464646465 | 0.42424242424242425 | 0.42424242424242425 | NA |
| direct_text | 0.465 | 0.445 | 0.465 | 0.204 (10/49) | 0.23232323232323232 | 0.2727272727272727 | 0.18181818181818182 | NA |
| direct_joint | 0.434 | 0.409 | 0.434 | 0.388 (19/49) | 0.5454545454545454 | 0.42424242424242425 | 0.42424242424242425 | NA |
| misleading_image | 0.566 | 0.567 | 0.566 | 0.204 (10/49) | 0.47474747474747475 | 0.3333333333333333 | 0.21212121212121213 | NA |
| misleading_text | 0.525 | 0.527 | 0.525 | 0.204 (10/49) | 0.3939393939393939 | 0.3333333333333333 | 0.18181818181818182 | NA |
| misleading_joint | 0.535 | 0.536 | 0.535 | 0.204 (10/49) | 0.43434343434343436 | 0.3333333333333333 | 0.21212121212121213 | NA |

ASR uses only clean-correct examples. Severity drop is clean prediction level minus attacked prediction level, with 0=little/no, 1=mild, 2=severe. No human review labels are filled automatically.
