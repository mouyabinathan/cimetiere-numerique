import flet as ft
from config import PRIMARY, SECONDARY, BG_DARK, BG_CARD, STATUT_COLORS, STATUT_LABELS
from components.sidebar import build_sidebar
from components.header import build_header
from components.widgets import btn
import services.api as api


def page_parametres(page: ft.Page, state: dict, nav):
    page.overlay.clear()
    page.controls.clear()
    page.add(
        ft.Row(
            controls=[
                build_sidebar(page, state, "parametres", nav),
                ft.Column(
                    controls=[
                        build_header(page, state),
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.ProgressRing(color=PRIMARY, width=40, height=40),
                                    ft.Text("Chargement des paramètres...", size=13, color=SECONDARY)
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
        res_zones = api.get_zones(state["token"])
        if res_zones.status_code in (401, 403):
            _erreur(page, state, nav, "Accès refusé — droits insuffisants")
            return
        if res_zones.status_code != 200:
            _erreur(page, state, nav, f"Erreur serveur : {res_zones.status_code}")
            return
        try:
            res_blocs   = api.get_blocs(state["token"])
            blocs_data  = res_blocs.json() if res_blocs.status_code == 200 else []
        except Exception:
            blocs_data = []
        try:
            res_caveaux  = api.get_caveaux(state["token"])
            caveaux_data = res_caveaux.json() if res_caveaux.status_code == 200 else []
        except Exception:
            caveaux_data = []
        _construire(page, state, nav, res_zones.json(), blocs_data, caveaux_data)
    except Exception as ex:
        _erreur(page, state, nav, str(ex))


def _erreur(page, state, nav, msg):
    page.overlay.clear()
    page.controls.clear()
    page.add(
        ft.Row(
            controls=[
                build_sidebar(page, state, "parametres", nav),
                ft.Column(
                    controls=[
                        build_header(page, state),
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Icon(ft.Icons.ERROR_OUTLINE, size=50, color=ft.Colors.RED_400),
                                    ft.Text(msg, size=13, color=ft.Colors.RED_400),
                                    btn("Réessayer", lambda e: page_parametres(page, state, nav), width=200)
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


def _construire(page, state, nav, zones, blocs, caveaux):
    zone_index = {z["id"]: z["nom"] for z in zones}
    bloc_index = {b["id"]: b for b in blocs}
    onglet_actif = {"value": "zones"}
    tab_content  = {"ref": None}
    filtre_btns  = {}

    # ===== Champs de formulaire (reutilisables) =====
    def champ_texte(label, value="", hint="", width=None):
        return ft.TextField(
            label=label,
            value=value,
            hint_text=hint,
            border_color=SECONDARY,
            color=ft.Colors.WHITE,
            bgcolor=BG_DARK,
            label_style=ft.TextStyle(color=SECONDARY),
            expand=True if width is None else False,
            width=width
        )

    # ===== TAB ZONES =====
    def build_tab_zones():
        nom_z = champ_texte("Nom de la zone *")
        desc_z = champ_texte("Description", multiline=True, min_lines=2, max_lines=3)
        expl_z = ft.Checkbox(label="Exploitable", value=True,
                             active_color=PRIMARY, check_color=ft.Colors.WHITE)
        msg_z = ft.Text("", size=12, color=ft.Colors.RED_400)

        def do_create():
            try:
                res = api.create_zone(state["token"], {
                    "nom": nom_z.value.strip(),
                    "description": desc_z.value or "",
                    "exploitable": expl_z.value
                })
                if res.status_code == 200:
                    page_parametres(page, state, nav)
                else:
                    msg_z.value = f"Erreur : {res.status_code}"
                    msg_z.color = ft.Colors.RED_400
                    page.update()
            except Exception as ex:
                msg_z.value = str(ex)
                msg_z.color = ft.Colors.RED_400
                page.update()

        def on_create(e):
            if not nom_z.value:
                msg_z.value = "Le nom est obligatoire"
                msg_z.color = ft.Colors.RED_400
                page.update()
                return
            page.run_thread(do_create)

        def zone_row(z):
            color = "#00CC77" if z["exploitable"] else "#555555"
            label = "Exploitable" if z["exploitable"] else "Non exploitable"
            nb = len([b for b in blocs if b["zone_id"] == z["id"]])
            return ft.Container(
                content=ft.Row(controls=[
                    ft.Container(width=4, height=44, bgcolor=color, border_radius=2),
                    ft.Column(controls=[
                        ft.Text(z["nom"], size=13, weight=ft.FontWeight.W_500, color=ft.Colors.WHITE),
                        ft.Row(controls=[
                            ft.Container(content=ft.Text(label, size=9, color=ft.Colors.WHITE),
                                         bgcolor=color, border_radius=4,
                                         padding=ft.Padding.symmetric(horizontal=6, vertical=2)),
                            ft.Text(f"{nb} bloc(s)", size=10, color=SECONDARY),
                        ], spacing=6)
                    ], spacing=2, expand=True),
                ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=BG_CARD, border_radius=8, padding=10,
                border=ft.Border.all(1, SECONDARY + "20")
            )

        # Formulaire + liste en ResponsiveRow
        return ft.ResponsiveRow(controls=[
            ft.Container(
                content=ft.Column(controls=[
                    ft.Text("Nouvelle zone", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Divider(color=SECONDARY + "30", height=1),
                    nom_z, desc_z, expl_z, msg_z,
                    btn("Créer la zone", on_create, icon=ft.Icons.ADD, expand=True)
                ], spacing=12, tight=True),
                bgcolor=BG_CARD, border_radius=12, padding=20,
                border=ft.Border.all(1, SECONDARY + "25"),
                col={"sm": 12, "md": 5, "lg": 4}
            ),
            ft.Container(
                content=ft.Column(controls=[
                    ft.Text(f"{len(zones)} zone(s)", size=12, color=SECONDARY),
                    ft.Column(
                        controls=[zone_row(z) for z in zones] if zones else [
                            ft.Text("Aucune zone créée", size=12, color=SECONDARY)
                        ],
                        spacing=8, scroll=ft.ScrollMode.AUTO, expand=True
                    )
                ], spacing=10, expand=True),
                col={"sm": 12, "md": 7, "lg": 8},
                expand=True
            )
        ], spacing=20, expand=True)

    # ===== TAB BLOCS =====
    def build_tab_blocs():
        nom_b = champ_texte("Nom du bloc *")
        zone_dd = ft.Dropdown(
            label="Zone parente",
            options=[ft.dropdown.Option(key=str(z["id"]), text=z["nom"]) for z in zones],
            border_color=SECONDARY, color=ft.Colors.WHITE, bgcolor=BG_DARK,
            expand=True
        )
        msg_b = ft.Text("", size=12, color=ft.Colors.RED_400)

        def do_create():
            try:
                res = api.create_bloc(state["token"], {
                    "nom": nom_b.value.strip(), "zone_id": int(zone_dd.value)
                })
                if res.status_code == 200:
                    page_parametres(page, state, nav)
                else:
                    msg_b.value = f"Erreur : {res.status_code}"
                    msg_b.color = ft.Colors.RED_400
                    page.update()
            except Exception as ex:
                msg_b.value = str(ex)
                msg_b.color = ft.Colors.RED_400
                page.update()

        def on_create(e):
            if not nom_b.value or not zone_dd.value:
                msg_b.value = "Nom et zone obligatoires"
                msg_b.color = ft.Colors.RED_400
                page.update()
                return
            page.run_thread(do_create)

        def bloc_row(b):
            nb = len([c for c in caveaux if c["bloc_id"] == b["id"]])
            return ft.Container(
                content=ft.Row(controls=[
                    ft.Container(width=4, height=44, bgcolor=PRIMARY, border_radius=2),
                    ft.Column(controls=[
                        ft.Text(b["nom"], size=13, weight=ft.FontWeight.W_500, color=ft.Colors.WHITE),
                        ft.Row(controls=[
                            ft.Icon(ft.Icons.MAP_OUTLINED, size=11, color=SECONDARY),
                            ft.Text(zone_index.get(b["zone_id"], "—"), size=10, color=SECONDARY),
                            ft.Text(f"· {nb} caveau(x)", size=10, color=SECONDARY),
                        ], spacing=4)
                    ], spacing=2, expand=True),
                ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=BG_CARD, border_radius=8, padding=10,
                border=ft.Border.all(1, SECONDARY + "20")
            )

        return ft.ResponsiveRow(controls=[
            ft.Container(
                content=ft.Column(controls=[
                    ft.Text("Nouveau bloc", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Divider(color=SECONDARY + "30", height=1),
                    zone_dd if zones else ft.Text("⚠ Créez d'abord une zone", size=12, color="#FF9922"),
                    nom_b, msg_b,
                    btn("Créer le bloc", on_create, icon=ft.Icons.ADD, disabled=(not zones), expand=True)
                ], spacing=12, tight=True),
                bgcolor=BG_CARD, border_radius=12, padding=20,
                border=ft.Border.all(1, SECONDARY + "25"),
                col={"sm": 12, "md": 5, "lg": 4}
            ),
            ft.Container(
                content=ft.Column(controls=[
                    ft.Text(f"{len(blocs)} bloc(s)", size=12, color=SECONDARY),
                    ft.Column(
                        controls=[bloc_row(b) for b in blocs] if blocs else [
                            ft.Text("Aucun bloc créé", size=12, color=SECONDARY)
                        ],
                        spacing=8, scroll=ft.ScrollMode.AUTO, expand=True
                    )
                ], spacing=10, expand=True),
                col={"sm": 12, "md": 7, "lg": 8},
                expand=True
            )
        ], spacing=20, expand=True)

    # ===== TAB CAVEAUX =====
    def build_tab_caveaux():
        numero_c = champ_texte("Numéro (ex: C003) *")
        bloc_dd = ft.Dropdown(
            label="Bloc",
            options=[ft.dropdown.Option(
                key=str(b["id"]),
                text=f"{b['nom']} — {zone_index.get(b['zone_id'],'?')}"
            ) for b in blocs],
            border_color=SECONDARY, color=ft.Colors.WHITE, bgcolor=BG_DARK,
            expand=True
        )
        statut_dd = ft.Dropdown(
            label="Statut initial", value="DISPONIBLE",
            options=[
                ft.dropdown.Option(key="DISPONIBLE",    text="Disponible"),
                ft.dropdown.Option(key="INEXPLOITABLE", text="Inexploitable"),
            ],
            border_color=SECONDARY, color=ft.Colors.WHITE, bgcolor=BG_DARK,
            expand=True
        )
        lat_c = champ_texte("Latitude", hint="-4.7761")
        lng_c = champ_texte("Longitude", hint="11.8635")
        long_c = champ_texte("Longueur (m)", value="2.0")
        larg_c = champ_texte("Largeur (m)", value="1.0")
        msg_c = ft.Text("", size=12, color=ft.Colors.RED_400)

        def do_create():
            try:
                payload = {
                    "bloc_id": int(bloc_dd.value),
                    "numero":  numero_c.value.strip(),
                    "statut":  statut_dd.value,
                    "longueur":float(long_c.value or 2.0),
                    "largeur": float(larg_c.value or 1.0),
                }
                if lat_c.value: payload["latitude"]  = float(lat_c.value)
                if lng_c.value: payload["longitude"] = float(lng_c.value)
                res = api.create_caveau(state["token"], payload)
                if res.status_code == 200:
                    page_parametres(page, state, nav)
                else:
                    msg_c.value = f"Erreur : {res.status_code} — {res.text[:80]}"
                    msg_c.color = ft.Colors.RED_400
                    page.update()
            except Exception as ex:
                msg_c.value = str(ex)
                msg_c.color = ft.Colors.RED_400
                page.update()

        def on_create(e):
            if not numero_c.value or not bloc_dd.value:
                msg_c.value = "Numéro et bloc obligatoires"
                msg_c.color = ft.Colors.RED_400
                page.update()
                return
            page.run_thread(do_create)

        def caveau_row(c):
            color = STATUT_COLORS.get(c["statut"], "#555555")
            bloc_nom = bloc_index.get(c["bloc_id"], {}).get("nom", "—")
            geo = f"📍 {c['latitude']:.4f}, {c['longitude']:.4f}" if c.get("latitude") else "Non géolocalisé"
            return ft.Container(
                content=ft.Row(controls=[
                    ft.Container(width=4, height=50, bgcolor=color, border_radius=2),
                    ft.Column(controls=[
                        ft.Row(controls=[
                            ft.Text(c["numero"], size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            ft.Container(
                                content=ft.Text(STATUT_LABELS.get(c["statut"], c["statut"]),
                                                size=9, color=ft.Colors.WHITE),
                                bgcolor=color, border_radius=4,
                                padding=ft.Padding.symmetric(horizontal=6, vertical=2)
                            ),
                        ], spacing=6),
                        ft.Row(controls=[
                            ft.Icon(ft.Icons.GRID_VIEW_OUTLINED, size=11, color=SECONDARY),
                            ft.Text(bloc_nom, size=10, color=SECONDARY),
                            ft.Text(f"· {c['longueur']}m×{c['largeur']}m", size=10, color=SECONDARY),
                            ft.Text(f"· {geo}", size=10, color=SECONDARY),
                        ], spacing=4)
                    ], spacing=2, expand=True),
                ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=BG_CARD, border_radius=8, padding=10,
                border=ft.Border.all(1, SECONDARY + "20")
            )

        return ft.ResponsiveRow(controls=[
            ft.Container(
                content=ft.Column(controls=[
                    ft.Text("Nouveau caveau", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Divider(color=SECONDARY + "30", height=1),
                    bloc_dd if blocs else ft.Text("⚠ Créez d'abord un bloc", size=12, color="#FF9922"),
                    numero_c, statut_dd,
                    ft.ResponsiveRow(controls=[
                        ft.Container(lat_c, col={"sm": 12, "md": 6}),
                        ft.Container(lng_c, col={"sm": 12, "md": 6}),
                    ], spacing=10),
                    ft.ResponsiveRow(controls=[
                        ft.Container(long_c, col={"sm": 12, "md": 6}),
                        ft.Container(larg_c, col={"sm": 12, "md": 6}),
                    ], spacing=10),
                    msg_c,
                    btn("Créer le caveau", on_create, icon=ft.Icons.ADD, disabled=(not blocs), expand=True)
                ], spacing=12, tight=True),
                bgcolor=BG_CARD, border_radius=12, padding=20,
                border=ft.Border.all(1, SECONDARY + "25"),
                col={"sm": 12, "md": 5, "lg": 4}
            ),
            ft.Container(
                content=ft.Column(controls=[
                    ft.Text(f"{len(caveaux)} caveau(x)", size=12, color=SECONDARY),
                    ft.Column(
                        controls=[caveau_row(c) for c in caveaux] if caveaux else [
                            ft.Text("Aucun caveau créé", size=12, color=SECONDARY)
                        ],
                        spacing=6, scroll=ft.ScrollMode.AUTO, expand=True
                    )
                ], spacing=10, expand=True),
                col={"sm": 12, "md": 7, "lg": 8},
                expand=True
            )
        ], spacing=20, expand=True)

    # ===== BARRE D'ONGLETS =====
    tab_container = ft.Container(content=build_tab_zones(), expand=True)
    tab_content["ref"] = tab_container

    def switch_tab(key):
        def handler(e):
            onglet_actif["value"] = key
            builders = {"zones": build_tab_zones, "blocs": build_tab_blocs, "caveaux": build_tab_caveaux}
            tab_container.content = builders[key]()
            for k, c in filtre_btns.items():
                c.bgcolor = PRIMARY if k == key else BG_CARD
                c.content.controls[0].color = ft.Colors.WHITE if k == key else SECONDARY
            page.update()
        return handler

    def mk_tab(label, key, icon):
        active = (key == "zones")
        c = ft.Container(
            content=ft.Row(controls=[
                ft.Icon(icon, size=14, color=ft.Colors.WHITE if active else SECONDARY),
                ft.Text(label, size=12,
                        color=ft.Colors.WHITE if active else SECONDARY,
                        weight=ft.FontWeight.W_500 if active else ft.FontWeight.W_400)
            ], spacing=6),
            bgcolor=PRIMARY if active else BG_CARD,
            border_radius=8,
            padding=ft.Padding.symmetric(horizontal=16, vertical=8),
            border=ft.Border.all(1, SECONDARY + "30"),
            ink=True, on_click=switch_tab(key)
        )
        filtre_btns[key] = c
        return c

    tab_row = ft.Row(controls=[
        mk_tab("Zones",   "zones",   ft.Icons.LAYERS_OUTLINED),
        mk_tab("Blocs",   "blocs",   ft.Icons.GRID_VIEW_OUTLINED),
        mk_tab("Caveaux", "caveaux", ft.Icons.PLACE_OUTLINED),
    ], spacing=10, scroll=ft.ScrollMode.AUTO)

    main_content = ft.Container(
        content=ft.Column(
            controls=[
                ft.ResponsiveRow(controls=[
                    ft.Column(controls=[
                        ft.Text("Paramètres", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ft.Text("Configuration du terrain", size=12, color=SECONDARY),
                    ], spacing=2, col={"sm": 12, "md": 8}),
                    ft.Container(
                        content=ft.Row(controls=[
                            ft.Icon(ft.Icons.REFRESH, size=14, color=ft.Colors.WHITE),
                            ft.Text("Actualiser", size=12, color=ft.Colors.WHITE)
                        ], spacing=6),
                        bgcolor=PRIMARY, border_radius=8,
                        padding=ft.Padding.symmetric(horizontal=14, vertical=8),
                        ink=True, on_click=lambda e: page_parametres(page, state, nav),
                        col={"sm": 12, "md": 4}
                    )
                ], spacing=10, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                tab_row,
                tab_container,
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
                build_sidebar(page, state, "parametres", nav),
                ft.Column(controls=[build_header(page, state), main_content], spacing=0, expand=True)
            ],
            spacing=0,
            expand=True
        )
    )
    page.update()