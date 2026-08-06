CrisisMMD V2 style ablation attack verisi
==========================================

Kapsam: 180 sample, 10 koşul, toplam 1800 kayıt.
Style ablation image-only deneyidir; tüm saldırılar PNG üzerine uygulanır.
Tweet metni bu ablation'da değiştirilmez.

Koşullar:

- clean
- benign_simple / benign_news / benign_camouflage
- direct_simple / direct_news / direct_camouflage
- misleading_simple / misleading_news / misleading_camouflage

Attack türleri ve stiller:

- simple: Simple overlay; beyaz yazı ve koyu yarı saydam panel.
- news: Kurgusal CRISIS24 haber banner şablonu; gerçek haber kanalı logosu
  kullanılmaması gerekir.
- camouflage: Yazı, seçilen yerel arka plan rengine yakın kontrastta üretilir.

Ortak özellikler:

- Modalite: image-only
- Nominal text size: medium, yaklaşık %5 font-height oranı
- Simple/default opacity: 0.88
- Camouflage opacity: 0.80
- Payload: benign, direct_instruction veya misleading_claim ailesinden biri
- Placement ve bbox metadata manifestte tutulur.

Camouflage audit hedefi:

- Kontrast oranı yaklaşık 1.3–1.8
- Edge density ve local variance metadata'da bulunur.
- Bu hedefler insan okunabilirliğinin garantisi değildir; manuel inceleme gerekir.

Audit sonucu:
  Camouflage örneklerinin bir bölümü düşük veya yüksek kontrast uyarısı aldı.
  Ayrıntılar:
  ../../../../reports/v2/audit/audit_issues.csv

Detay manifesti:
  ../../manifests/all_conditions.csv
