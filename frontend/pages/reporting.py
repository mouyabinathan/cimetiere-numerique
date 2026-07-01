import flet as ft
import os, tempfile, subprocess
from config import PRIMARY, SECONDARY, BG_DARK, BG_CARD
from components.sidebar import build_sidebar
from components.header import build_header
from components.widgets import btn, kpi_mini
import services.api as api


def page_reporting(page: ft.Page, state: dict, nav):
    page.overlay.clear()
    page.controls.clear()
    page.add(
        ft.Row(
            controls=[
                build_sidebar(page, state, "reporting", nav),
                ft.Column(
                    controls=[
                        build_header(page, state),
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.ProgressRing(color=PRIMARY, width=40, height=40),
                                    ft.Text("Chargement du reporting...", size=13, color=SECONDARY)
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=12
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
    page.run_thread(_fetch, page, state, nav)


def _fetch(page, state, nav):
    try:
        res_dash = api.get_reporting_dashboard(state["token"])
        if res_dash.status_code in (401, 403):
            _erreur(page, state, nav, "Accès refusé — droits Admin requis")
            return
        if res_dash.status_code != 200:
            _erreur(page, state, nav, f"Erreur serveur : {res_dash.status_code}")
            return
        try:
            res_blocs = api.get_stats_par_bloc(state["token"])
            blocs_data = res_blocs.json() if res_blocs.status_code == 200 else []
        except Exception:
            blocs_data = []
        _construire(page, state, nav, res_dash.json(), blocs_data)
    except Exception as ex:
        _erreur(page, state, nav, str(ex))


def _erreur(page, state, nav, msg):
    page.overlay.clear()
    page.controls.clear()
    page.add(
        ft.Row(
            controls=[
                build_sidebar(page, state, "reporting", nav),
                ft.Column(
                    controls=[
                        build_header(page, state),
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Icon(ft.Icons.ERROR_OUTLINE, size=50, color=ft.Colors.RED_400),
                                    ft.Text(msg, size=13, color=ft.Colors.RED_400),
                                    btn("Réessayer", lambda e: page_reporting(page, state, nav), width=200)
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


def _construire(page, state, nav, dash, blocs):
    caveaux  = dash.get("caveaux", {})
    resa     = dash.get("reservations", {})
    finances = dash.get("finances", {})
    taux     = caveaux.get("taux_occupation", 0)
    total_paye    = finances.get("total_paye", 0)
    total_impaye  = finances.get("total_impaye", 0)
    total_facture = finances.get("total_facture", 0)

    export_msg = ft.Text("", size=11, color=ft.Colors.GREEN_400)

    def do_export(fmt):
        try:
            res = api.export_csv(state["token"]) if fmt == "csv" else api.export_excel(state["token"])
            if res.status_code == 200:
                ext   = "csv" if fmt == "csv" else "xlsx"
                fname = f"registre_funeraire.{ext}"
                tmp   = os.path.join(tempfile.gettempdir(), fname)
                with open(tmp, "wb") as f:
                    f.write(res.content)
                if os.name == "nt":
                    os.startfile(tmp)
                else:
                    subprocess.Popen(["xdg-open", tmp])
                export_msg.value = f"✅ Fichier téléchargé : {tmp}"
                export_msg.color = ft.Colors.GREEN_400
            else:
                export_msg.value = f"Erreur export : {res.status_code}"
                export_msg.color = ft.Colors.RED_400
            page.update()
        except Exception as ex:
            export_msg.value = str(ex)
            export_msg.color = ft.Colors.RED_400
            page.update()

    def barre(label, valeur, total_ref, color):
        pct = round((valeur / total_ref * 100)) if total_ref > 0 else 0
        return ft.Column(controls=[
            ft.Row(controls=[
                ft.Text(label, size=11, color=ft.Colors.WHITE, expand=True),
                ft.Text(f"{valeur} ({pct}%)", size=11, color=SECONDARY)
            ]),
            ft.ProgressBar(value=pct/100, bgcolor=SECONDARY+"20", color=color,
                           border_radius=4, height=6)
        ], spacing=4)

    def row_bloc(b):
        t = b.get("taux", 0)
        color = "#00CC77" if t < 70 else "#FF9922" if t < 90 else "#FF4444"
        return ft.Container(
            content=ft.Row(controls=[
                ft.Column(controls=[
                    ft.Text(f"{b['bloc']} — {b['zone']}", size=12,
                            weight=ft.FontWeight.W_500, color=ft.Colors.WHITE),
                    ft.Text(f"{b['occupes']} / {b['total']} occupés", size=10, color=SECONDARY)
                ], spacing=2, expand=True),
                ft.Column(controls=[
                    ft.Text(f"{t}%", size=12, weight=ft.FontWeight.BOLD, color=color),
                    ft.ProgressBar(value=t/100, bgcolor=SECONDARY+"20", color=color,
                                   border_radius=4, height=5, width=120)
                ], spacing=3, horizontal_alignment=ft.CrossAxisAlignment.END)
            ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=BG_CARD, border_radius=8, padding=12,
            border=ft.Border.all(1, SECONDARY + "20")
        )

    def section_title(txt):
        return ft.Container(
            content=ft.Text(txt, size=11, color=SECONDARY + "CC", weight=ft.FontWeight.BOLD),
            padding=ft.Padding.only(top=8, bottom=4)
        )

    col_gauche = ft.Column(
        controls=[
            section_title("OCCUPATION DES CAVEAUX"),
            ft.Row(controls=[
                kpi_mini("Total",       caveaux.get("total", 0),       "#4D7FFF"),
                kpi_mini("Disponibles", caveaux.get("disponibles", 0), "#00CC77"),
                kpi_mini("Occupés",     caveaux.get("occupes", 0),     "#FF4444"),
                kpi_mini("Réservés",    caveaux.get("reserves", 0),    "#FF9922"),
            ], spacing=10),
            ft.Container(
                content=ft.Column(controls=[
                    ft.Row(controls=[
                        ft.Text("Taux d'occupation global", size=12,
                                color=ft.Colors.WHITE, expand=True),
                        ft.Text(f"{taux}%", size=14, weight=ft.FontWeight.BOLD,
                                color="#00CC77" if taux < 70 else "#FF9922" if taux < 90 else "#FF4444")
                    ]),
                    ft.ProgressBar(
                        value=taux/100, bgcolor=SECONDARY+"20",
                        color="#00CC77" if taux < 70 else "#FF9922" if taux < 90 else "#FF4444",
                        border_radius=6, height=10
                    )
                ], spacing=8),
                bgcolor=BG_CARD, border_radius=10, padding=16,
                border=ft.Border.all(1, SECONDARY + "25")
            ),
            section_title("RÉSERVATIONS"),
            ft.Container(
                content=ft.Column(controls=[
                    barre("Total",      resa.get("total", 0),     resa.get("total", 1),    "#4D7FFF"),
                    barre("Validées",   resa.get("validees", 0),  resa.get("total", 1),    "#00CC77"),
                    barre("En attente", resa.get("en_attente", 0),resa.get("total", 1),    "#FF9922"),
                ], spacing=10),
                bgcolor=BG_CARD, border_radius=10, padding=16,
                border=ft.Border.all(1, SECONDARY + "25")
            ),
            section_title("FINANCES"),
            ft.Row(controls=[
                kpi_mini("Total facturé", f"{int(total_facture):,} F".replace(",", " "), "#4D7FFF"),
                kpi_mini("Encaissé",      f"{int(total_paye):,} F".replace(",", " "),    "#00CC77"),
                kpi_mini("Impayé",        f"{int(total_impaye):,} F".replace(",", " "),  "#FF4444"),
            ], spacing=10),
        ],
        spacing=12,
        expand=True
    )

    col_droite = ft.Column(
        controls=[
            section_title("STATS PAR BLOC"),
            ft.Column(
                controls=[row_bloc(b) for b in blocs] if blocs else [
                    ft.Container(content=ft.Text("Aucun bloc configuré", size=12, color=SECONDARY), padding=20)
                ],
                spacing=8, scroll=ft.ScrollMode.AUTO, height=280
            ),
            section_title("EXPORTS"),
            ft.Container(
                content=ft.Column(controls=[
                    ft.Text("Registre funéraire", size=13,
                            weight=ft.FontWeight.W_500, color=ft.Colors.WHITE),
                    ft.Text("Exporter toutes les réservations avec les détails du caveau.",
                            size=11, color=SECONDARY),
                    ft.Row(controls=[
                        ft.Container(
                            content=ft.Row(controls=[
                                ft.Icon(ft.Icons.DOWNLOAD_OUTLINED, size=14, color=ft.Colors.WHITE),
                                ft.Text("Export CSV", size=12, color=ft.Colors.WHITE,
                                        weight=ft.FontWeight.BOLD)
                            ], spacing=6),
                            bgcolor="#00CC77", border_radius=8,
                            padding=ft.Padding.symmetric(horizontal=14, vertical=8),
                            ink=True, on_click=lambda e: page.run_thread(do_export, "csv")
                        ),
                        ft.Container(
                            content=ft.Row(controls=[
                                ft.Icon(ft.Icons.TABLE_CHART_OUTLINED, size=14, color=ft.Colors.WHITE),
                                ft.Text("Export Excel", size=12, color=ft.Colors.WHITE,
                                        weight=ft.FontWeight.BOLD)
                            ], spacing=6),
                            bgcolor="#1D6F42", border_radius=8,
                            padding=ft.Padding.symmetric(horizontal=14, vertical=8),
                            ink=True, on_click=lambda e: page.run_thread(do_export, "excel")
                        ),
                    ], spacing=10),
                    export_msg,
                ], spacing=10),
                bgcolor=BG_CARD, border_radius=10, padding=16,
                border=ft.Border.all(1, SECONDARY + "25")
            ),
        ],
        spacing=12,
        width=340
    )

    main_content = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Column(controls=[
                            ft.Text("Reporting", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            ft.Text("Tableau de bord analytique", size=12, color=SECONDARY),
                        ], spacing=2),
                        ft.Container(
                            content=ft.Row(controls=[
                                ft.Icon(ft.Icons.REFRESH, size=14, color=ft.Colors.WHITE),
                                ft.Text("Actualiser", size=12, color=ft.Colors.WHITE)
                            ], spacing=6),
                            bgcolor=PRIMARY, border_radius=8,
                            padding=ft.Padding.symmetric(horizontal=14, vertical=8),
                            ink=True, on_click=lambda e: page_reporting(page, state, nav)
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Row(
                    controls=[col_gauche, col_droite],
                    spacing=20, expand=True,
                    vertical_alignment=ft.CrossAxisAlignment.START
                )
            ],
            spacing=16, expand=True, scroll=ft.ScrollMode.AUTO
        ),
        padding=24,
        expand=True
    )

    page.overlay.clear()
    page.controls.clear()
    page.add(
        ft.Row(
            controls=[
                build_sidebar(page, state, "reporting", nav),
                ft.Column(controls=[build_header(page, state), main_content], spacing=0, expand=True)
            ],
            spacing=0,
            expand=True
        )
    )
    page.update()
