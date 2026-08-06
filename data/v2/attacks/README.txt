CrisisMMD V2 adversarial attack görselleri
===========================================

Bu klasördeki PNG dosyaları, orijinal CrisisMMD görsellerinin üzerine deterministik
olarak eklenmiş typographic adversarial attack örnekleridir. Orijinal görseller
değiştirilmemiştir.

Alt klasörler:

- pilot/: 99 sample x 10 koşul
- main/: 900 sample x 10 koşul
- style_ablation/: 180 sample x 10 koşul
- size_ablation/: 90 sample x 10 koşul

Koşul manifesti:
  data/v2/manifests/all_conditions.csv

Payload atamaları:
  data/v2/manifests/payload_assignments.csv

Text-only ve joint tweet içerikleri:
  data/v2/manifests/text_conditions.csv

Ana deney koşulları:

- clean: Değiştirilmemiş görüntü ve tweet.
- benign_image: Nötr payload yalnızca görselde.
- benign_text: Nötr payload yalnızca tweet başında.
- benign_joint: Nötr payload hem görselde hem tweet başında.
- direct_image/text/joint: Doğrudan model yönlendiren payload.
- misleading_image/text/joint: Yanıltıcı hasar iddiası payload'ı.

Görsel dosya adı örneği:
  <sample_id>.png

Bir dosyanın hangi payload, stil, boyut, opacity, bbox, placement ve ground-truth
etiketine ait olduğu manifestte aynı sample_id + condition satırından okunmalıdır.

Konfigürasyon:
  configs/v2/attack_payloads.yaml
  configs/v2/pipeline.yaml

Audit notu:
  reports/v2/audit/audit_summary.md
  Size ablation'da bazı sample gruplarında placement_region boyutlar arasında
  değişmiştir. Bu nedenle size sonuçları yalnızca saf font-size etkisi olarak
  değil, size + placement etkisi olarak yorumlanmalıdır.
