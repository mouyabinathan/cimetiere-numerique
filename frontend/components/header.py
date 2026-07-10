import flet as ft
from config import PRIMARY, SECONDARY, BG_CARD


def build_header(page: ft.Page, state: dict):
    """
    En-tête responsive avec :
    - Bouton hamburger (mobile) pour ouvrir le drawer
    - Barre de recherche (cachée sur très petit écran)
    - Notifications et profil utilisateur
    """
    is_mobile = state.get("is_mobile", False)
    
    user_initials = "?"
    if state and state.get("user_nom"):
        parts = state["user_nom"].split()[:2]
        user_initials = "".join([p[0].upper() for p in parts])

    notif_count = state.get("notif_count", 0) if state else 0

    # ✅ Contrôles du header
    controls = []

    # ✅ Bouton hamburger (visible uniquement sur mobile)
    if is_mobile:
        controls.append(
            ft.IconButton(
                icon=ft.Icons.MENU,
                icon_size=24,
                icon_color=ft.Colors.WHITE,
                on_click=lambda e: page.drawer.open_toggle() if page.drawer else None,
                tooltip="Menu",
                style=ft.ButtonStyle(
                    overlay_color=ft.Colors.TRANSPARENT,
                )
            )
        )

    # ✅ Barre de recherche (réduite ou masquée sur mobile)
    if is_mobile:
        # Sur mobile : champ de recherche plus petit
        search_field = ft.TextField(
            hint_text="Rechercher...",
            prefix_icon=ft.Icons.SEARCH,
            border=ft.InputBorder.NONE,
            color=ft.Colors.WHITE,
            hint_style=ft.TextStyle(color=SECONDARY + "80", size=12),
            cursor_color=PRIMARY,
            bgcolor=ft.Colors.TRANSPARENT,
            height=34,
            text_size=12,
            expand=True
        )
    else:
        # Sur desktop : champ de recherche complet
        search_field = ft.TextField(
            hint_text="Rechercher un caveau, défunt... (Entrée pour valider)",
            prefix_icon=ft.Icons.SEARCH,
            border=ft.InputBorder.NONE,
            color=ft.Colors.WHITE,
            hint_style=ft.TextStyle(color=SECONDARY + "80", size=13),
            cursor_color=PRIMARY,
            bgcolor=ft.Colors.TRANSPARENT,
            height=38,
            text_size=13,
            expand=True
        )

    controls.append(
        ft.Container(
            content=search_field,
            expand=True,
            bgcolor=BG_CARD,
            border_radius=8,
            padding=ft.Padding.only(left=4, right=14, top=0, bottom=0),
            border=ft.Border.all(1, SECONDARY + "30")
        )
    )

    # ✅ Notifications
    controls.append(
        ft.Container(
            content=ft.Stack(
                controls=[
                    ft.Icon(ft.Icons.NOTIFICATIONS_OUTLINED, size=20, color=SECONDARY),
                    *(
                        [ft.Container(
                            content=ft.Text(str(notif_count), size=8, color=ft.Colors.WHITE),
                            width=16, height=16,
                            bgcolor=PRIMARY,
                            border_radius=8,
                            alignment=ft.Alignment(0, 0),
                            left=12, top=0
                        )]
                        if notif_count > 0 else
                        [ft.Container(width=8, height=8, bgcolor=PRIMARY, border_radius=4, left=12, top=0)]
                    )
                ],
                width=30, height=30
            ),
            width=40, height=40, bgcolor=BG_CARD, border_radius=8,
            alignment=ft.Alignment(0, 0),
            border=ft.Border.all(1, SECONDARY + "30"),
            tooltip="Notifications",
        )
    )

    # ✅ Profil utilisateur
    controls.append(
        ft.Container(
            content=ft.Text(user_initials, size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            width=36, height=36, bgcolor=PRIMARY, border_radius=18,
            alignment=ft.Alignment(0, 0)
        )
    )

    # ✅ Ajustement du padding selon le mode
    padding = ft.Padding.symmetric(horizontal=12 if is_mobile else 24, vertical=8 if is_mobile else 12)

    return ft.Container(
        content=ft.Row(
            controls=controls,
            spacing=8 if is_mobile else 12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        ),
        bgcolor=BG_CARD,
        padding=padding,
        border=ft.Border.only(bottom=ft.BorderSide(1, SECONDARY + "25")),
        height=56 if is_mobile else 68
    )