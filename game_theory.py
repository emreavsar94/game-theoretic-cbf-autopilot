import math

PROFILLER = {
    "normal": {
        "change_coop": 15.0,   # Yol verirse şeridi aldık
        "change_agg": -50.0,   # Gaza basarsa kaza riski cezası
        "keep_coop": -5.0,     # Fırsatı kaçırdık
        "keep_agg": 5.0        # Geçmesine izin vermek makul karar
    },
    "agresif": {
        "change_coop": 30.0,   # Şerit değiştirmeye aşırı istekli
        "change_agg": -20.0,   # Kaza riskini çok umursamıyor (korkusuz)
        "keep_coop": -20.0,    # Sağda beklemek büyük ceza
        "keep_agg": 0.0
    },
    "korkak": {
        "change_coop": 5.0,
        "change_agg": -100.0,  # En ufak risk durumunda bile asla şerit değiştirmez
        "keep_coop": 5.0,
        "keep_agg": 20.0       # Sağ şeritte kalmayı çok güvenli buluyor
    }
}

def niyet_tahmini(ego_arac, tehdit_arac):
    t_arac_v = getattr(tehdit_arac, 'v_x', None)
    if t_arac_v is not None:
        dv = t_arac_v - ego_arac.v_x
    else:
        return 0.0, 1.0

    # ZAMANSAL HAFIZA (Behavioral Memory)
    bonus_agg = 0.0
    speed_history = getattr(tehdit_arac, 'hiz_gecmisi', [])
    if len(speed_history) >= 5:
        ivme_trend = speed_history[-1] - speed_history[-5]
        if ivme_trend > 0.1:  # Eğer arkadaki araç aktif olarak hızlanıyorsa
            bonus_agg = 3.0   # agresiflik ihtimalini yapay olarak artır

    # Sigmoid (Lojistik) Fonksiyonu ile Psikoloji Tahmini
    p_agg = 1.0 / (1.0 + math.exp(-(dv - 3.0 + bonus_agg)))
    p_coop = 1.0 - p_agg
    return p_agg, p_coop

def serit_degisimi_onayla(ego_arac, grid, yon="sol", profil="normal"):
    on_key = 'sol_on' if yon == "sol" else 'sag_on'
    yan_key = 'sol_yan' if yon == "sol" else 'sag_yan'
    arka_key = 'sol_arka' if yon == "sol" else 'sag_arka'

    # Yanımız doluysa veya hedef şeridin önü tıkalıysa kesin ret
    if grid[yan_key] is not None:
        return False 

    # Geçmek istediğimiz şeridin önü kapalıysa mesafe ve hız kontrolü yap
    hedef_on = grid[on_key]
    if hedef_on is not None:
        mesafe_on = hedef_on.x - ego_arac.x
        if mesafe_on < 25.0 or (mesafe_on < 40.0 and hedef_on.v_x < ego_arac.v_x) or hedef_on.v_x < ego_arac.v_x - 4.0:
            return False 

    # Arkadan gelenin niyetine bak
    tehdit_arka = grid[arka_key]
    if tehdit_arka is None:
        return True

    mesafe_arka = ego_arac.x - tehdit_arka.x
    if mesafe_arka < 25.0:
        return False

    # Hız farkına bağlı Dinamik Güvenlik Sınırı
    dv = tehdit_arka.v_x - ego_arac.v_x
    dinamik_guvenlik_siniri = 25.0 + max(0.0, dv) * 4.0
    if mesafe_arka > dinamik_guvenlik_siniri:
        return True

    # Niyet Olasılıklarını Hesapla
    p_agg, p_coop = niyet_tahmini(ego_arac, tehdit_arka)

    matris = PROFILLER.get(profil, PROFILLER["normal"]).copy()
    
    # Çarpışma Süresi (TTC) Hesaplama: Mesafe / Bağıl Hız
    ttc = mesafe_arka / max(0.1, dv) if dv > 0 else float('inf')
    if ttc < 4.0:
        matris["change_agg"] = matris["change_agg"] * (4.0 / (ttc + 0.1))
    
    # Arkadaki oyuncu özelinde Beklenen Kazançlar (Expected Utility)
    eu_change_arka = (p_coop * matris["change_coop"]) + (p_agg * matris["change_agg"])
    eu_keep_arka = (p_coop * matris["keep_coop"]) + (p_agg * matris["keep_agg"])

    eu_change_on = 0.0
    if hedef_on is not None:
        mesafe_hedef_on = hedef_on.x - ego_arac.x
        if mesafe_hedef_on < 50.0:
            eu_change_on = -15.0 * (50.0 / mesafe_hedef_on)

    # Nihai Karar Dengesi
    eu_change = eu_change_arka + eu_change_on
    eu_keep = eu_keep_arka
    
    return eu_change > eu_keep