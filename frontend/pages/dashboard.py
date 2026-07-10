import flet as ft
from config import PRIMARY, SECONDARY, BG_CARD, BG_DARK
from components.header import build_header  # Ajout de components.
from components.sidebar import create_drawer, get_sidebar_menu  # Ajout de components.

def page_dashboard(page: ft.Page, state: dict, nav):
    # Détection mobile
    is_mobile = page.window.width < 768
    
    # Nettoyer la page
    page.controls.clear()
    
    # Initialiser user_initials
    if "user_initials" not in state or not state["user_initials"]:
        if state.get("user_nom"):
            parts = state["user_nom"].split()[:2]
            state["user_initials"] = "".join([p[0].upper() for p in parts])
        else:
            state["user_initials"] = "?"
    
    # Créer drawer et menu
    drawer = create_drawer(page, state, nav, is_mobile)
    sidebar_menu = get_sidebar_menu(page, state, nav, is_mobile)
    
    # Header
    header = build_header(page, state, nav, is_mobile, drawer)
    
    # ===== CONTENU PRINCIPAL =====
    main_content = ft.Column([
        ft.Text("Tableau de bord", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
        ft.Text("Bienvenue dans votre espace de gestion", color=SECONDARY),
        ft.Container(
            content=ft.Row([
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("Réservations", size=14, color=SECONDARY),
                            ft.Text("1,234", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ], spacing=4),
                        padding=20,
                        width=150,
                    ),
                ),
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("Concessions", size=14, color=SECONDARY),
                            ft.Text("567", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ], spacing=4),
                        padding=20,
                        width=150,
                    ),
                ),
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("Factures", size=14, color=SECONDARY),
                            ft.Text("890", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ], spacing=4),
                        padding=20,
                        width=150,
                    ),
                ),
            ], spacing=12, wrap=True),
            padding=10,
        ),
        ft.Text("Activité récente", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
        ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("• Réservation #1234 - Nouvelle réservation par Jean Dupont", color=SECONDARY),
                    ft.Text("• Concession #567 - Paiement effectué", color=SECONDARY),
                    ft.Text("• Exhumation #890 - Demande approuvée", color=SECONDARY),
                ], spacing=8),
                padding=16,
                width=400,
            ),
        ),
    ], spacing=16, expand=True)
    
    # ===== LAYOUT FINAL =====
    if is_mobile:
        page.add(
            ft.Column([
                header,
                ft.Container(
                    content=main_content,
                    padding=16,
                    expand=True,
                ),
            ], expand=True)
        )
    else:
        page.add(
            ft.Column([
                header,
                ft.Row([
                    sidebar_menu,
                    ft.VerticalDivider(width=1, color=SECONDARY + "30"),
                    ft.Container(
                        content=main_content,
                        padding=16,
                        expand=True,
                    ),
                ], expand=True),
            ], expand=True)
        )
    
    page.update()