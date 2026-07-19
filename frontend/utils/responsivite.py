import flet as ft
import os

def is_mobile(page: ft.Page) -> bool:
    """Détecte si l'écran est mobile avec plusieurs méthodes"""
    try:
        # Méthode 1: page.width (le plus fiable après chargement)
        if hasattr(page, 'width') and page.width:
            if page.width < 768:
                return True
    except:
        pass
    
    try:
        # Méthode 2: page.window.width
        if hasattr(page, 'window') and hasattr(page.window, 'width'):
            if page.window.width and page.window.width < 768:
                return True
    except:
        pass
    
    # Méthode 3: Environnement Render (par défaut mobile)
    if os.environ.get("RENDER"):
        return True
    
    return False

def get_responsive_value(page: ft.Page, mobile_value, desktop_value):
    """Retourne la valeur adaptée selon le type d'écran"""
    return mobile_value if is_mobile(page) else desktop_value