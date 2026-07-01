import flet as ft
from config import PRIMARY, SECONDARY, BG_DARK, BG_CARD


def btn(label, on_click, color=PRIMARY, width=380, icon=None, disabled=False):
    controls = []
    if icon:
        controls.append(ft.Icon(icon, color=ft.Colors.WHITE, size=16))
    controls.append(ft.Text(label, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, size=14))
    return ft.Container(
        content=ft.Row(controls, alignment=ft.MainAxisAlignment.CENTER, spacing=8),
        width=width,
        height=48,
        bgcolor=color if not disabled else SECONDARY + "50",
        border_radius=10,
        alignment=ft.Alignment(0, 0),
        on_click=None if disabled else on_click,
        ink=not disabled,
        data="btn"
    )


def card_wrapper(content_col, width=480):
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(
                    content=content_col,
                    bgcolor=BG_CARD,
                    border_radius=16,
                    padding=40,
                    width=width,
                    border=ft.Border.all(1, SECONDARY + "40"),
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER
        ),
        alignment=ft.Alignment(0, 0),
        expand=True,
        bgcolor=BG_DARK
    )


def kpi_card(label, value, sub, icon, color):
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text(label, size=10, color=SECONDARY, weight=ft.FontWeight.W_500),
                        ft.Icon(icon, size=16, color=color + "80")
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Text(str(value), size=28, weight=ft.FontWeight.BOLD, color=color),
                ft.Text(sub, size=11, color=SECONDARY),
            ],
            spacing=6
        ),
        bgcolor=BG_CARD,
        border_radius=12,
        padding=16,
        border=ft.Border.all(1, SECONDARY + "25"),
        expand=True
    )


def kpi_mini(label, value, color):
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(str(value), size=22, weight=ft.FontWeight.BOLD, color=color),
                ft.Text(label, size=10, color=SECONDARY)
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=2
        ),
        bgcolor=BG_CARD,
        border_radius=10,
        padding=ft.Padding.symmetric(horizontal=16, vertical=12),
        border=ft.Border.all(1, color + "35"),
        expand=True
    )


def activity_row(icon, color, main_txt, sub_txt):
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(
                    content=ft.Icon(icon, size=14, color=color),
                    width=28, height=28,
                    bgcolor=color + "20",
                    border_radius=8,
                    alignment=ft.Alignment(0, 0)
                ),
                ft.Column(
                    controls=[
                        ft.Text(main_txt, size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                        ft.Text(sub_txt, size=10, color=SECONDARY)
                    ],
                    spacing=2,
                    expand=True
                )
            ],
            spacing=10
        ),
        padding=ft.Padding.only(bottom=10, top=10),
        border=ft.Border.only(bottom=ft.BorderSide(1, SECONDARY + "15"))
    )


def statut_badge(label, color):
    return ft.Container(
        content=ft.Text(label, size=10, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
        bgcolor=color,
        border_radius=6,
        padding=ft.Padding.symmetric(horizontal=8, vertical=2),
    )


def show_dialog(page, content_col, width=420):
    dlg = ft.AlertDialog(
        modal=True,
        bgcolor=BG_CARD,
        content=ft.Container(content=content_col, width=width),
        shape=ft.RoundedRectangleBorder(radius=14),
    )
    page.overlay.append(dlg)
    dlg.open = True
    page.update()
    return dlg


def close_dialog(page, dlg):
    dlg.open = False
    page.update()


def erreur_page(page, msg, on_retry, sidebar):
    from components.header import build_header
    page.overlay.clear()
    page.controls.clear()
    page.add(
        ft.Row(
            controls=[
                sidebar,
                ft.Column(
                    controls=[
                        build_header(page, None),
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Icon(ft.Icons.ERROR_OUTLINE, size=50, color=ft.Colors.RED_400),
                                    ft.Text(msg, size=13, color=ft.Colors.RED_400),
                                    btn("Réessayer", on_retry, width=200)
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=14
                            ),
                            alignment=ft.Alignment(0, 0),
                            expand=True
                        )
                    ],
                    spacing=0,
                    expand=True
                )
            ],
            spacing=0,
            expand=True
        )
    )
    page.update()
