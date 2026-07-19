import flet as ft
import os

def is_mobile(page: ft.Page) -> bool:
    """Détecte si l'écran est mobile avec plusieurs méthodes de fallback."""
    
    # Méthode 1: window.width
    try:
        if hasattr(page, 'window') and hasattr(page.window, 'width'):
            if page.window.width and page.window.width < 768:
                return True
    except:
        pass
    
    # Méthode 2: page.width
    try:
        if page.width and page.width < 768:
            return True
    except:
        pass
    
    # Méthode 3: User-Agent (pour Render/WebView)
    try:
        if hasattr(page, 'web') and page.web:
            return True
    except:
        pass
    
    # Méthode 4: Environnement Render
    if os.environ.get("RENDER"):
        return True
    
    # Par défaut: desktop
    return False

def get_responsive_padding(page: ft.Page) -> int:
    """Retourne le padding adapté."""
    return 12 if is_mobile(page) else 24

def get_responsive_font_size(page: ft.Page, base_size: int) -> int:
    """Retourne la taille de police adaptée."""
    return base_size - 2 if is_mobile(page) else base_size