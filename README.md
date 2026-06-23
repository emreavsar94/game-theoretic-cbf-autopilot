# Game-Theoretic Autonomous Driving Simulator with Safety Filter (CBF)

![Otonom Sollama Simülasyonu Demo Videosu](otonom_sollama.gif)

Bu proje; derin öğrenme "kara kutularına" (black-box) bağlı kalmadan, tamamen açıklanabilir (**explainable AI**) ve deterministik kurallarla çalışan modüler bir otonom sürüş ve otoban sollama simülatörüdür. 

Proje, endüstri standardı olan **Sense-Plan-Act (Algıla-Planla-Uygula)** mimarisi üzerine inşa edilmiştir ve her katman birbirinden tamamen izole (decoupled) durumdadır.


## 🛠️ Sistem Mimarisi & Modüller

1. **Fizik Katmanı (`vehicle_plant.py`):** Noktasal kütle modelleri yerine, aracın yönelimini ($\theta$) ve dingil mesafesini ($L$) hesaba katan **Kinematik Bisiklet Modeli (Kinematic Bicycle Model)** kullanılmıştır. Araç durumları ($\theta$ ve $y$ konumu) fiziksel sınırlarla sınırlandırılmıştır.
2. **Algı Katmanı (`perception.py`):** Ego aracın çevresini 3x3'lük dinamik bir grid'e (Sol/Orta/Sağ ve Ön/Yan/Arka) bölerek en yakın tehditleri takip eden ve şerit değiştirme esnasındaki kör noktaları reel sayı doğrusu üzerinde eksiksiz filtreleyen bir çevre tarama algoritması içerir.
3. **Karar Mekanizması (`game_theory.py` & `planner.py`):** Şerit değişim kararlarında çevredeki araçların niyetlerini **Oyun Teorisi (Expected Utility)** ile analiz eder. Sistem; arkadan gelen araçların son 1 saniyedeki hız trendlerini inceleyen bir **Zamansal Hafızaya (Behavioral Memory)** ve yaklaşma hızına göre riski üstel büyüten **Dinamik TTC (Time-to-Collision) Ceza Ölçeklendirmesine** sahiptir. Modül; Normal, Agresif ve Korkak olmak üzere farklı otopilot sürüş profillerini ve çok oyunculu (multi-player) veto kararlarını destekler. Pürüzsüz şerit geçişleri için **Virtual Rabbit (Sanal Tavşan)** yörünge üreteci entegre edilmiştir.
4. **Güvenlik Kalkanı (`cbf_filter.py`):** Karar mekanizması hatalı bir sollama emri üretse dahi, acil durumlarda **Control Barrier Functions (CBF)** ve `cvxpy (OSQP solver)` kullanarak kazayı matematiksel olarak %100 engelleyen çelik bir güvenlik katmanı sunar. Slack variable entegrasyonu ve matris ölçekleme (scaling) optimizasyonları ile çözücü üzerindeki tüm sayısal kararsızlıklar ve tolerans uyarıları giderilmiştir.

## 🚀 Performans ve Veri Yapısı Optimizasyonu
Simülasyonun arka planında bellek şişmesini (Memory Leak) önlemek amacıyla dinamik bir **Çöp Toplayıcı (Garbage Collector)** kurgulanmıştır. 
* Trafik ortamı, senkronizasyon hatalarını ve hafıza sızıntılarını sıfırlamak adına tek bir **`trafik = {id: (Arac, hedef_hiz)}`** (Single Source of Truth) sözlük yapısı üzerinden hafif ve optimize şekilde yönetilir.
* Görüş alanından (Ego aracın 100m arkası ve 200m önü) çıkan araçlar bellekten temizlenir.

## 🔮 Gelecek Geliştirmeler (Future Work) & Teorik Derinlik
* **HO-CBF (Higher-Order CBF) Entegrasyonu:** Mevcut sistemde kontrol girdimiz ivme ($u$) iken güvenlik bariyerimiz konum tabanlıdır ($\Delta x, \Delta y$). Matematiksel olarak bu durum **Relative Degree = 2** (İkinci Dereceden) bir problem teşkil eder. Mevcut yapı hız diferansiyeli üzerinden problemi birinci dereceye indirgeyerek çözmektedir; gelecek aşamalarda sistemin *Yüksek Dereceden Kontrol Bariyer Fonksiyonları (HO-CBF)* ile diferansiyel olarak genişletilmesi planlanmaktadır.
* **Dinamik Oyun Teorisi:** Sabit kazanç (payoff) matrisleri yerine, anlık trafik yoğunluğuna ve yol yapısına göre dinamik olarak güncellenen ağırlıklı olasılık matrislerinin kurgulanması.

## 💻 Kurulum ve Çalıştırma

Projeyi yerelde çalıştırmak için gerekli kütüphaneleri yükleyin:
```bash
pip install matplotlib numpy cvxpy osqp