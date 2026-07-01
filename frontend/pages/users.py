import flet as ft
from config import PRIMARY, SECONDARY, BG_DARK, BG_CARD
from components.sidebar import build_sidebar
from components.header import build_header
from components.widgets import btn
import services.api as api


ROLE_COLORS = {
    "ADMIN":        "#FF4444",
    "SECRETARIAT":  "#4D7FFF",
    "AGENT":        "#FF9922",
    "CLIENT":       "#00CC77",
}
ROLE_LABELS = {
    "ADMIN":       "Administrateur",
    "SECRETARIAT": "Secrétariat",
    "AGENT":       "Agent terrain",
    "CLIENT":      "Client",
}


def page_users(page: ft.Page, state: dict, nav):
    page.overlay.clear()
    page.controls.clear()
    page.add(
        ft.Row(
            controls=[
                build_sidebar(page, state, "users", nav),
                ft.Column(
                    controls=[
                        build_header(page, state),
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.ProgressRing(color=PRIMARY, width=40, height=40),
                                    ft.Text("Chargement des utilisateurs...", size=13, color=SECONDARY)
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
        res = api.get_users(state["token"])
        if res.status_code in (401, 403):
            _erreur(page, state, nav, "Accès refusé — droits Admin requis")
            return
        if res.status_code != 200:
            _erreur(page, state, nav, f"Erreur serveur : {res.status_code}")
            return
        _construire(page, state, nav, res.json())
    except Exception as ex:
        _erreur(page, state, nav, str(ex))


def _erreur(page, state, nav, msg):
    page.overlay.clear()
    page.controls.clear()
    page.add(
        ft.Row(
            controls=[
                build_sidebar(page, state, "users", nav),
                ft.Column(
                    controls=[
                        build_header(page, state),
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Icon(ft.Icons.ERROR_OUTLINE, size=50, color=ft.Colors.RED_400),
                                    ft.Text(msg, size=13, color=ft.Colors.RED_400),
                                    btn("Réessayer", lambda e: page_users(page, state, nav), width=200)
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


def _construire(page, state, nav, users):
    feedback = ft.Text("", size=12, color=ft.Colors.RED_400)

    def user_card(u):
        role    = u.get("role", "CLIENT")
        couleur = ROLE_COLORS.get(role, "#555555")
        label   = ROLE_LABELS.get(role, role)
        initials = "".join([p[0].upper() for p in
                            f"{u.get('first_name','')} {u.get('last_name','')}".split()[:2]])
        nom = f"{u.get('first_name','')} {u.get('last_name','')}".strip() or u.get("email","—")

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Text(initials or "?", size=14, weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.WHITE),
                        width=40, height=40, bgcolor=couleur,
                        border_radius=20, alignment=ft.Alignment(0, 0)
                    ),
                    ft.Column(
                        controls=[
                            ft.Row(controls=[
                                ft.Text(nom, size=13, weight=ft.FontWeight.W_500, color=ft.Colors.WHITE),
                                ft.Container(
                                    content=ft.Text(label, size=10, color=ft.Colors.WHITE),
                                    bgcolor=couleur, border_radius=6,
                                    padding=ft.Padding.symmetric(horizontal=8, vertical=2)
                                ),
                                *(
                                    [ft.Container(
                                        content=ft.Text("Actif", size=9, color=ft.Colors.WHITE),
                                        bgcolor="#00CC77", border_radius=6,
                                        padding=ft.Padding.symmetric(horizontal=6, vertical=2)
                                    )] if u.get("is_active", True) else
                                    [ft.Container(
                                        content=ft.Text("Inactif", size=9, color=ft.Colors.WHITE),
                                        bgcolor="#555555", border_radius=6,
                                        padding=ft.Padding.symmetric(horizontal=6, vertical=2)
                                    )]
                                )
                            ], spacing=8),
                            ft.Row(controls=[
                                ft.Icon(ft.Icons.EMAIL_OUTLINED, size=12, color=SECONDARY),
                                ft.Text(u.get("email", "—"), size=11, color=SECONDARY),
                            ], spacing=4),
                        ],
                        spacing=4,
                        expand=True
                    ),
                ],
                spacing=14,
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            ),
            bgcolor=BG_CARD, border_radius=10, padding=14,
            border=ft.Border.all(1, SECONDARY + "20"),
        )

    # ---- Formulaire création utilisateur ----
    first_name_f = ft.TextField(label="Prénom *", width=380, border_color=SECONDARY,
                                color=ft.Colors.WHITE, bgcolor=BG_DARK,
                                label_style=ft.TextStyle(color=SECONDARY))
    last_name_f  = ft.TextField(label="Nom *", width=380, border_color=SECONDARY,
                                color=ft.Colors.WHITE, bgcolor=BG_DARK,
                                label_style=ft.TextStyle(color=SECONDARY))
    email_f      = ft.TextField(label="Email *", width=380, border_color=SECONDARY,
                                color=ft.Colors.WHITE, bgcolor=BG_DARK,
                                label_style=ft.TextStyle(color=SECONDARY))
    password_f   = ft.TextField(label="Mot de passe *", password=True,
                                can_reveal_password=True, width=380,
                                border_color=SECONDARY, color=ft.Colors.WHITE, bgcolor=BG_DARK,
                                label_style=ft.TextStyle(color=SECONDARY))
    role_dd      = ft.Dropdown(
        label="Rôle",
        options=[
            ft.dropdown.Option(key="ADMIN",       text="Administrateur"),
            ft.dropdown.Option(key="SECRETARIAT", text="Secrétariat"),
            ft.dropdown.Option(key="AGENT",       text="Agent terrain"),
            ft.dropdown.Option(key="CLIENT",      text="Client"),
        ],
        value="CLIENT",
        width=380, border_color=SECONDARY,
        color=ft.Colors.WHITE, bgcolor=BG_DARK,
    )
    form_msg  = ft.Text("", size=12, color=ft.Colors.RED_400)
    dlg_ref   = {"dlg": None}

    def do_create(prenom, nom, email, password, role):
        try:
            # Générer username depuis email (avant le @)
            username = email.split("@")[0].lower().replace(".", "_")
            res = api.create_user(state["token"], {
                "username":   username,
                "first_name": prenom,
                "last_name":  nom,
                "email":      email,
                "password":   password,
                "telephone":  "",
                "role":       role,
            })
            if res.status_code == 200:
                data = res.json()
                if "error" in data:
                    form_msg.value = data["error"]
                    form_msg.color = ft.Colors.RED_400
                    page.update()
                else:
                    dlg_ref["dlg"].open = False
                    page.update()
                    import time; time.sleep(0.1)
                    page_users(page, state, nav)
            else:
                form_msg.color = ft.Colors.RED_400
                form_msg.value = f"Erreur : {res.status_code} — {res.text[:100]}"
                form_msg.color = ft.Colors.RED_400
                page.update()
        except Exception as ex:
            form_msg.value = str(ex)
            form_msg.color = ft.Colors.RED_400
            page.update()

    def on_create(e):
        if not all([first_name_f.value, last_name_f.value, email_f.value, password_f.value]):
            form_msg.value = "Tous les champs * sont obligatoires"
            form_msg.color = ft.Colors.RED_400
            page.update()
            return
        form_msg.value = "Création en cours..."
        form_msg.color = ft.Colors.AMBER_400
        page.update()
        page.run_thread(do_create, first_name_f.value, last_name_f.value,
                        email_f.value, password_f.value, role_dd.value)

    def open_form(e):
        form_col = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text("Nouvel utilisateur", size=16,
                                weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE_OUTLINED, icon_color=SECONDARY,
                            on_click=lambda e: (setattr(dlg_ref["dlg"], "open", False), page.update())
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Divider(color=SECONDARY + "30", height=1),
                first_name_f, last_name_f, email_f, password_f, role_dd,
                form_msg,
                btn("Créer l'utilisateur", on_create, width=380,
                    icon=ft.Icons.PERSON_ADD_OUTLINED)
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

    # Stats
    total   = len(users)
    admins  = len([u for u in users if u.get("role") == "ADMIN"])
    clients = len([u for u in users if u.get("role") == "CLIENT"])
    agents  = len([u for u in users if u.get("role") in ("SECRETARIAT", "AGENT")])

    kpis = ft.Row(controls=[
        ft.Container(
            content=ft.Column(controls=[
                ft.Text(str(total), size=24, weight=ft.FontWeight.BOLD, color=SECONDARY),
                ft.Text("Total", size=10, color=SECONDARY)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
            bgcolor=BG_CARD, border_radius=10,
            padding=ft.Padding.symmetric(horizontal=20, vertical=12),
            border=ft.Border.all(1, SECONDARY + "40"), expand=True
        ),
        ft.Container(
            content=ft.Column(controls=[
                ft.Text(str(admins), size=24, weight=ft.FontWeight.BOLD, color="#FF4444"),
                ft.Text("Admins", size=10, color=SECONDARY)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
            bgcolor=BG_CARD, border_radius=10,
            padding=ft.Padding.symmetric(horizontal=20, vertical=12),
            border=ft.Border.all(1, "#FF4444" + "40"), expand=True
        ),
        ft.Container(
            content=ft.Column(controls=[
                ft.Text(str(agents), size=24, weight=ft.FontWeight.BOLD, color="#4D7FFF"),
                ft.Text("Agents/Secrét.", size=10, color=SECONDARY)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
            bgcolor=BG_CARD, border_radius=10,
            padding=ft.Padding.symmetric(horizontal=20, vertical=12),
            border=ft.Border.all(1, "#4D7FFF" + "40"), expand=True
        ),
        ft.Container(
            content=ft.Column(controls=[
                ft.Text(str(clients), size=24, weight=ft.FontWeight.BOLD, color="#00CC77"),
                ft.Text("Clients", size=10, color=SECONDARY)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
            bgcolor=BG_CARD, border_radius=10,
            padding=ft.Padding.symmetric(horizontal=20, vertical=12),
            border=ft.Border.all(1, "#00CC77" + "40"), expand=True
        ),
    ], spacing=12)

    main_content = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Column(controls=[
                            ft.Text("Utilisateurs", size=20, weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.WHITE),
                            ft.Text(f"{total} utilisateur(s) enregistré(s)", size=12, color=SECONDARY),
                        ], spacing=2),
                        ft.Container(
                            content=ft.Row(controls=[
                                ft.Icon(ft.Icons.PERSON_ADD_OUTLINED, size=14, color=ft.Colors.WHITE),
                                ft.Text("Nouvel utilisateur", size=12, color=ft.Colors.WHITE)
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
                    controls=[user_card(u) for u in users] if users else [
                        ft.Container(
                            content=ft.Column(controls=[
                                ft.Icon(ft.Icons.PEOPLE_OUTLINED, size=40, color=SECONDARY),
                                ft.Text("Aucun utilisateur trouvé", size=13, color=SECONDARY)
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                            alignment=ft.Alignment(0, 0), padding=40
                        )
                    ],
                    spacing=8,
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
                build_sidebar(page, state, "users", nav),
                ft.Column(controls=[build_header(page, state), main_content], spacing=0, expand=True)
            ],
            spacing=0,
            expand=True
        )
    )
    page.update()
