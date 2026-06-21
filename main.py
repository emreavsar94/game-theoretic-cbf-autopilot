import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches
import numpy as np
import random

from vehicle_plant import Arac
from cbf_filter import guvenlik_kalkani
from perception import CevreSensoru
from planner import OtonomPlanlayici

DEBUG_MODU = True  # Kalkanı ve tavşanı ekranda görmek için True, sade HUD için False yapın

def kinematik_kontrolcu(arac, hedef_hiz, tavsan_y):
    # İvme (P kontrol)
    hata_v = hedef_hiz - arac.v_x
    a_x = max(-4.0, min(2.0, 0.4 * hata_v)) 
    
    # Direksiyon (Yanal takip)
    hata_y = tavsan_y - arac.y
    hedef_theta = np.clip(hata_y * 0.15, -0.15, 0.15) # Yola doğru yönel
    direksiyon = 1.2 * (hedef_theta - arac.theta)     # Burnunu o açıya oturt
    direksiyon = np.clip(direksiyon, -0.15, 0.15)
    
    return a_x, direksiyon

def simule_et():
    # Sistem Kurulumu
    sensor = CevreSensoru(gorus_mesafesi=120.0)
    beyin = OtonomPlanlayici(hiz_limiti_ms=33.3) # 120 km/h
    
    # Senaryo Kurulumu
    ego = Arac(id_no=0, x_init=0.0, y_init=0.0, v_x_init=25.0) # Bizim Aracımız
    kamyon = Arac(id_no=1, x_init=60.0, y_init=0.0, v_x_init=19.4) # Öndeki Yavaş Tır (70 km/h)
    hizli_arac = Arac(id_no=2, x_init=-30.0, y_init=4.0, v_x_init=36.0) # Sol Arkadaki Tehdit (130 km/h)
    trafik = {
        1: (kamyon, 19.4),
        2: (hizli_arac, 36.0)
    }
    arac_sayaci = 3

    # Görsel Arayüz
    bg_color = '#F5F5F7'        # Yumuşak arka plan
    road_color = '#D1D1D6'      # Açık gri yol sınırları
    ego_color = '#007AFF'       # Modern mavi
    target_color = '#FF3B30'    # Pastel kırmızı
    cbf_color = '#34C759'       # Soft yeşil

    fig, ax = plt.subplots(figsize=(14, 5))
    fig.patch.set_facecolor(bg_color)
    ax.set_facecolor(bg_color)
    fig.canvas.manager.set_window_title('Otonom Sürüş Mimarisi | Game Theory & CBF')

    dt = 0.05

    def update(frame):
        nonlocal arac_sayaci, trafik
        ax.clear()

        # Trafik Motoru (Spawner / Çöp Toplayıcı)
        trafik = {k: v for k, v in trafik.items() if ego.x - 100 < v[0].x < ego.x + 200}

        if len(trafik) < 4 and random.random() < 0.05: 
            tip = random.choice(["yavas_on", "hizli_arka"])
            yeni_x = ego.x + random.uniform(130.0, 160.0) if tip == "yavas_on" else ego.x - random.uniform(60.0, 80.0)
            yeni_y = 0.0 if tip == "yavas_on" else 4.0
            yeni_v = random.uniform(15.0, 20.0) if tip == "yavas_on" else random.uniform(30.0, 38.0)

            if not any(abs(v[0].x - yeni_x) < 20.0 and v[0].y == yeni_y for v in trafik.values()):
                trafik[arac_sayaci] = (Arac(id_no=arac_sayaci, x_init=yeni_x, y_init=yeni_y, v_x_init=yeni_v), yeni_v)
                arac_sayaci += 1

        trafik_listesi = [v[0] for v in trafik.values()]

        # Otonom Sürüş Döngüsü (Sense -> Plan -> Act)
        cevre_grid = sensor.cevreyi_tara(ego, trafik_listesi) 
        hedef_hiz, tavsan_y = beyin.rota_ve_hiz_belirle(ego, cevre_grid, dt)
        a_x_nom, direksiyon = kinematik_kontrolcu(ego, hedef_hiz, tavsan_y)
        cbf_a_x = guvenlik_kalkani(ego, trafik_listesi, a_x_nom)
        ego.guncelle(cbf_a_x, direksiyon, dt)

        # Trafik Araçlarının Hareketi
        for t_id, (arac, t_hedef_hiz) in trafik.items():
            a_x_trafik, direksiyon_trafik = kinematik_kontrolcu(arac, t_hedef_hiz, arac.y)
            a_x_guvenli = guvenlik_kalkani(arac, [ego] + trafik_listesi, a_x_trafik)
            arac.guncelle(a_x_guvenli, direksiyon_trafik, dt)

        # Görselleştirme
        for i in np.arange(int(ego.x-40), int(ego.x+150), 15):
            ax.plot([i, i+7], [2, 2], color=road_color, lw=2)
        ax.axhline(-2, color=road_color, lw=2)
        ax.axhline(6, color=road_color, lw=2)

        for obj in [ego] + trafik_listesi:
            renk = ego_color if obj.id == 0 else target_color
            ax.add_patch(patches.FancyBboxPatch((obj.x-2.25, obj.y-0.9), 4.5, 1.8, boxstyle="round,pad=0.2", color=renk, zorder=3))
            ax.text(obj.x, obj.y, f"{obj.v_x*3.6:.0f}", color='white', fontsize=10, fontweight='bold', ha='center', va='center', zorder=4)

        if DEBUG_MODU:
            # Sanal Tavşan Noktası Çizimi
            ax.plot(ego.x + 10.0, tavsan_y, marker='o', markersize=6, color='#00d2d3', zorder=5)

            # CBF Güvenlik Elipsi Çizimi
            a_ell = 10.0 + (0.8 * ego.v_x)
            ellipse = patches.Ellipse((ego.x, ego.y), a_ell*2, 5.6, angle=0, linewidth=1.2, edgecolor=cbf_color, facecolor='none', linestyle='--', alpha=0.5)
            ax.add_patch(ellipse)

        ax.set_xlim(ego.x - 30, ego.x + 130)
        ax.set_ylim(-6, 18)
        ax.set_aspect('equal')
        ax.axis('off')
        
        if tavsan_y == 4.0 and ego.y > 3.8:
            durum_metni = "SOLLAMA (SOL ŞERİT)"
        elif tavsan_y == 0.0 and ego.y < 0.2:
            durum_metni = "ASLİ SEYİR (SAĞ ŞERİT)"
        elif tavsan_y > ego.y + 0.1:
            durum_metni = "SOLA GEÇİŞ MANEVRASI"
        elif tavsan_y < ego.y - 0.1:
            durum_metni = "SAĞA DÖNÜŞ MANEVRASI"
        else:
            durum_metni = "ŞERİT ORTALANIYOR"

        bilgi = (f"FSM Durumu: {durum_metni}\n"
                 f"Hız (Hedef / Gerçek): {hedef_hiz*3.6:.0f} / {ego.v_x*3.6:.0f} km/h\n"
                 f"İvme: {cbf_a_x:+.2f} m/s² | Direksiyon: {np.degrees(direksiyon):+.1f}°")
                 
        ax.text(0.02, 0.95, bilgi, transform=ax.transAxes, fontsize=11, color='#1C1C1E', 
                verticalalignment='top', bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.9, edgecolor='#E5E5EA'))

    ani = animation.FuncAnimation(fig, update, frames=800, interval=20, blit=False)
    plt.show()

if __name__ == "__main__":
    simule_et()