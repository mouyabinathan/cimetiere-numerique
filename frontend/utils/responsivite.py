# utils/responsivite.py
import flet as ft
import os

# 🔥 FORCER le mode mobile TOUJOURS sur Render
FORCE_MOBILE = True  # 👈 Mettre à True pour forcer

def is_mobile(page: ft.Page) -> bool:
    # 1️⃣ FORCER toujours
    if FORCE_MOBILE:
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