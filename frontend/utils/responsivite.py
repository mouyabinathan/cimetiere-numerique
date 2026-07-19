# utils/responsivite.py - Ajoute ceci en haut
import os

# 🔥 FORCER mobile sur Render
if os.environ.get("RENDER"):
    print("📱 MODE MOBILE FORCÉ SUR RENDER")  # Pour vérifier dans les logs

def is_mobile(page: ft.Page) -> bool:
    # 1️⃣ FORCER sur Render
    if os.environ.get("RENDER"):
        return True
    
    # 2️⃣ window.width
    try:
        if page.window.width and page.window.width < 768:
            return True
    except:
        pass
    
    # 3️⃣ page.width
    try:
        if page.width and page.width < 768:
            return True
    except:
        pass
    
    return False