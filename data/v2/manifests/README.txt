CrisisMMD V2 manifest dosyaları
==============================

all_conditions.csv / all_conditions.parquet
--------------------------------------------

Her satır bir sample_id + condition deney kaydıdır. Önemli alanlar:

- sample_id, split_name, condition
- attack_modality: none, image, text veya joint
- attack_semantics: none, benign, direct_instruction veya misleading_claim
- visual_style: simple_overlay, news_banner veya camouflage
- text_size: small, medium, large veya none
- payload_id, payload_text
- original_image_path, condition_image_path
- original_tweet, condition_tweet
- ground_truth, event_name
- text_bbox, font_size_px, occupied_area_ratio, opacity
- placement_region, contrast_ratio, edge_density, local_variance

payload_assignments.csv
-----------------------

Her sample için benign, direct ve misleading payload ID atamasını içerir.
assignment_seed=42 kullanılmıştır. Aynı sample'ın ilgili image/text/joint veya
style/size koşulları aynı payload ailesini kullanmalıdır.

text_conditions.csv
-------------------

Text-only ve joint koşulların tweet alanlarını açıkça listeler. condition_tweet
şu kurala göre oluşturulur:

payload_text + iki newline + original_tweet

truncated alanı, orijinal tweetin korunup korunmadığını belirtir.

Kontrol komutları ve sonuçları:

- Attack validation: reports/v2/attack_validation_<split>.md
- Independent audit: reports/v2/audit/audit_summary.md
