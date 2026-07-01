import flet as ft
from config import PRIMARY, SECONDARY, DARK


def nav_item(icon, label, active=False, badge=None, on_click=None):
    controls = [
        ft.Icon(icon, size=18, color=ft.Colors.WHITE if active else SECONDARY),
        ft.Text(label, size=13, color=ft.Colors.WHITE if active else SECONDARY,
                weight=ft.FontWeight.W_500 if active else ft.FontWeight.W_400)
    ]
    if badge:
        controls.append(
            ft.Container(
                content=ft.Text(str(badge), size=10, color=ft.Colors.WHITE),
                bgcolor=PRIMARY,
                border_radius=10,
                padding=ft.Padding.symmetric(horizontal=6, vertical=1)
            )
        )
    return ft.Container(
        content=ft.Row(controls, spacing=10),
        padding=ft.Padding.symmetric(horizontal=20, vertical=10),
        bgcolor=PRIMARY + "30" if active else ft.Colors.TRANSPARENT,
        border=ft.Border.only(left=ft.BorderSide(2, PRIMARY)) if active else None,
        ink=True,
        on_click=on_click,
        border_radius=ft.BorderRadius.only(top_right=8, bottom_right=8)
    )


def build_sidebar(page, state: dict, active_key: str, nav):
    """
    state : {"token": ..., "role": ..., "user": ..., "resa_count": ...}
    nav   : dict de callbacks {"dashboard": fn, "carte": fn, ...}
    """
    def goto(key):
        def handler(e):
            nav(key)
        return handler

    user_name  = state.get("user_nom", "—")
    user_initials = "".join([p[0].upper() for p in user_name.split()[:2]]) if user_name != "—" else "?"
    user_role  = state.get("role", "")
    resa_count = state.get("resa_count", 0)

    role = state.get("role", "CLIENT")
    is_admin        = role == "ADMIN"
    is_staff        = role in ("ADMIN", "SECRETARIAT", "AGENT")
    is_client       = role == "CLIENT"

    # Construction des nav items selon le rôle
    nav_controls = [
        ft.Container(
            content=ft.Text("PRINCIPAL", size=9, color=SECONDARY + "80", weight=ft.FontWeight.BOLD),
            padding=ft.Padding.only(left=20, top=16, bottom=6)
        ),
        nav_item(ft.Icons.DASHBOARD_OUTLINED, "Tableau de bord",
                 active=(active_key == "dashboard"), on_click=goto("dashboard")),
        nav_item(ft.Icons.MAP_OUTLINED, "Cartographie",
                 active=(active_key == "carte"), on_click=goto("carte")),
        nav_item(ft.Icons.PEOPLE_OUTLINED, "Réservations",
                 badge=resa_count if resa_count > 0 and is_staff else None,
                 active=(active_key == "reservations"), on_click=goto("reservations")),
    ]

    if is_staff:
        nav_controls += [
            ft.Container(
                content=ft.Text("GESTION", size=9, color=SECONDARY + "80", weight=ft.FontWeight.BOLD),
                padding=ft.Padding.only(left=20, top=16, bottom=6)
            ),
            nav_item(ft.Icons.DESCRIPTION_OUTLINED, "Concessions",
                     active=(active_key == "concessions"), on_click=goto("concessions")),
            nav_item(ft.Icons.RECEIPT_OUTLINED, "Facturation",
                     active=(active_key == "facturation"), on_click=goto("facturation")),
            nav_item(ft.Icons.SWAP_HORIZ_OUTLINED, "Exhumations",
                     active=(active_key == "exhumations"), on_click=goto("exhumations")),
            nav_item(ft.Icons.BAR_CHART_OUTLINED, "Reporting",
                     active=(active_key == "reporting"), on_click=goto("reporting")),
        ]

    if is_admin:
        nav_controls += [
            ft.Container(
                content=ft.Text("ADMIN", size=9, color=SECONDARY + "80", weight=ft.FontWeight.BOLD),
                padding=ft.Padding.only(left=20, top=16, bottom=6)
            ),
            nav_item(ft.Icons.MANAGE_ACCOUNTS_OUTLINED, "Utilisateurs",
                     active=(active_key == "users"), on_click=goto("users")),
            nav_item(ft.Icons.SETTINGS_OUTLINED, "Paramètres",
                     active=(active_key == "parametres"), on_click=goto("parametres")),
        ]

    return ft.Container(
        content=ft.Column(
            controls=[
                # Logo
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.ACCOUNT_BALANCE, size=24, color=PRIMARY),
                            ft.Column(
                                controls=[
                                    ft.Text("CimétièrePRO", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                    ft.Text("Pointe-Noire", size=10, color=SECONDARY)
                                ],
                                spacing=0
                            )
                        ],
                        spacing=10
                    ),
                    padding=ft.Padding.only(left=20, right=20, top=20, bottom=16),
                    border=ft.Border.only(bottom=ft.BorderSide(1, SECONDARY + "25"))
                ),
                # Nav items filtrés selon le rôle
                ft.Container(
                    content=ft.Column(
                        controls=nav_controls,
                        spacing=2,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                    expand=True
                ),
                # User footer
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Text(user_initials, size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                width=34, height=34, bgcolor=PRIMARY, border_radius=17,
                                alignment=ft.Alignment(0, 0)
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text(user_name, size=12, weight=ft.FontWeight.W_500, color=ft.Colors.WHITE),
                                    ft.Text(user_role, size=10, color=SECONDARY)
                                ],
                                spacing=1,
                                expand=True
                            ),
                            ft.IconButton(
                                icon=ft.Icons.LOGOUT,
                                icon_size=16,
                                icon_color=SECONDARY,
                                tooltip="Déconnexion",
                                on_click=lambda e: nav("logout")
                            )
                        ],
                        spacing=10
                    ),
                    padding=ft.Padding.all(16),
                    border=ft.Border.only(top=ft.BorderSide(1, SECONDARY + "25"))
                )
            ],
            spacing=0
        ),
        bgcolor=DARK,
        width=220,
    )
