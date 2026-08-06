CrisisMMD V2 size ablation attack verisi
=========================================

Kapsam: 90 sample, 10 koşul, toplam 900 kayıt.
Size ablation image-only simple overlay deneyidir; tweet metni clean kalır.

Koşullar:

- clean
- benign_small / benign_medium / benign_large
- direct_small / direct_medium / direct_large
- misleading_small / misleading_medium / misleading_large

Nominal text size hedefleri:

- small: yaklaşık %3 font-height oranı
- medium: yaklaşık %5 font-height oranı
- large: yaklaşık %8 font-height oranı

Diğer nominal renderer özellikleri:

- Stil: simple_overlay_v2
- Opacity: 0.88
- Yazı rengi: beyaz
- Panel: siyah yarı saydam overlay
- Placement ve bbox metadata manifestte tutulur.

Önemli audit uyarısı:

Size ablation planı size dışındaki değişkenleri sabit tutmayı amaçlıyor; ancak
independent audit, 89 sample grubunda placement_region değerinin small/medium/
large arasında değiştiğini buldu. Bu nedenle sonuçlar saf size karşılaştırması
olarak değil, size + placement karşılaştırması olarak raporlanmalıdır.

Ayrıca küçük kaynak görsellerde tam payload'ı korumak için renderer fontu
nominal minimumun altına indirebilir. Bu örnekler manuel okunabilirlik incelemesi
gerektirir.

Detay manifesti:
  ../../manifests/all_conditions.csv

Audit çıktıları:
  ../../../../reports/v2/audit/audit_summary.md
  ../../../../reports/v2/audit/audit_issues.csv
