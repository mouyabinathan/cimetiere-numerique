import flet as ft
import time
import sys
import os

# Ajouter le dossier frontend au path
sys.path.insert(0, os.path.dirname(__file__))

from config import PRIMARY, SECONDARY, BG_DARK
from pages.auth import page_splash, page_login, page_register
from pages.dashboard import page_dashboard
from pages.cartographie import page_cartographie
from pages.reservations import page_reservations
from pages.concessions import page_concessions
from pages.facturation import page_facturation
from pages.exhumations import page_exhumations
from pages.reporting import page_reporting
from pages.parametres import page_parametres
from pages.users import page_users


def main(page: ft.Page):
    page.title = "CimétièrePRO — Pointe-Noire"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.bgcolor = BG_DARK
    
    # Dimension initiale (sera ajustée automatiquement)
    page.window.width = 1280
    page.window.height = 800
    page.window.min_width = 320  # Empêcher un trop petit écran
    page.window.min_height = 480

    # ---- État global partagé ----
    state = {
        "token":      None,
        "role":       None,
        "user_nom":   None,
        "user_email": None,
        "resa_count": 0,
        "notif_count": 0,
    }

    # ---- Gestion du redimensionnement ----
    def on_resize(e):
        """Recharge la page courante si besoin pour adapter le layout."""
        # On ne recharge que si la page actuelle est une page avec menu
        # Pour éviter les rechargements intempestifs sur les pages d'auth
        if state.get("token") and page.controls:
            # Récupérer la page actuelle depuis la navigation
            # On pourrait stocker la route actuelle dans state
            pass
    
    page.on_resize = on_resize

    # ---- Navigation centralisée ----
    def nav(key):
        routes = {
            "dashboard":   lambda: page_dashboard(page, state, nav),
            "carte":       lambda: page_cartographie(page, state, nav),
            "reservations":lambda: page_reservations(page, state, nav),
            "concessions": lambda: page_concessions(page, state, nav),
            "facturation": lambda: page_facturation(page, state, nav),
            "exhumations": lambda: page_exhumations(page, state, nav),
            "reporting":   lambda: page_reporting(page, state, nav),
            "parametres":  lambda: page_parametres(page, state, nav),
            "users":       lambda: page_users(page, state, nav),
            "logout":      do_logout,
        }
        if key in routes:
            routes[key]()

    def on_login_success(data):
        state["token"]      = data["token"]
        state["role"]       = data["role"]
        state["user_nom"]   = data.get("nom", data.get("email", "Utilisateur"))
        state["user_email"] = data.get("email", "")
        nav("dashboard")

    def do_logout():
        state["token"]      = None
        state["role"]       = None
        state["user_nom"]   = None
        state["user_email"] = None
        state["resa_count"] = 0
        page_login(page, on_login_success, lambda: page_register(page, lambda: page_login(page, on_login_success, lambda: page_register(page, None))))

    def on_register_click():
        page_register(page, lambda: page_login(page, on_login_success, on_register_click))

    # ---- Boot ----
    def boot():
        page_login(page, on_login_success, on_register_click)

    page_splash(page)
    boot()

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    ft.run(target=main, port=port, view=None, host="0.0.0.0")