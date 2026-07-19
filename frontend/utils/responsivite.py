import flet as ft
import os

# Force le mode mobile sur Render
FORCE_MOBILE = os.environ.get("RENDER") is not None

def is_mobile(page: ft.Page) -> bool:
    """Détection mobile"""
    # FORCER mobile sur Render
    if FORCE_MOBILE:
        return True
    
    # Détection normale
    try:
        if page.width and page.width < 768:
            return True
    except:
        pass
    
    try:
        if page.window.width and page.window.width < 768:
            return True
    except:
        pass
    
    return False