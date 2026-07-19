import flet as ft
import os

def is_mobile(page: ft.Page) -> bool:
    """Détection mobile simple et fiable"""
    # Si on est sur Render, on suppose mobile (car WebView)
    if os.environ.get("RENDER"):
        return True
    
    # Vérifier la largeur de la page
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