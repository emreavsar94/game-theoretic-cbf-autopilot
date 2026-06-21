import numpy as np

class Arac:
    def __init__(self, id_no, x_init, y_init, v_x_init):
        self.id = id_no
        self.x = x_init
        self.y = y_init
        self.v_x = v_x_init 
        self.theta = 0.0    
        self.L = 2.8 # Dingil mesafesi
        self.kilit_sayaci = 0.0
        self.hiz_gecmisi = []
        
    def guncelle(self, a_x, direksiyon, dt):
        # Kinematik hareket denklemleri
        self.x += self.v_x * np.cos(self.theta) * dt
        self.y += self.v_x * np.sin(self.theta) * dt
        self.theta += (self.v_x / self.L) * np.tan(direksiyon) * dt
        
        # Hız güncellemesi
        self.v_x = max(0.0, self.v_x + a_x * dt)
        
        # Fiziksel sınırlar
        self.theta = np.clip(self.theta, -0.2, 0.2) 
        self.y = np.clip(self.y, -0.5, 4.5)         

        if self.kilit_sayaci > 0: 
            self.kilit_sayaci -= dt
        
        self.hiz_gecmisi.append(self.v_x)
        if len(self.hiz_gecmisi) > 20: self.hiz_gecmisi.pop(0)