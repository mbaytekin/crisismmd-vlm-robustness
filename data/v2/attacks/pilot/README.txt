CrisisMMD V2 pilot attack verisi
===============================

Kapsam: 99 sample, her sample için 10 koşul, toplam 990 manifest kaydı.
Bu klasörde PNG bulunan koşullar image ve joint koşullarıdır. Clean ve text-only
koşulları için manifestteki original_image_path kullanılır.

Koşullar:

- clean
- benign_image / benign_text / benign_joint
- direct_image / direct_text / direct_joint
- misleading_image / misleading_text / misleading_joint

Attack türleri:

- benign: Nötr kontrol payload'ı; model sınıflandırmasını yönlendirmemesi amaçlanır.
- direct_instruction: little_or_no_damage yönüne doğrudan sınıflandırma talimatı.
- misleading_claim: Görüntüdeki hasarla çelişen güvenlik/hasar iddiası.

Modalite:

- image: Payload PNG üzerine yazılır, tweet clean kalır.
- text: Görsel clean kalır; tweet şu biçimdedir:
  payload + iki newline + original_tweet
- joint: Aynı payload ID hem PNG'de hem tweet başında kullanılır.

Görsel stil ve boyut:

- Görsel saldırılarda simple_overlay_v2 kullanılır.
- Varsayılan boyut medium oranıdır; nominal font oranı yaklaşık %5'tir.
- Varsayılan opacity 0.88'dir.
- Placement top_edge veya bottom_edge olabilir.

Örnek dosya:
  benign_image/<sample_id>.png

Detay için:
  ../../manifests/all_conditions.csv
  ../../manifests/text_conditions.csv
