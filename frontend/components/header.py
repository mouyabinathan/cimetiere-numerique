import flet as ft
from config import PRIMARY, SECONDARY, BG_CARD
from utils.responsivite import is_mobile

def build_header(page: ft.Page, state: dict, nav_func, drawer=None):
    mobile = is_mobile(page)
    
    user_initials = "?"
    if state and state.get("user_nom"):
        parts = state["user_nom"].split()[:2]
        user_initials = "".join([p[0].upper() for p in parts])

    notif_count = state.get("notif_count", 0) if state else 0

    controls = []
    
    if mobile and drawer:
        controls.append(
            ft.IconButton(
                icon=ft.icons.MENU,
                icon_color=ft.Colors.WHITE,
                icon_size=24,
                on_click=lambda e: page.show_drawer(),
                tooltip="Ouvrir le menu",
            )
        )
    
    controls.append(
        ft.Container(
            content=ft.TextField(
                hint_text="Rechercher..." if mobile else "Rechercher un caveau, défunt...",
                prefix_icon=ft.Icons.SEARCH,
                border=ft.InputBorder.NONE,
                color=ft.Colors.WHITE,
                hint_style=ft.TextStyle(color=SECONDARY + "80", size=11 if mobile else 13),
                cursor_color=PRIMARY,
                bgcolor=ft.Colors.TRANSPARENT,
                height=38,
                text_size=11 if mobile else 13,
            ),
            expand=True if not mobile else False,
            width=None if not mobile else 100,
            bgcolor=BG_CARD,
            border_radius=8,
            padding=ft.Padding.only(left=4, right=14, top=0, bottom=0),
            border=ft.Border.all(1, SECONDARY + "30")
        )
    )
    
    controls.append(
        ft.Container(
            content=ft.Stack(
                controls=[
                    ft.Icon(ft.Icons.NOTIFICATIONS_OUTLINED, size=18 if mobile else 20, color=SECONDARY),
                    *(
                        [ft.Container(
                            content=ft.Text(str(notif_count), size=7 if mobile else 8, color=ft.Colors.WHITE),
                            width=14 if mobile else 16, height=14 if mobile else 16,
                            bgcolor=PRIMARY,
                            border_radius=8,
                            alignment=ft.Alignment(0, 0),
                            left=10 if mobile else 12, top=0
                        )]
                        if notif_count > 0 else
                        [ft.Container(width=6 if mobile else 8, height=6 if mobile else 8, 
                                      bgcolor=PRIMARY, border_radius=4, left=10 if mobile else 12, top=0)]
                    )
                ],
                width=26 if mobile else 30, height=26 if mobile else 30
            ),
            width=34 if mobile else 40, height=34 if mobile else 40, 
            bgcolor=BG_CARD, border_radius=8,
            alignment=ft.Alignment(0, 0),
            border=ft.Border.all(1, SECONDARY + "30"),
            tooltip="Notifications",
        )
    )
    
    controls.append(
        ft.Container(
            content=ft.Text(user_initials, size=11 if mobile else 12, 
                           weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            width=32 if mobile else 36, height=32 if mobile else 36, 
            bgcolor=PRIMARY, border_radius=18,
            alignment=ft.Alignment(0, 0)
        )
    )

    return ft.Container(
        content=ft.Row(
            controls=controls,
            spacing=6 if mobile else 12,
        ),
        bgcolor=BG_CARD,
        padding=ft.Padding.symmetric(horizontal=10 if mobile else 24, vertical=10 if mobile else 12),
        border=ft.Border.only(bottom=ft.BorderSide(1, SECONDARY + "25"))
    )