import flet as ft
from config import PRIMARY, SECONDARY, BG_DARK, BG_CARD
from components.sidebar import build_sidebar, create_drawer
from components.header import build_header
from components.widgets import kpi_card, activity_row
from utils.responsivite import is_mobile
import services.api as api


def page_dashboard(page: ft.Page, state: dict, nav):
    page.overlay.clear()
    page.controls.clear()
    page.add(
        ft.Container(
            content=ft.Column(
                controls=[
                    ft.ProgressRing(color=PRIMARY, width=40, height=40),
                    ft.Text("Chargement du tableau de bord...", size=13, color=SECONDARY)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=12
            ),
            alignment=ft.Alignment(0, 0),
            expand=True,
            bgcolor=BG_DARK
        )
    )
    page.update()
    page.run_thread(_fetch, page, state, nav)


def _fetch(page, state, nav):
    try:
        res = api.get_carte_stats(state["token"])
        if res.status_code == 200:
            try:
                res_resa = api.get_reservations(state["token"])
                if res_resa.status_code == 200:
                    resa_data = res_resa.json()
                    state["resa_count"] = len([r for r in resa_data if r["statut"] == "EN_ATTENTE"])
            except Exception:
                pass
            _construire(page, state, nav, res.json())
        else:
            _erreur(page, state, nav, f"Erreur {res.status_code}")
    except Exception as ex:
        _erreur(page, state, nav, str(ex))


def _erreur(page, state, nav, msg):
    page.overlay.clear()
    page.controls.clear()
    page.add(
        ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.ERROR_OUTLINE, size=50, color=ft.Colors.RED_400),
                    ft.Text(msg, size=13, color=ft.Colors.RED_400),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=14
            ),
            alignment=ft.Alignment(0, 0),
            expand=True,
            bgcolor=BG_DARK
        )
    )
    page.update()


def _construire(page, state, nav, stats):
    mobile = is_mobile(page)
    taux = stats.get("taux_occupation", 0)
    
    # Drawer pour mobile
    drawer = create_drawer(page, state, nav)
    
    # Sidebar (retourne None sur mobile)
    sidebar = build_sidebar(page, state, "dashboard", nav)
    
    # Header
    header = build_header(page, state, nav, drawer)

    # KPI Cards
    kpi_cards = ft.Row(
        controls=[
            kpi_card("TOTAL CAVEAUX", stats["total"], "Capacité totale",
                     ft.Icons.GRID_VIEW_OUTLINED, "#4D7FFF"),
            kpi_card("DISPONIBLES", stats["disponibles"], "Libres",
                     ft.Icons.CHECK_CIRCLE_OUTLINED, "#00CC77"),
            kpi_card("RÉSERVÉS", stats["reserves"], "En attente",
                     ft.Icons.PENDING_OUTLINED, "#FF9922"),
            kpi_card("TAUX OCCUPATION", f"{taux}%", f"{stats['occupes']} occupés",
                     ft.Icons.DONUT_LARGE_OUTLINED, SECONDARY),
        ],
        spacing=8 if mobile else 12,
        wrap=True,
        run_spacing=8,
    )

    # Carte du cimetière
    carte_container = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text("Carte du cimetière", size=13,
                                weight=ft.FontWeight.W_500, color=ft.Colors.WHITE),
                        ft.TextButton(
                            content=ft.Text("Plein écran →", size=11, color=PRIMARY),
                            on_click=lambda e: nav("carte")
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Row(
                    controls=[
                        ft.Text("Taux d'occupation", size=11, color=SECONDARY),
                        ft.Text(f"{taux}%", size=11, color=ft.Colors.WHITE)
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.ProgressBar(
                    value=taux / 100,
                    bgcolor=SECONDARY + "20",
                    color="#00CC77" if taux < 70 else "#FF9922" if taux < 90 else "#FF4444",
                    border_radius=4
                ),
                ft.Container(height=8),
                ft.Row(
                    controls=[
                        ft.Row([ft.Container(width=8, height=8, bgcolor="#00CC77", border_radius=2),
                                ft.Text("Disponible", size=10, color=SECONDARY)], spacing=4),
                        ft.Row([ft.Container(width=8, height=8, bgcolor="#FF4444", border_radius=2),
                                ft.Text("Occupé", size=10, color=SECONDARY)], spacing=4),
                        ft.Row([ft.Container(width=8, height=8, bgcolor="#FF9922", border_radius=2),
                                ft.Text("Réservé", size=10, color=SECONDARY)], spacing=4),
                    ],
                    spacing=12,
                    wrap=True if mobile else False,
                ),
            ],
            spacing=10
        ),
        bgcolor=BG_CARD, border_radius=12, padding=16,
        border=ft.Border.all(1, SECONDARY + "25"),
        expand=True,
    )

    # Activité récente
    activite_container = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text("Activité récente", size=13,
                                weight=ft.FontWeight.W_500, color=ft.Colors.WHITE),
                        ft.TextButton(
                            content=ft.Text("Tout voir →", size=11, color=PRIMARY),
                            on_click=lambda e: nav("reservations")
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                activity_row(ft.Icons.ASSIGNMENT_TURNED_IN_OUTLINED, "#4D7FFF",
                             "Réservation validée", "Secrétariat"),
                activity_row(ft.Icons.PAYMENT_OUTLINED, "#00CC77",
                             "Paiement MTN enregistré", "Facturation"),
                activity_row(ft.Icons.ARTICLE_OUTLINED, "#FF9922",
                             "Concession renouvelée", "Zone A"),
                activity_row(ft.Icons.PERSON_ADD_OUTLINED, "#4D7FFF",
                             "Nouveau client enregistré", "Portail citoyen"),
            ],
            spacing=0
        ),
        bgcolor=BG_CARD, border_radius=12, padding=16,
        border=ft.Border.all(1, SECONDARY + "25"),
        width=None if mobile else 300,
        expand=True if mobile else False,
    )

    # Row pour carte + activité
    carte_activite_row = ft.Row(
        controls=[carte_container, activite_container],
        spacing=12,
        wrap=True,
        run_spacing=12,
    )

    # Main content
    main_content = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Tableau de bord", size=18 if mobile else 20, 
                       weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Text("Vue d'ensemble — Cimetière Municipal de Pointe-Noire", 
                       size=11 if mobile else 12, color=SECONDARY),
                kpi_cards,
                carte_activite_row,
            ],
            spacing=12 if mobile else 16,
            expand=True
        ),
        padding=12 if mobile else 24,
        expand=True
    )

    # Layout final
    page.overlay.clear()
    page.controls.clear()
    
    if mobile:
        page.add(
            ft.Column(
                controls=[header, main_content],
                spacing=0,
                expand=True
            )
        )
    else:
        page.add(
            ft.Row(
                controls=[
                    sidebar,
                    ft.Column(controls=[header, main_content], spacing=0, expand=True)
                ],
                spacing=0,
                expand=True
            )
        )
    page.update()