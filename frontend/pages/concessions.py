import flet as ft
import re
from config import PRIMARY, SECONDARY, BG_DARK, BG_CARD, CONC_STATUT_COLORS, CONC_STATUT_LABELS, CONC_TYPE_LABELS
from components.sidebar import build_sidebar
from components.header import build_header
from components.widgets import btn
import services.api as api


def page_concessions(page: ft.Page, state: dict, nav):
    page.overlay.clear()
    page.controls.clear()
    page.add(
        ft.Row(
            controls=[
                build_sidebar(page, state, "concessions", nav),
                ft.Column(
                    controls=[
                        build_header(page, state),
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.ProgressRing(color=PRIMARY, width=40, height=40),
                                    ft.Text("Chargement des concessions...", size=13, color=SECONDARY)
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
        res_conc = api.get_concessions(state["token"])
        if res_conc.status_code in (401, 403):
            _erreur(page, state, nav, "Accès refusé — droits insuffisants")
            return
        if res_conc.status_code != 200:
            _erreur(page, state, nav, f"Erreur serveur : {res_conc.status_code}")
            return
        try:
            res_resa = api.get_reservations(state["token"])
            resa_data = res_resa.json() if res_resa.status_code == 200 else []
        except Exception:
            resa_data = []
        _construire(page, state, nav, res_conc.json(), resa_data)
    except Exception as ex:
        _erreur(page, state, nav, str(ex))


def _erreur(page, state, nav, msg):
    # Initialiser la ref de recherche sur la liste
    for ctrl in main_content.content.controls:
        if hasattr(ctrl, "data") and ctrl.data == "liste_conc":
            liste_search_ref["container"] = ctrl
            break

    page.overlay.clear()
    page.controls.clear()
    page.add(
        ft.Row(
            controls=[
                build_sidebar(page, state, "concessions", nav),
                ft.Column(
                    controls=[
                        build_header(page, state),
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Icon(ft.Icons.ERROR_OUTLINE, size=50, color=ft.Colors.RED_400),
                                    ft.Text(msg, size=13, color=ft.Colors.RED_400),
                                    btn("Réessayer", lambda e: page_concessions(page, state, nav), width=200)
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


def _construire(page, state, nav, concessions, reservations):
    feedback   = ft.Text("", size=12, color=ft.Colors.RED_400)
    resa_index = {r["id"]: r for r in reservations}
    conc_ids   = {c["reservation_id"] for c in concessions}
    resa_dispo = [r for r in reservations if r["statut"] == "VALIDEE" and r["id"] not in conc_ids]

    def do_resilier(cid):
        try:
            res = api.resilier_concession(state["token"], cid)
            if res.status_code == 200:
                page_concessions(page, state, nav)
            else:
                feedback.value = f"Résiliation refusée : {res.status_code}"
                page.update()
        except Exception as ex:
            feedback.value = str(ex)
            page.update()

    def card_conc(c):
        couleur     = CONC_STATUT_COLORS.get(c["statut"], "#555555")
        label_s     = CONC_STATUT_LABELS.get(c["statut"], c["statut"])
        label_t     = CONC_TYPE_LABELS.get(c["type_concession"], c["type_concession"])
        resa        = resa_index.get(c["reservation_id"], {})
        defunt      = f"{resa.get('prenom_defunt','—')} {resa.get('nom_defunt','—')}"
        date_fin    = c.get("date_fin") or "Perpétuelle"

        bouton = []
        if c["statut"] == "ACTIVE":
            bouton = [ft.Container(
                content=ft.Row(controls=[
                    ft.Icon(ft.Icons.CANCEL_OUTLINED, size=13, color=ft.Colors.WHITE),
                    ft.Text("Résilier", size=11, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
                ], spacing=6),
                bgcolor="#FF4444", border_radius=8,
                padding=ft.Padding.symmetric(horizontal=12, vertical=7),
                ink=True,
                on_click=lambda e, cid=c["id"]: page.run_thread(do_resilier, cid)
            )]

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(width=4, height=70, bgcolor=couleur, border_radius=2),
                    ft.Column(
                        controls=[
                            ft.Row(controls=[
                                ft.Text(f"Concession #{c['id']}", size=14,
                                        weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                ft.Container(content=ft.Text(label_s, size=10, color=ft.Colors.WHITE),
                                             bgcolor=couleur, border_radius=6,
                                             padding=ft.Padding.symmetric(horizontal=8, vertical=2)),
                                ft.Container(content=ft.Text(label_t, size=10, color=ft.Colors.WHITE),
                                             bgcolor=SECONDARY + "60", border_radius=6,
                                             padding=ft.Padding.symmetric(horizontal=8, vertical=2)),
                            ], spacing=8),
                            ft.Row(controls=[
                                ft.Icon(ft.Icons.PERSON_OUTLINED, size=12, color=SECONDARY),
                                ft.Text(defunt, size=11, color=SECONDARY),
                                ft.Icon(ft.Icons.CALENDAR_TODAY_OUTLINED, size=12, color=SECONDARY),
                                ft.Text(f"Du {c['date_debut']} au {date_fin}", size=11, color=SECONDARY),
                            ], spacing=6),
                            ft.Row(controls=[
                                ft.Icon(ft.Icons.PAYMENTS_OUTLINED, size=12, color=SECONDARY),
                                ft.Text(f"{c['montant']} FCFA", size=12, color=ft.Colors.WHITE,
                                        weight=ft.FontWeight.W_500),
                                ft.Icon(ft.Icons.TIMER_OUTLINED, size=12, color=SECONDARY),
                                ft.Text(f"{c['duree_annees']} ans"
                                        if c["type_concession"] != "PERPETUELLE" else "Perpétuelle",
                                        size=11, color=SECONDARY),
                            ], spacing=6),
                        ],
                        spacing=4, expand=True
                    ),
                    ft.Row(controls=bouton, spacing=8)
                ],
                spacing=14,
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            ),
            bgcolor=BG_CARD, border_radius=10, padding=14,
            border=ft.Border.all(1, SECONDARY + "20"),
        )

    # KPIs
    total     = len(concessions)
    actives   = len([c for c in concessions if c["statut"] == "ACTIVE"])
    expirees  = len([c for c in concessions if c["statut"] == "EXPIREE"])
    resiliees = len([c for c in concessions if c["statut"] == "RESILIEE"])

    kpis = ft.Row(controls=[
        ft.Container(content=ft.Column(controls=[
            ft.Text(str(actives), size=24, weight=ft.FontWeight.BOLD, color="#00CC77"),
            ft.Text("Actives", size=10, color=SECONDARY)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
        bgcolor=BG_CARD, border_radius=10,
        padding=ft.Padding.symmetric(horizontal=20, vertical=12),
        border=ft.Border.all(1, "#00CC77" + "40"), expand=True),

        ft.Container(content=ft.Column(controls=[
            ft.Text(str(expirees), size=24, weight=ft.FontWeight.BOLD, color="#FF9922"),
            ft.Text("Expirées", size=10, color=SECONDARY)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
        bgcolor=BG_CARD, border_radius=10,
        padding=ft.Padding.symmetric(horizontal=20, vertical=12),
        border=ft.Border.all(1, "#FF9922" + "40"), expand=True),

        ft.Container(content=ft.Column(controls=[
            ft.Text(str(resiliees), size=24, weight=ft.FontWeight.BOLD, color="#FF4444"),
            ft.Text("Résiliées", size=10, color=SECONDARY)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
        bgcolor=BG_CARD, border_radius=10,
        padding=ft.Padding.symmetric(horizontal=20, vertical=12),
        border=ft.Border.all(1, "#FF4444" + "40"), expand=True),

        ft.Container(content=ft.Column(controls=[
            ft.Text(str(total), size=24, weight=ft.FontWeight.BOLD, color=SECONDARY),
            ft.Text("Total", size=10, color=SECONDARY)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
        bgcolor=BG_CARD, border_radius=10,
        padding=ft.Padding.symmetric(horizontal=20, vertical=12),
        border=ft.Border.all(1, SECONDARY + "40"), expand=True),
    ], spacing=12)

    # Formulaire
    resa_dd   = ft.Dropdown(
        label="Réservation validée",
        options=[ft.dropdown.Option(
            key=str(r["id"]),
            text=f"#{r['id']} — {r['prenom_defunt']} {r['nom_defunt']} (Caveau #{r['caveau_id']})"
        ) for r in resa_dispo],
        width=400, border_color=SECONDARY, color=ft.Colors.WHITE, bgcolor=BG_DARK,
    )
    type_dd   = ft.Dropdown(
        label="Type", value="TEMPORAIRE",
        options=[
            ft.dropdown.Option(key="TEMPORAIRE",  text="Temporaire"),
            ft.dropdown.Option(key="PERPETUELLE", text="Perpétuelle"),
        ],
        width=400, border_color=SECONDARY, color=ft.Colors.WHITE, bgcolor=BG_DARK,
    )
    date_f    = ft.TextField(label="Date de début (AAAA-MM-JJ)", width=400,
                             border_color=SECONDARY, color=ft.Colors.WHITE, bgcolor=BG_DARK,
                             hint_text="ex : 2026-06-19",
                             hint_style=ft.TextStyle(color=SECONDARY + "60"))
    duree_f   = ft.TextField(label="Durée (années)", value="10", width=400,
                             border_color=SECONDARY, color=ft.Colors.WHITE, bgcolor=BG_DARK)
    montant_f = ft.TextField(label="Montant (FCFA)", width=400,
                             border_color=SECONDARY, color=ft.Colors.WHITE, bgcolor=BG_DARK,
                             hint_text="ex : 150000",
                             hint_style=ft.TextStyle(color=SECONDARY + "60"))
    form_msg  = ft.Text("", size=12, color=ft.Colors.RED_400)
    dlg_ref   = {"dlg": None}

    def do_create(resa_id, type_c, date_d, duree, montant):
        try:
            res = api.create_concession(state["token"], {
                "reservation_id": int(resa_id),
                "type_concession": type_c,
                "date_debut": date_d,
                "duree_annees": int(duree),
                "montant": float(montant)
            })
            if res.status_code == 200:
                dlg_ref["dlg"].open = False
                page.update()
                page_concessions(page, state, nav)
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
        if not resa_dd.value or not date_f.value or not montant_f.value:
            form_msg.value = "Veuillez remplir tous les champs obligatoires"
            form_msg.color = ft.Colors.RED_400
            page.update()
            return
        duree = duree_f.value if type_dd.value == "TEMPORAIRE" else "0"
        form_msg.value = "Création en cours..."
        form_msg.color = ft.Colors.AMBER_400
        page.update()
        page.run_thread(do_create, resa_dd.value, type_dd.value,
                        date_f.value, duree, montant_f.value)

    def open_form(e):
        form_col = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text("Nouvelle concession", size=16,
                                weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE_OUTLINED, icon_color=SECONDARY,
                            on_click=lambda e: (setattr(dlg_ref["dlg"], "open", False), page.update())
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Divider(color=SECONDARY + "30", height=1),
                resa_dd if resa_dispo else ft.Row(controls=[
                    ft.Icon(ft.Icons.WARNING_AMBER_OUTLINED, size=16, color="#FF9922"),
                    ft.Text("Aucune réservation validée sans concession", size=12, color="#FF9922")
                ], spacing=6),
                type_dd, date_f, duree_f, montant_f, form_msg,
                btn("Créer la concession", on_create, width=400,
                    icon=ft.Icons.ADD, disabled=(not resa_dispo))
            ],
            spacing=12, tight=True
        )
        dlg = ft.AlertDialog(
            modal=True, bgcolor=BG_CARD,
            content=ft.Container(content=form_col, width=440),
            shape=ft.RoundedRectangleBorder(radius=14),
        )
        dlg_ref["dlg"] = dlg
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    # Filtre statut
    filtre_statut = {"value": "TOUS"}
    filtre_btns_s = {}
    liste_filtre_ref = {"container": None}

    def apply_filters(q="", statut="TOUS"):
        filtered = concessions
        if statut != "TOUS":
            filtered = [c for c in filtered if c["statut"] == statut]
        if q:
            filtered = [c for c in filtered
                        if q in str(c.get("id","")).lower()
                        or q in resa_index.get(c["reservation_id"],{}).get("nom_defunt","").lower()
                        or q in resa_index.get(c["reservation_id"],{}).get("prenom_defunt","").lower()]
        if liste_filtre_ref["container"]:
            liste_filtre_ref["container"].content = ft.Column(
                controls=[card_conc(c) for c in filtered] if filtered else [
                    ft.Container(
                        content=ft.Text("Aucun résultat", size=12, color=SECONDARY),
                        padding=20
                    )
                ],
                spacing=10, scroll=ft.ScrollMode.AUTO, height=480
            )
            page.update()

    # Barre de recherche
    search_field = ft.TextField(
        hint_text="Rechercher par défunt, numéro...",
        prefix_icon=ft.Icons.SEARCH,
        width=300,
        height=40,
        border_color=SECONDARY,
        focused_border_color=PRIMARY,
        bgcolor=BG_CARD,
        color=ft.Colors.WHITE,
        hint_style=ft.TextStyle(color=SECONDARY + "80"),
        border_radius=8,
        text_size=12,
    )
    liste_search_ref = {"container": None}

    def on_search(e):
        apply_filters(
            q=search_field.value.lower().strip(),
            statut=filtre_statut["value"]
        )

    search_field.on_change = on_search

    def mk_filtre_statut(label, key):
        c = ft.Container(
            content=ft.Text(label, size=10, color=ft.Colors.WHITE),
            bgcolor=PRIMARY if key == "TOUS" else BG_CARD,
            border_radius=6,
            padding=ft.Padding.symmetric(horizontal=10, vertical=5),
            border=ft.Border.all(1, SECONDARY + "30"),
            ink=True,
            on_click=lambda e, k=key: _switch_statut(k)
        )
        filtre_btns_s[key] = c
        return c

    def _switch_statut(key):
        filtre_statut["value"] = key
        for k, c in filtre_btns_s.items():
            c.bgcolor = PRIMARY if k == key else BG_CARD
        apply_filters(q=search_field.value.lower().strip(), statut=key)

    filtre_statut_row = ft.Row(controls=[
        mk_filtre_statut("Toutes",    "TOUS"),
        mk_filtre_statut("Actives",   "ACTIVE"),
        mk_filtre_statut("Expirées",  "EXPIREE"),
        mk_filtre_statut("Résiliées", "RESILIEE"),
    ], spacing=6)

    liste_container = ft.Container(
        content=ft.Column(
            controls=[card_conc(c) for c in concessions] if concessions else [
                ft.Container(
                    content=ft.Column(controls=[
                        ft.Icon(ft.Icons.DESCRIPTION_OUTLINED, size=40, color=SECONDARY),
                        ft.Text("Aucune concession enregistrée", size=13, color=SECONDARY)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    alignment=ft.Alignment(0, 0), padding=40
                )
            ],
            spacing=10, scroll=ft.ScrollMode.AUTO, height=480
        ),
        expand=True,
        data="liste_conc"
    )
    liste_search_ref["container"] = liste_container
    liste_filtre_ref["container"] = liste_container

    main_content = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Column(controls=[
                            ft.Text("Concessions", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            ft.Text(f"{total} concession(s)", size=12, color=SECONDARY),
                        ], spacing=2),
                        ft.Row(controls=[
                            search_field,
                            ft.Container(
                                content=ft.Row(controls=[
                                    ft.Icon(ft.Icons.ADD, size=14, color=ft.Colors.WHITE),
                                    ft.Text("Nouvelle concession", size=12, color=ft.Colors.WHITE)
                                ], spacing=6),
                                bgcolor=PRIMARY, border_radius=8,
                                padding=ft.Padding.symmetric(horizontal=14, vertical=8),
                                ink=True, on_click=open_form
                            )
                        ], spacing=10)
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                kpis,
                filtre_statut_row,
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
                build_sidebar(page, state, "concessions", nav),
                ft.Column(controls=[build_header(page, state), main_content], spacing=0, expand=True)
            ],
            spacing=0,
            expand=True
        )
    )
    page.update()
