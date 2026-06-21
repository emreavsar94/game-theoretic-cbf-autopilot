class CevreSensoru:
    def __init__(self, gorus_mesafesi=120.0):
        self.gorus_mesafesi = gorus_mesafesi

    def cevreyi_tara(self, ego, global_trafik):
        grid = {
            'sol_on': None,   'orta_on': None,   'sag_on': None,
            'sol_yan': None,  'orta_yan': ego,   'sag_yan': None, 
            'sol_arka': None, 'orta_arka': None, 'sag_arka': None
        }

        min_mesafeler = {k: float('inf') for k in grid.keys() if k != 'orta_yan'}

        for arac in global_trafik:
            if arac.id == ego.id: 
                continue

            dx = arac.x - ego.x
            dy = arac.y - ego.y 
            
            mesafe = (dx**2 + dy**2)**0.5
            if mesafe > self.gorus_mesafesi:
                continue

            # Yanal (Şerit) sınıflandırma
            if dy >= 2.0: sutun = 'sol'
            elif dy <= -2.0: sutun = 'sag'
            else: sutun = 'orta'

            # Boylamsal sınıflandırma
            if dx > 8.0: satir = 'on'
            elif dx < -8.0: satir = 'arka'
            else: satir = 'yan' 

            bolge_adi = f"{sutun}_{satir}"

            if bolge_adi == 'orta_yan':
                continue

            if abs(dx) < min_mesafeler[bolge_adi]:
                min_mesafeler[bolge_adi] = abs(dx)
                grid[bolge_adi] = arac

        return grid