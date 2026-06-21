import numpy as np
from game_theory import serit_degisimi_onayla

class OtonomPlanlayici:
    def __init__(self, hiz_limiti_ms=33.3): # 120 km/h
        self.hiz_limiti = hiz_limiti_ms 
        self.aktif_hedef_serit = 0.0 
        self.tavsan_y = 0.0 # Sanal referans noktası
        
    def rota_ve_hiz_belirle(self, ego_arac, grid, dt):
        hedef_hiz = self.hiz_limiti
        on_arac = grid['orta_on']
        on_tikali = on_arac is not None and (on_arac.x - ego_arac.x) < 40.0
        sollama_menzili = on_arac is not None and (on_arac.x - ego_arac.x) < 80.0

        # if ego_arac.kilit_sayaci > 0:
        #    return hedef_hiz, self.aktif_hedef_serit

        # ==================================================
        # DURUM MAKİNESİ (STATE MACHINE)
        # ==================================================
        if ego_arac.kilit_sayaci <= 0:
            if ego_arac.y < 2.0: # SAĞ ŞERİT
                if sollama_menzili:
                    if serit_degisimi_onayla(ego_arac, grid, yon="sol"):
                        self.aktif_hedef_serit = 4.0
                        ego_arac.kilit_sayaci = 4.0 
                    elif on_tikali:
                        hedef_hiz = on_arac.v_x
            else: # SOL ŞERİT
                if serit_degisimi_onayla(ego_arac, grid, yon="sag"):
                    self.aktif_hedef_serit = 0.0
                    ego_arac.kilit_sayaci = 4.0 
                elif on_tikali:
                    hedef_hiz = on_arac.v_x
        else:
            if on_tikali and self.tavsan_y < 2.0:
                hedef_hiz = on_arac.v_x

        # Tavşanı hedef şeride doğru kaydır 
        tavsan_hizi = 1.0
        adim = np.clip(self.aktif_hedef_serit - self.tavsan_y, -tavsan_hizi * dt, tavsan_hizi * dt)
        self.tavsan_y += float(adim)

        return hedef_hiz, self.tavsan_y