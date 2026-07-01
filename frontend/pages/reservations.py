import flet as ft
from config import PRIMARY, SECONDARY, BG_DARK, BG_CARD, RESA_STATUT_COLORS, RESA_STATUT_LABELS
from components.sidebar import build_sidebar
from components.header import build_header
from components.widgets import btn
import services.api as api


def page_reservations(page: ft.Page, state: dict, nav):
    page.overlay.clear()
    page.controls.clear()
    page.add(
        ft.Row(
            controls=[
                build_sidebar(page, state, "reservations", nav),
                ft.Column(
                    controls=[
                        build_header(page, state),
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.ProgressRing(color=PRIMARY, width=40, height=40),
                                    ft.Text("Chargement des réservations...", size=13, color=SECONDARY)
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
        res_list    = api.get_reservations(state["token"])
        res_caveaux = api.get_caveaux(state["token"])
        if res_list.status_code == 200 and res_caveaux.status_code == 200:
            resa_data = res_list.json()
            # Mettre à jour le badge sidebar
            state["resa_count"] = len([r for r in resa_data if r["statut"] == "EN_ATTENTE"])
            _construire(page, state, nav, resa_data, res_caveaux.json())
        elif res_list.status_code in (401, 403):
            _erreur(page, state, nav, "Accès non autorisé pour ce rôle")
        else:
            _erreur(page, state, nav, f"Erreur {res_list.status_code}")
    except Exception as ex:
        _erreur(page, state, nav, str(ex))


def _erreur(page, state, nav, msg):
    page.overlay.clear()
    page.controls.clear()
    page.add(
        ft.Row(
            controls=[
                build_sidebar(page, state, "reservations", nav),
                ft.Column(
                    controls=[
                        build_header(page, state),
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Icon(ft.Icons.ERROR_OUTLINE, size=50, color=ft.Colors.RED_400),
                                    ft.Text(msg, size=13, color=ft.Colors.RED_400),
                                    btn("Réessayer", lambda e: page_reservations(page, state, nav), width=200)
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


def _construire(page, state, nav, reservations, caveaux):
    feedback = ft.Text("", size=12, color=ft.Colors.RED_400)

    # Filtre actif
    filtre_actif   = {"value": "TOUS"}
    liste_ref      = {"container": None}
    filtre_btns    = {}

    def do_action(reservation_id, statut):
        try:
            res = api.valider_reservation(state["token"], reservation_id, statut)
            if res.status_code == 200:
                page_reservations(page, state, nav)
            else:
                feedback.value = f"Action refusée : {res.status_code}"
                page.update()
        except Exception as ex:
            feedback.value = str(ex)
            page.update()

    def card_for(r):
        couleur = RESA_STATUT_COLORS.get(r["statut"], "#555555")
        label   = RESA_STATUT_LABELS.get(r["statut"], r["statut"])
        date_d  = r.get("date_demande", "")[:10]

        actions = []
        if r["statut"] == "EN_ATTENTE":
            actions = [
                ft.Container(
                    content=ft.Row(controls=[
                        ft.Icon(ft.Icons.THUMB_UP_OUTLINED, size=14, color=ft.Colors.WHITE),
                        ft.Text("Valider", size=12, color=ft.Colors.WHITE)
                    ], spacing=6),
                    bgcolor="#00CC77", border_radius=8,
                    padding=ft.Padding.symmetric(horizontal=12, vertical=7),
                    ink=True,
                    on_click=lambda e, rid=r["id"]: page.run_thread(do_action, rid, "VALIDEE")
                ),
                ft.Container(
                    content=ft.Row(controls=[
                        ft.Icon(ft.Icons.THUMB_DOWN_OUTLINED, size=14, color=ft.Colors.WHITE),
                        ft.Text("Refuser", size=12, color=ft.Colors.WHITE)
                    ], spacing=6),
                    bgcolor="#FF4444", border_radius=8,
                    padding=ft.Padding.symmetric(horizontal=12, vertical=7),
                    ink=True,
                    on_click=lambda e, rid=r["id"]: page.run_thread(do_action, rid, "REFUSEE")
                ),
            ]

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(width=4, height=70, bgcolor=couleur, border_radius=2),
                    ft.Column(
                        controls=[
                            ft.Row(controls=[
                                ft.Text(f"{r['prenom_defunt']} {r['nom_defunt']}", size=14,
                                        weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                ft.Container(
                                    content=ft.Text(label, size=10, color=ft.Colors.WHITE),
                                    bgcolor=couleur, border_radius=6,
                                    padding=ft.Padding.symmetric(horizontal=8, vertical=2)
                                )
                            ], spacing=10),
                            ft.Row(controls=[
                                ft.Icon(ft.Icons.CALENDAR_TODAY_OUTLINED, size=12, color=SECONDARY),
                                ft.Text(f"Décès le {r['date_deces']}", size=11, color=SECONDARY),
                                ft.Icon(ft.Icons.DOOR_BACK_DOOR_OUTLINED, size=12, color=SECONDARY),
                                ft.Text(f"Caveau #{r['caveau_id']}", size=11, color=SECONDARY),
                                ft.Icon(ft.Icons.ACCESS_TIME_OUTLINED, size=12, color=SECONDARY),
                                ft.Text(f"Demande : {date_d}", size=11, color=SECONDARY),
                            ], spacing=6),
                            ft.Text(r.get("notes", "") or "—", size=11, color=SECONDARY + "AA"),
                        ],
                        spacing=4,
                        expand=True
                    ),
                    ft.Row(controls=actions, spacing=8)
                ],
                spacing=14,
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            ),
            bgcolor=BG_CARD, border_radius=10, padding=14,
            border=ft.Border.all(1, SECONDARY + "20"),
        )

    def build_liste(filtre):
        items = reservations if filtre == "TOUS" else [r for r in reservations if r["statut"] == filtre]
        if not items:
            return ft.Container(
                content=ft.Column(controls=[
                    ft.Icon(ft.Icons.INBOX_OUTLINED, size=40, color=SECONDARY),
                    ft.Text("Aucune réservation dans cette catégorie", size=13, color=SECONDARY)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                alignment=ft.Alignment(0, 0), padding=40
            )
        return ft.Column(
            controls=[card_for(r) for r in items],
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
            height=480
        )

    def on_filtre(f):
        def handler(e):
            filtre_actif["value"] = f
            liste_ref["container"].content = build_liste(f)
            for key, c in filtre_btns.items():
                c.bgcolor = PRIMARY if key == f else BG_CARD
            page.update()
        return handler

    def mk_filtre_btn(label, key):
        c = ft.Container(
            content=ft.Text(label, size=11, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
            bgcolor=PRIMARY if key == "TOUS" else BG_CARD,
            border_radius=8,
            padding=ft.Padding.symmetric(horizontal=14, vertical=7),
            border=ft.Border.all(1, SECONDARY + "30"),
            ink=True,
            on_click=on_filtre(key),
        )
        filtre_btns[key] = c
        return c

    # KPIs
    total      = len(reservations)
    en_attente = len([r for r in reservations if r["statut"] == "EN_ATTENTE"])
    validees   = len([r for r in reservations if r["statut"] == "VALIDEE"])
    refusees   = len([r for r in reservations if r["statut"] == "REFUSEE"])

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
                ft.Text(str(refusees), size=24, weight=ft.FontWeight.BOLD, color="#FF4444"),
                ft.Text("Refusées", size=10, color=SECONDARY)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
            bgcolor=BG_CARD, border_radius=10,
            padding=ft.Padding.symmetric(horizontal=20, vertical=12),
            border=ft.Border.all(1, "#FF4444" + "40"), expand=True
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

    # Formulaire création
    caveaux_dispo = [c for c in caveaux if c["statut"] == "DISPONIBLE"]
    dlg_ref = {"dlg": None}

    def open_form(e):
        # Nouveaux champs créés à chaque ouverture = pas d'état résiduel
        caveau_dd = ft.Dropdown(
            label="Caveau disponible",
            options=[ft.dropdown.Option(key=str(c["id"]), text=c["numero"]) for c in caveaux_dispo],
            width=380, border_color=SECONDARY, color=ft.Colors.WHITE, bgcolor=BG_DARK,
        )
        nom_f    = ft.TextField(label="Nom du défunt", width=380, border_color=SECONDARY,
                                color=ft.Colors.WHITE, bgcolor=BG_DARK)
        prenom_f = ft.TextField(label="Prénom du défunt", width=380, border_color=SECONDARY,
                                color=ft.Colors.WHITE, bgcolor=BG_DARK)
        date_f   = ft.TextField(label="Date de décès (AAAA-MM-JJ)", width=380,
                                border_color=SECONDARY, color=ft.Colors.WHITE, bgcolor=BG_DARK,
                                hint_text="2026-05-30")
        notes_f  = ft.TextField(label="Notes (optionnel)", width=380, border_color=SECONDARY,
                                color=ft.Colors.WHITE, bgcolor=BG_DARK,
                                multiline=True, min_lines=2, max_lines=3)
        form_msg = ft.Text("", size=12, color=ft.Colors.RED_400)

        def close_form(e=None):
            dlg_ref["dlg"].open = False
            page.update()

        def do_create(caveau_id, nom, prenom, date_deces, notes):
            import time
            try:
                res = api.create_reservation(state["token"], {
                    "caveau_id":     int(caveau_id),
                    "nom_defunt":    nom,
                    "prenom_defunt": prenom,
                    "date_deces":    date_deces,
                    "notes":         notes or ""
                })
                if res.status_code == 200:
                    data = res.json()
                    if "error" in data:
                        form_msg.value = data["error"]
                        form_msg.color = ft.Colors.RED_400
                        page.update()
                    else:
                        # Fermer immédiatement + recharger
                        dlg_ref["dlg"].open = False
                        page.update()
                        time.sleep(0.1)
                        page_reservations(page, state, nav)
                else:
                    form_msg.value = f"Erreur serveur : {res.status_code}"
                    form_msg.color = ft.Colors.RED_400
                    page.update()
            except Exception as ex:
                form_msg.value = str(ex)
                form_msg.color = ft.Colors.RED_400
                page.update()

        def on_create(e):
            if not caveau_dd.value or not nom_f.value or not prenom_f.value or not date_f.value:
                form_msg.value = "Veuillez remplir tous les champs obligatoires"
                form_msg.color = ft.Colors.RED_400
                page.update()
                return
            form_msg.value = "Création en cours..."
            form_msg.color = ft.Colors.AMBER_400
            page.update()
            page.run_thread(do_create, caveau_dd.value, nom_f.value,
                            prenom_f.value, date_f.value, notes_f.value)

        form_col = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text("Nouvelle réservation", size=16,
                                weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ft.IconButton(icon=ft.Icons.CLOSE_OUTLINED,
                                      icon_color=SECONDARY, on_click=close_form)
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Divider(color=SECONDARY + "30", height=1),
                caveau_dd if caveaux_dispo else ft.Row(controls=[
                    ft.Icon(ft.Icons.WARNING_AMBER_OUTLINED, size=16, color="#FF9922"),
                    ft.Text("Aucun caveau disponible", size=12, color="#FF9922")
                ], spacing=6),
                nom_f, prenom_f, date_f, notes_f, form_msg,
                btn("Créer la réservation", on_create, width=380,
                    icon=ft.Icons.ADD, disabled=(not caveaux_dispo))
            ],
            spacing=12, tight=True
        )
        dlg = ft.AlertDialog(
            modal=True, bgcolor=BG_CARD,
            content=ft.Container(content=form_col, width=420),
            shape=ft.RoundedRectangleBorder(radius=14),
        )
        dlg_ref["dlg"] = dlg
        page.overlay.append(dlg)
        dlg.open = True
        page.update()


    liste_container = ft.Container(content=build_liste("TOUS"), expand=True)
    liste_ref["container"] = liste_container

    filtre_row = ft.Row(controls=[
        mk_filtre_btn("Toutes",     "TOUS"),
        mk_filtre_btn("En attente", "EN_ATTENTE"),
        mk_filtre_btn("Validées",   "VALIDEE"),
        mk_filtre_btn("Refusées",   "REFUSEE"),
        mk_filtre_btn("Annulées",   "ANNULEE"),
    ], spacing=8)

    main_content = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Column(controls=[
                            ft.Text("Réservations", size=20, weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.WHITE),
                            ft.Text(f"{total} demande(s) au total", size=12, color=SECONDARY),
                        ], spacing=2),
                        ft.Container(
                            content=ft.Row(controls=[
                                ft.Icon(ft.Icons.ADD, size=14, color=ft.Colors.WHITE),
                                ft.Text("Nouvelle réservation", size=12, color=ft.Colors.WHITE)
                            ], spacing=6),
                            bgcolor=PRIMARY, border_radius=8,
                            padding=ft.Padding.symmetric(horizontal=14, vertical=8),
                            ink=True, on_click=open_form
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                kpis,
                filtre_row,
                feedback,
                liste_container,
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
                build_sidebar(page, state, "reservations", nav),
                ft.Column(controls=[build_header(page, state), main_content], spacing=0, expand=True)
            ],
            spacing=0,
            expand=True
        )
    )
    page.update()
