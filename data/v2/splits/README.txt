CrisisMMD V2 ablation split dosyaları
=====================================

style_ablation.csv
------------------
180 örnek; sınıf başına 60 sample.

size_ablation.csv
-----------------
90 örnek; sınıf başına 30 sample.

Bu iki split, pilot ve main splitlerden sample_id, SHA-256 ve pHash seviyesinde
ayrı tutulmak üzere kullanılmayan örneklerden seçilmiştir.

Orijinal splitler:

- data/splits/pilot.csv: 99 sample
- data/splits/test.csv: 900 sample

V2 split bütünlüğü:
  reports/v2/split_validation.md
  reports/v2/audit/audit_summary.md
