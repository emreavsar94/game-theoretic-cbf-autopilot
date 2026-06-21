import cvxpy as cp

def guvenlik_kalkani(ego_arac, trafik_listesi, a_x_nominal):
    u = cp.Variable(1) # Optimize edilecek yeni ivme
    slack = cp.Variable(1, nonneg=True)
    gamma = 1.5       # Kalkanın sertlik katsayısı (Büyüdükçe araç daha sert tepki verir)
    
    # Temel uzunluk 10 metre + Hızımızın her m/s'si için 0.8 metre ek güvenlik mesafesi
    a_ell = 10.0 + (0.8 * ego_arac.v_x) 
    b_ell = 2.8
    
    # Aracın fiziksel motor sınırları
    constraints = [u <= 4.0, u >= -8.0] 
    
    for arac in trafik_listesi:
        if arac.id == ego_arac.id: continue # Kendini yoksay
        
        dx = arac.x - ego_arac.x
        dy = arac.y - ego_arac.y
        dv = arac.v_x - ego_arac.v_x
        
        # Eğer önümüzde ve tehlikeli bölgedeyse CBF denklemini constraints'e ekle
        if dx > 0 and abs(dy) < 3.2:
            h = (dx / a_ell)**2 + (dy / b_ell)**2 - 1
            h_dot_v = (2 * dx * dv) / (a_ell**2)

            # CBF Kısıtı
            lhs = (2 * dx * dv) + gamma * h * (a_ell**2)
            rhs = (2 * dx * u) - slack[0]
            constraints.append(lhs >= rhs)
            #constraints.append(h_dot_v + gamma * h >= (2 * dx * u) / (a_ell**2) - slack[0])
            
    # Optimizasyon Problemi: Nominal karara en yakın, ama güvenli olan ivmeyi bul
    prob = cp.Problem(cp.Minimize(cp.square(u - a_x_nominal) + 1000.0 * slack[0]), constraints)
    
    try:
        prob.solve(solver=cp.OSQP, warm_start=True, max_iter=30000, eps_abs=1e-2, eps_rel=1e-2)
        return u.value[0] if u.value is not None else a_x_nominal
    except:
        return a_x_nominal