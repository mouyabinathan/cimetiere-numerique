import flet as ft
import flet_map as fm
import time
from config import PRIMARY, SECONDARY, BG_DARK, BG_CARD, STATUT_COLORS, STATUT_LABELS
from components.sidebar import build_sidebar
from components.header import build_header
import services.api as api


def page_cartographie(page: ft.Page, state: dict, nav):
    page.overlay.clear()
    page.controls.clear()
    page.add(
        ft.Row(
            controls=[
                build_sidebar(page, state, "carte", nav),
                ft.Column(
                    controls=[
                        build_header(page, state),
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.ProgressRing(color=PRIMARY, width=40, height=40),
                                    ft.Text("Chargement de la carte...", size=13, color=SECONDARY)
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
        res = api.get_carte(state["token"])
        if res.status_code == 200:
            _construire(page, state, nav, res.json())
            time.sleep(0.3)
            page.update()
        else:
            _erreur(page, state, nav, f"Erreur {res.status_code}")
    except Exception as ex:
        _erreur(page, state, nav, str(ex))


def _erreur(page, state, nav, msg):
    page.overlay.clear()
    page.controls.clear()
    page.add(
        ft.Row(
            controls=[
                build_sidebar(page, state, "carte", nav),
                ft.Column(
                    controls=[
                        build_header(page, state),
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


def _construire(page, state, nav, caveaux):
    detail_panel = ft.Container(
        content=ft.Column(
            controls=[
                ft.Icon(ft.Icons.PLACE_OUTLINED, size=36, color=SECONDARY),
                ft.Text("Sélectionnez un caveau", size=13, color=SECONDARY,
                        text_align=ft.TextAlign.CENTER),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10
        ),
        bgcolor=BG_CARD, border_radius=12, padding=20,
        border=ft.Border.all(1, SECONDARY + "25"),
        width=300, height=440,
        alignment=ft.Alignment(0, 0)
    )

    def on_select(caveau):
        bouton_reserver = []
        if caveau.get("statut") == "DISPONIBLE":
            bouton_reserver = [
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.ADD_CIRCLE_OUTLINED, size=14, color=ft.Colors.WHITE),
                            ft.Text("Réserver ce caveau", size=12, color=ft.Colors.WHITE,
                                    weight=ft.FontWeight.BOLD)
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=6
                    ),
                    bgcolor=PRIMARY, border_radius=8,
                    padding=ft.Padding.symmetric(horizontal=14, vertical=10),
                    ink=True,
                    on_click=lambda e: nav("reservations")
                    
                )
            ]

        detail_panel.content = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Container(width=14, height=14, border_radius=4,
                                     bgcolor=STATUT_COLORS.get(caveau["statut"], "#555555")),
                        ft.Text(caveau["numero"], size=16, weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE)
                    ],
                    spacing=8
                ),
                ft.Divider(color=SECONDARY + "30", height=1),
                ft.Row(controls=[
                    ft.Text("Statut", size=11, color=SECONDARY),
                    ft.Text(STATUT_LABELS.get(caveau["statut"], caveau["statut"]), size=12, color=ft.Colors.WHITE)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row(controls=[
                    ft.Text("Latitude", size=11, color=SECONDARY),
                    ft.Text(str(caveau.get("latitude", "—")), size=12, color=ft.Colors.WHITE)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row(controls=[
                    ft.Text("Longitude", size=11, color=SECONDARY),
                    ft.Text(str(caveau.get("longitude", "—")), size=12, color=ft.Colors.WHITE)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row(controls=[
                    ft.Text("Dimensions", size=11, color=SECONDARY),
                    ft.Text(f"{caveau.get('longueur','—')}m × {caveau.get('largeur','—')}m",
                            size=12, color=ft.Colors.WHITE)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                *bouton_reserver,
            ],
            spacing=14
        )
        page.update()

    markers, valid_coords = [], []
    # Décaler les marqueurs avec les mêmes coordonnées
    seen_coords = {}
    for c in caveaux:
        lat, lng = c.get("latitude"), c.get("longitude")
        if lat is None or lng is None:
            continue
        # Décalage si coordonnées identiques
        key = (round(lat, 5), round(lng, 5))
        if key in seen_coords:
            seen_coords[key] += 1
            offset = seen_coords[key] * 0.00005
            lat = lat + offset
            lng = lng + offset
        else:
            seen_coords[key] = 0
        valid_coords.append((lat, lng))
        marker_content = ft.Container(
            content=ft.Text(c["numero"], size=8, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
            width=34, height=34,
            bgcolor=STATUT_COLORS.get(c["statut"], "#555555"),
            border=ft.Border.all(2, ft.Colors.WHITE),
            border_radius=17,
            alignment=ft.Alignment(0, 0),
            ink=True,
            on_click=lambda e, caveau=c: on_select(caveau),
            tooltip=f"{c['numero']} — {STATUT_LABELS.get(c['statut'], c['statut'])}"
        )
        markers.append(fm.Marker(
            content=marker_content,
            coordinates=fm.MapLatitudeLongitude(latitude=lat, longitude=lng),
            width=34, height=34,
        ))

    if valid_coords:
        center_lat = sum(c[0] for c in valid_coords) / len(valid_coords)
        center_lng = sum(c[1] for c in valid_coords) / len(valid_coords)
    else:
        center_lat, center_lng = -4.7761, 11.8635

    map_widget = fm.Map(
        initial_center=fm.MapLatitudeLongitude(latitude=center_lat, longitude=center_lng),
        initial_zoom=16,
        layers=[
            fm.TileLayer(
                url_template="https://a.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png",
                user_agent_package_name="com.cimetiere.pointenoire",
                subdomains=["a", "b", "c", "d"],
                max_native_zoom=19,
                max_zoom=20,
            ),
            fm.MarkerLayer(markers=markers),
        ],
    )

    legend = ft.Row(
        controls=[
            ft.Row(controls=[
                ft.Container(width=10, height=10, bgcolor=color, border_radius=3),
                ft.Text(STATUT_LABELS[statut], size=11, color=SECONDARY)
            ], spacing=6)
            for statut, color in STATUT_COLORS.items()
        ],
        spacing=18
    )

    main_content = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Column(controls=[
                            ft.Text("Cartographie", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            ft.Text(f"{len(caveaux)} caveaux géolocalisés", size=12, color=SECONDARY),
                        ], spacing=2),
                        ft.Container(
                            content=ft.Row(controls=[
                                ft.Icon(ft.Icons.REFRESH, size=14, color=ft.Colors.WHITE),
                                ft.Text("Actualiser", size=12, color=ft.Colors.WHITE)
                            ], spacing=6),
                            bgcolor=PRIMARY, border_radius=8,
                            padding=ft.Padding.symmetric(horizontal=14, vertical=8),
                            ink=True, on_click=lambda e: page_cartographie(page, state, nav)
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                legend,
                ft.Row(
                    controls=[
                        ft.Container(
                            content=map_widget if markers else ft.Column(
                                controls=[
                                    ft.Icon(ft.Icons.MAP_OUTLINED, size=40, color=SECONDARY),
                                    ft.Text("Aucun caveau géolocalisé", size=13, color=SECONDARY)
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=10
                            ),
                            border_radius=8, expand=True,
                            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                        ),
                        detail_panel
                    ],
                    spacing=12,
                    expand=True
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
                build_sidebar(page, state, "carte", nav),
                ft.Column(controls=[build_header(page, state), main_content], spacing=0, expand=True)
            ],
            spacing=0,
            expand=True
        )
    )
    page.update()


def _ouvrir_form_reservation(page, state, nav, caveau):
    nom_f    = ft.TextField(label="Nom du défunt", width=380, border_color=SECONDARY,
                            color=ft.Colors.WHITE, bgcolor=BG_DARK,
                            label_style=ft.TextStyle(color=SECONDARY))
    prenom_f = ft.TextField(label="Prénom du défunt", width=380, border_color=SECONDARY,
                            color=ft.Colors.WHITE, bgcolor=BG_DARK,
                            label_style=ft.TextStyle(color=SECONDARY))
    date_f   = ft.TextField(label="Date de décès (AAAA-MM-JJ)", width=380,
                            border_color=SECONDARY, color=ft.Colors.WHITE, bgcolor=BG_DARK,
                            label_style=ft.TextStyle(color=SECONDARY),
                            hint_text="ex : 2026-06-15",
                            hint_style=ft.TextStyle(color=SECONDARY + "60"))
    notes_f  = ft.TextField(label="Notes (optionnel)", width=380, border_color=SECONDARY,
                            color=ft.Colors.WHITE, bgcolor=BG_DARK,
                            label_style=ft.TextStyle(color=SECONDARY),
                            multiline=True, min_lines=2, max_lines=3)
    msg_f    = ft.Text("", size=12, color=ft.Colors.RED_400)
    dlg_ref  = {"dlg": None}

    def do_submit():
        import time
        try:
            res = api.create_reservation(state["token"], {
                "caveau_id":     caveau["id"],
                "nom_defunt":    nom_f.value.strip(),
                "prenom_defunt": prenom_f.value.strip(),
                "date_deces":    date_f.value.strip(),
                "notes":         notes_f.value.strip() if notes_f.value else ""
            })
            if res.status_code == 200:
                data = res.json()
                if "error" in data:
                    msg_f.value = data["error"]
                    msg_f.color = ft.Colors.RED_400
                    page.update()
                else:
                    dlg_ref["dlg"].open = False
                    page.update()
                    time.sleep(0.1)
                    page_cartographie(page, state, nav)
            else:
                msg_f.value = f"Erreur serveur : {res.status_code}"
                msg_f.color = ft.Colors.RED_400
                page.update()
        except Exception as ex:
            msg_f.value = str(ex)
            msg_f.color = ft.Colors.RED_400
            page.update()

    def on_submit(e):
        if not nom_f.value or not prenom_f.value or not date_f.value:
            msg_f.value = "Veuillez remplir tous les champs obligatoires"
            msg_f.color = ft.Colors.RED_400
            page.update()
            return
        msg_f.value = "Envoi en cours..."
        msg_f.color = ft.Colors.AMBER_400
        page.update()
        import threading
        threading.Thread(target=do_submit, daemon=True).start()


    dlg = ft.AlertDialog(
        modal=True, bgcolor=BG_CARD,
        shape=ft.RoundedRectangleBorder(radius=14),
        title=ft.Row(controls=[
            ft.Container(width=12, height=12, border_radius=3, bgcolor="#00CC77"),
            ft.Text(f"Réserver le caveau {caveau['numero']}", size=15,
                    weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
        ], spacing=8),
        content=ft.Column(
            controls=[
                ft.Row(controls=[
                    ft.Icon(ft.Icons.PLACE_OUTLINED, size=13, color=SECONDARY),
                    ft.Text(f"Lat {caveau.get('latitude','—')} · Lng {caveau.get('longitude','—')}",
                            size=11, color=SECONDARY),
                ], spacing=6),
                ft.Divider(color=SECONDARY + "30", height=1),
                prenom_f, nom_f, date_f, notes_f, msg_f,
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.CHECK, color=ft.Colors.WHITE, size=14),
                            ft.Text("Confirmer la réservation", color=ft.Colors.WHITE,
                                    weight=ft.FontWeight.BOLD, size=13)
                        ],
                        alignment=ft.MainAxisAlignment.CENTER, spacing=8
                    ),
                    width=380, height=44, bgcolor=PRIMARY, border_radius=10,
                    alignment=ft.Alignment(0, 0), on_click=on_submit, ink=True,
                ),
            ],
            spacing=12, width=400, tight=True,
        ),
        actions=[
            ft.TextButton(
                content=ft.Text("Annuler", color=SECONDARY, size=12),
                on_click=lambda e: (setattr(dlg, "open", False), page.update())
            )
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    dlg_ref["dlg"] = dlg
    page.overlay.append(dlg)
    dlg.open = True
    page.update()
