import flet as ft
from config import PRIMARY, SECONDARY, BG_DARK, BG_CARD
from components.sidebar import build_sidebar
from components.header import build_header
from components.widgets import btn
import services.api as api


EXHU_COLORS = {
    "EN_ATTENTE": "#FF9922",
    "VALIDEE":    "#00CC77",
    "REFUSEE":    "#FF4444",
    "EFFECTUEE":  "#4D7FFF",
}
EXHU_LABELS = {
    "EN_ATTENTE": "En attente",
    "VALIDEE":    "Validée",
    "REFUSEE":    "Refusée",
    "EFFECTUEE":  "Effectuée",
}


def page_exhumations(page: ft.Page, state: dict, nav):
    page.overlay.clear()
    page.controls.clear()
    page.add(
        ft.Row(
            controls=[
                build_sidebar(page, state, "exhumations", nav),
                ft.Column(
                    controls=[
                        build_header(page, state),
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.ProgressRing(color=PRIMARY, width=40, height=40),
                                    ft.Text("Chargement des exhumations...", size=13, color=SECONDARY)
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
        res_exhu = api.get_exhumations(state["token"])
        if res_exhu.status_code in (401, 403):
            _erreur(page, state, nav, "Accès refusé — droits insuffisants")
            return
        if res_exhu.status_code != 200:
            _erreur(page, state, nav, f"Erreur serveur : {res_exhu.status_code}")
            return
        try:
            res_resa = api.get_reservations(state["token"])
            resa_data = res_resa.json() if res_resa.status_code == 200 else []
        except Exception:
            resa_data = []
        _construire(page, state, nav, res_exhu.json(), resa_data)
    except Exception as ex:
        _erreur(page, state, nav, str(ex))


def _erreur(page, state, nav, msg):
    page.overlay.clear()
    page.controls.clear()
    page.add(
        ft.Row(
            controls=[
                build_sidebar(page, state, "exhumations", nav),
                ft.Column(
                    controls=[
                        build_header(page, state),
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Icon(ft.Icons.ERROR_OUTLINE, size=50, color=ft.Colors.RED_400),
                                    ft.Text(msg, size=13, color=ft.Colors.RED_400),
                                    btn("Réessayer", lambda e: page_exhumations(page, state, nav), width=200)
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


def _construire(page, state, nav, exhumations, reservations):
    feedback    = ft.Text("", size=12, color=ft.Colors.RED_400)
    resa_index  = {r["id"]: r for r in reservations}
    resa_validees = [r for r in reservations if r["statut"] == "VALIDEE"]

    def do_valider(exhu_id, statut, notes, date_exhu):
        try:
            import re
            payload = {"statut": statut, "notes_admin": notes or ""}
            if date_exhu and re.match(r"^\d{4}-\d{2}-\d{2}$", date_exhu.strip()):
                payload["date_exhumation"] = date_exhu.strip()
            res = api.valider_exhumation(state["token"], exhu_id, payload)
            if res.status_code == 200:
                page_exhumations(page, state, nav)
            else:
                feedback.value = f"Erreur : {res.status_code}"
                page.update()
        except Exception as ex:
            feedback.value = str(ex)
            page.update()

    def ouvrir_dialog_validation(exhu):
        notes_f    = ft.TextField(label="Notes admin (optionnel)", width=380,
                                  border_color=SECONDARY, color=ft.Colors.WHITE, bgcolor=BG_DARK,
                                  multiline=True, min_lines=2)
        date_f     = ft.TextField(label="Date d'exhumation (AAAA-MM-JJ)", width=380,
                                  border_color=SECONDARY, color=ft.Colors.WHITE, bgcolor=BG_DARK,
                                  hint_text="ex : 2026-07-01",
                                  hint_style=ft.TextStyle(color=SECONDARY + "60"))
        statut_dd  = ft.Dropdown(
            label="Décision",
            options=[
                ft.dropdown.Option(key="VALIDEE", text="✅ Valider"),
                ft.dropdown.Option(key="REFUSEE", text="❌ Refuser"),
                ft.dropdown.Option(key="EFFECTUEE", text="✔ Marquer effectuée"),
            ],
            width=380, border_color=SECONDARY,
            color=ft.Colors.WHITE, bgcolor=BG_DARK
        )
        dlg_ref = {"dlg": None}

        def on_confirm(e):
            if not statut_dd.value:
                return
            dlg_ref["dlg"].open = False
            page.update()
            page.run_thread(do_valider, exhu["id"], statut_dd.value,
                            notes_f.value, date_f.value or None)

        dlg = ft.AlertDialog(
            modal=True, bgcolor=BG_CARD,
            shape=ft.RoundedRectangleBorder(radius=14),
            title=ft.Text(f"Exhumation #{exhu['id']}", size=15,
                          weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            content=ft.Column(
                controls=[
                    ft.Text(f"Motif : {exhu['motif']}", size=12, color=SECONDARY),
                    ft.Divider(color=SECONDARY + "30", height=1),
                    statut_dd, date_f, notes_f,
                ],
                spacing=12, width=400, tight=True
            ),
            actions=[
                ft.TextButton(
                    content=ft.Text("Annuler", color=SECONDARY, size=12),
                    on_click=lambda e: (setattr(dlg, "open", False), page.update())
                ),
                ft.TextButton(
                    content=ft.Text("Confirmer", color=PRIMARY, size=12,
                                    weight=ft.FontWeight.BOLD),
                    on_click=on_confirm
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        dlg_ref["dlg"] = dlg
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    def card_exhu(e):
        couleur = EXHU_COLORS.get(e["statut"], "#555555")
        label   = EXHU_LABELS.get(e["statut"], e["statut"])
        resa    = resa_index.get(e["reservation_id"], {})
        defunt  = f"{resa.get('prenom_defunt','—')} {resa.get('nom_defunt','—')}"
        date_d  = e["date_demande"][:10]

        actions = []
        if e["statut"] == "EN_ATTENTE":
            actions = [
                ft.Container(
                    content=ft.Row(controls=[
                        ft.Icon(ft.Icons.RULE_OUTLINED, size=13, color=ft.Colors.WHITE),
                        ft.Text("Traiter", size=11, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
                    ], spacing=6),
                    bgcolor=PRIMARY, border_radius=8,
                    padding=ft.Padding.symmetric(horizontal=12, vertical=7),
                    ink=True,
                    on_click=lambda ev, exhu=e: ouvrir_dialog_validation(exhu)
                )
            ]

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(width=4, height=70, bgcolor=couleur, border_radius=2),
                    ft.Column(
                        controls=[
                            ft.Row(controls=[
                                ft.Text(f"Exhumation #{e['id']}", size=14,
                                        weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                ft.Container(
                                    content=ft.Text(label, size=10, color=ft.Colors.WHITE),
                                    bgcolor=couleur, border_radius=6,
                                    padding=ft.Padding.symmetric(horizontal=8, vertical=2)
                                ),
                            ], spacing=8),
                            ft.Row(controls=[
                                ft.Icon(ft.Icons.PERSON_OUTLINED, size=12, color=SECONDARY),
                                ft.Text(defunt, size=11, color=SECONDARY),
                                ft.Icon(ft.Icons.CALENDAR_TODAY_OUTLINED, size=12, color=SECONDARY),
                                ft.Text(f"Demande : {date_d}", size=11, color=SECONDARY),
                            ], spacing=6),
                            ft.Text(e.get("motif", "—")[:80] + "..." if len(e.get("motif","")) > 80
                                    else e.get("motif","—"),
                                    size=11, color=SECONDARY + "AA"),
                        ],
                        spacing=4, expand=True
                    ),
                    ft.Row(controls=actions, spacing=8)
                ],
                spacing=14,
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            ),
            bgcolor=BG_CARD, border_radius=10, padding=14,
            border=ft.Border.all(1, SECONDARY + "20"),
        )

    # ---- Formulaire nouvelle exhumation ----
    resa_dd = ft.Dropdown(
        label="Réservation (caveau concerné)",
        options=[
            ft.dropdown.Option(
                key=str(r["id"]),
                text=f"#{r['id']} — {r['prenom_defunt']} {r['nom_defunt']} (Caveau #{r['caveau_id']})"
            ) for r in resa_validees
        ],
        width=400, border_color=SECONDARY, color=ft.Colors.WHITE, bgcolor=BG_DARK,
    )
    motif_f = ft.TextField(
        label="Motif de la demande", width=400,
        border_color=SECONDARY, color=ft.Colors.WHITE, bgcolor=BG_DARK,
        multiline=True, min_lines=3, max_lines=5
    )
    date_exhu_f = ft.TextField(
        label="Date souhaitée (optionnel, AAAA-MM-JJ)", width=400,
        border_color=SECONDARY, color=ft.Colors.WHITE, bgcolor=BG_DARK,
        hint_text="ex : 2026-07-15",
        hint_style=ft.TextStyle(color=SECONDARY + "60")
    )
    form_msg = ft.Text("", size=12, color=ft.Colors.RED_400)
    dlg_f_ref = {"dlg": None}

    def do_create_exhu(resa_id, motif, date_exhu):
        try:
            payload = {"reservation_id": int(resa_id), "motif": motif}
            if date_exhu:
                payload["date_exhumation"] = date_exhu
            res = api.create_exhumation(state["token"], payload)
            if res.status_code == 200:
                dlg_f_ref["dlg"].open = False
                page.update()
                page_exhumations(page, state, nav)
            else:
                form_msg.color = ft.Colors.RED_400
                form_msg.value = f"Erreur : {res.status_code}"
                form_msg.color = ft.Colors.RED_400
                page.update()
        except Exception as ex:
            form_msg.value = str(ex)
            form_msg.color = ft.Colors.RED_400
            page.update()

    def on_create(e):
        if not resa_dd.value or not motif_f.value:
            form_msg.value = "Réservation et motif obligatoires"
            form_msg.color = ft.Colors.RED_400
            page.update()
            return
        form_msg.value = "Envoi..."
        form_msg.color = ft.Colors.AMBER_400
        page.update()
        page.run_thread(do_create_exhu, resa_dd.value, motif_f.value, date_exhu_f.value or None)

    def open_form(e):
        form_col = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text("Nouvelle demande d'exhumation", size=15,
                                weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE_OUTLINED, icon_color=SECONDARY,
                            on_click=lambda e: (setattr(dlg_f_ref["dlg"], "open", False), page.update())
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Divider(color=SECONDARY + "30", height=1),
                resa_dd if resa_validees else ft.Row(controls=[
                    ft.Icon(ft.Icons.WARNING_AMBER_OUTLINED, size=16, color="#FF9922"),
                    ft.Text("Aucune réservation validée", size=12, color="#FF9922")
                ], spacing=6),
                motif_f, date_exhu_f, form_msg,
                btn("Soumettre la demande", on_create, width=400,
                    icon=ft.Icons.SEND_OUTLINED, disabled=(not resa_validees))
            ],
            spacing=12, tight=True
        )
        dlg = ft.AlertDialog(
            modal=True, bgcolor=BG_CARD,
            content=ft.Container(content=form_col, width=440),
            shape=ft.RoundedRectangleBorder(radius=14),
        )
        dlg_f_ref["dlg"] = dlg
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    # KPIs
    total     = len(exhumations)
    en_attente = len([e for e in exhumations if e["statut"] == "EN_ATTENTE"])
    validees  = len([e for e in exhumations if e["statut"] == "VALIDEE"])
    effectuees = len([e for e in exhumations if e["statut"] == "EFFECTUEE"])

    kpis = ft.Row(controls=[
        ft.Container(
            content=ft.Column(controls=[
                ft.Text(str(en_attente), size=24, weight=ft.FontWeight.BOLD, color="#FF9922"),
                ft.Text("En attente", size=10, color=SECONDARY)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
            bgcolor=BG_CARD, border_radius=10,
            padding=ft.Padding.symmetric(horizontal=20, vertical=12),
            border=ft.Border.all(1, "#FF9922" + "40"), expand=True
        ),
        ft.Container(
            content=ft.Column(controls=[
                ft.Text(str(validees), size=24, weight=ft.FontWeight.BOLD, color="#00CC77"),
                ft.Text("Validées", size=10, color=SECONDARY)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
            bgcolor=BG_CARD, border_radius=10,
            padding=ft.Padding.symmetric(horizontal=20, vertical=12),
            border=ft.Border.all(1, "#00CC77" + "40"), expand=True
        ),
        ft.Container(
            content=ft.Column(controls=[
                ft.Text(str(effectuees), size=24, weight=ft.FontWeight.BOLD, color="#4D7FFF"),
                ft.Text("Effectuées", size=10, color=SECONDARY)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
            bgcolor=BG_CARD, border_radius=10,
            padding=ft.Padding.symmetric(horizontal=20, vertical=12),
            border=ft.Border.all(1, "#4D7FFF" + "40"), expand=True
        ),
        ft.Container(
            content=ft.Column(controls=[
                ft.Text(str(total), size=24, weight=ft.FontWeight.BOLD, color=SECONDARY),
                ft.Text("Total", size=10, color=SECONDARY)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
            bgcolor=BG_CARD, border_radius=10,
            padding=ft.Padding.symmetric(horizontal=20, vertical=12),
            border=ft.Border.all(1, SECONDARY + "40"), expand=True
        ),
    ], spacing=12)

    main_content = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Column(controls=[
                            ft.Text("Exhumations", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            ft.Text(f"{total} demande(s) d'exhumation", size=12, color=SECONDARY),
                        ], spacing=2),
                        ft.Container(
                            content=ft.Row(controls=[
                                ft.Icon(ft.Icons.ADD, size=14, color=ft.Colors.WHITE),
                                ft.Text("Nouvelle demande", size=12, color=ft.Colors.WHITE)
                            ], spacing=6),
                            bgcolor=PRIMARY, border_radius=8,
                            padding=ft.Padding.symmetric(horizontal=14, vertical=8),
                            ink=True, on_click=open_form
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                kpis,
                feedback,
                ft.Column(
                    controls=[card_exhu(e) for e in exhumations] if exhumations else [
                        ft.Container(
                            content=ft.Column(controls=[
                                ft.Icon(ft.Icons.SWAP_HORIZ_OUTLINED, size=40, color=SECONDARY),
                                ft.Text("Aucune demande d'exhumation", size=13, color=SECONDARY)
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                            alignment=ft.Alignment(0, 0), padding=40
                        )
                    ],
                    spacing=10,
                    scroll=ft.ScrollMode.AUTO,
                    height=480
                )
            ],
            spacing=16,
            expand=True
        ),
        padding=24,
        expand=True
    )

    page.overlay.clear()
    page.controls.clear()
    page.add(
        ft.Row(
            controls=[
                build_sidebar(page, state, "exhumations", nav),
                ft.Column(controls=[build_header(page, state), main_content], spacing=0, expand=True)
            ],
            spacing=0,
            expand=True
        )
    )
    page.update()
