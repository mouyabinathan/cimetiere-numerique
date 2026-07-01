import flet as ft
from config import PRIMARY, SECONDARY, BG_DARK, BG_CARD
from components.widgets import btn, card_wrapper
import services.api as api


def page_splash(page: ft.Page):
    page.overlay.clear()
    page.controls.clear()
    page.add(
        ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.ACCOUNT_BALANCE, size=80, color=PRIMARY),
                    ft.Text("CimétièrePRO", size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Text("Pointe-Noire · Municipal", size=14, color=SECONDARY),
                    ft.Container(height=30),
                    ft.ProgressRing(color=PRIMARY, width=40, height=40),
                    ft.Text("Chargement...", size=12, color=SECONDARY),
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


def page_login(page: ft.Page, on_success, on_register):
    page.overlay.clear()
    page.controls.clear()

    email_field = ft.TextField(
        label="Adresse email", prefix_icon=ft.Icons.EMAIL_OUTLINED,
        width=380, border_radius=10, border_color=SECONDARY,
        focused_border_color=PRIMARY, bgcolor=BG_DARK,
        color=ft.Colors.WHITE, label_style=ft.TextStyle(color=SECONDARY),
        cursor_color=PRIMARY,
    )
    password_field = ft.TextField(
        label="Mot de passe", prefix_icon=ft.Icons.LOCK_OUTLINED,
        password=True, can_reveal_password=True,
        width=380, border_radius=10, border_color=SECONDARY,
        focused_border_color=PRIMARY, bgcolor=BG_DARK,
        color=ft.Colors.WHITE, label_style=ft.TextStyle(color=SECONDARY),
        cursor_color=PRIMARY,
    )
    message = ft.Text("", size=13, color=ft.Colors.RED_400)
    login_btn_ref = {"control": None}

    def set_msg(text, kind="error"):
        colors = {"error": ft.Colors.RED_400, "info": ft.Colors.AMBER_400, "ok": ft.Colors.GREEN_400}
        message.color = colors.get(kind, ft.Colors.RED_400)
        message.value = text
        page.update()

    def set_loading(v):
        login_btn_ref["control"].bgcolor = SECONDARY + "50" if v else PRIMARY
        login_btn_ref["control"].on_click = None if v else on_login
        login_btn_ref["control"].content = ft.Row(
            controls=(
                [ft.ProgressRing(width=16, height=16, stroke_width=2, color=ft.Colors.WHITE)] if v
                else [ft.Icon(ft.Icons.LOGIN, color=ft.Colors.WHITE, size=16)]
            ) + [ft.Text("Connexion..." if v else "Se connecter",
                         color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, size=14)],
            alignment=ft.MainAxisAlignment.CENTER, spacing=8
        )
        page.update()

    def do_login(email, password):
        try:
            res = api.login(email, password)
            if res.status_code == 200:
                data = res.json()
                if "error" in data:
                    set_loading(False)
                    set_msg(data["error"])
                else:
                    page_mfa(page, email, on_success, on_register)
            else:
                set_loading(False)
                set_msg("Erreur de connexion au serveur")
        except Exception as ex:
            set_loading(False)
            set_msg(f"Erreur : {str(ex)}")

    def on_login(e):
        if not email_field.value or not password_field.value:
            set_msg("Veuillez remplir tous les champs")
            return
        set_loading(True)
        set_msg("Connexion en cours...", "info")
        page.run_thread(do_login, email_field.value, password_field.value)

    login_button = btn("Se connecter", on_login, width=380, icon=ft.Icons.LOGIN)
    login_btn_ref["control"] = login_button

    page.add(
        card_wrapper(
            ft.Column(
                controls=[
                    ft.Icon(ft.Icons.ACCOUNT_BALANCE, size=60, color=PRIMARY),
                    ft.Text("CimétièrePRO", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Text("Pointe-Noire · Municipal", size=13, color=SECONDARY),
                    ft.Container(height=10),
                    ft.Divider(color=SECONDARY, height=1),
                    ft.Container(height=10),
                    ft.Text("Connexion à votre espace", size=16, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                    email_field,
                    password_field,
                    message,
                    login_button,
                    ft.Container(height=5),
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.SECURITY, size=14, color=SECONDARY),
                            ft.Text("Connexion sécurisée avec MFA", size=11, color=SECONDARY)
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=6
                    ),
                    ft.Divider(color=SECONDARY + "30", height=1),
                    ft.Row(
                        controls=[
                            ft.Text("Pas encore de compte ?", size=12, color=SECONDARY),
                            ft.TextButton(
                                content=ft.Text("S'inscrire", size=12, color=PRIMARY,
                                                weight=ft.FontWeight.BOLD),
                                on_click=lambda e: on_register()
                            )
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=6
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=14
            )
        )
    )
    page.update()


def page_mfa(page: ft.Page, email: str, on_success, on_register):
    page.overlay.clear()
    page.controls.clear()

    code_field = ft.TextField(
        label="Code MFA reçu par email",
        prefix_icon=ft.Icons.VERIFIED_OUTLINED,
        width=380, border_radius=10, border_color=SECONDARY,
        focused_border_color=PRIMARY, bgcolor=BG_DARK,
        color=ft.Colors.WHITE, label_style=ft.TextStyle(color=SECONDARY),
        cursor_color=PRIMARY, text_align=ft.TextAlign.CENTER,
    )
    message = ft.Text("", size=13, color=ft.Colors.RED_400)
    verify_btn_ref = {"control": None}

    def set_msg(text, kind="error"):
        colors = {"error": ft.Colors.RED_400, "info": ft.Colors.AMBER_400, "ok": ft.Colors.GREEN_400}
        message.color = colors.get(kind, ft.Colors.RED_400)
        message.value = text
        page.update()

    def set_loading(v):
        verify_btn_ref["control"].bgcolor = SECONDARY + "50" if v else PRIMARY
        verify_btn_ref["control"].on_click = None if v else on_verify
        verify_btn_ref["control"].content = ft.Row(
            controls=(
                [ft.ProgressRing(width=16, height=16, stroke_width=2, color=ft.Colors.WHITE)] if v
                else [ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINED, color=ft.Colors.WHITE, size=16)]
            ) + [ft.Text("Vérification..." if v else "Vérifier le code",
                         color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, size=14)],
            alignment=ft.MainAxisAlignment.CENTER, spacing=8
        )
        page.update()

    def do_verify(code):
        try:
            res = api.verify_mfa(email, code)
            if res.status_code == 200:
                data = res.json()
                if "error" in data:
                    set_loading(False)
                    set_msg(data["error"])
                else:
                    on_success(data)
            else:
                set_loading(False)
                set_msg("Code invalide ou expiré")
        except Exception as ex:
            set_loading(False)
            set_msg(f"Erreur : {str(ex)}")

    def on_verify(e):
        if not code_field.value:
            set_msg("Veuillez entrer le code reçu")
            return
        set_loading(True)
        set_msg("Vérification en cours...", "info")
        page.run_thread(do_verify, code_field.value)

    verify_button = btn("Vérifier le code", on_verify, width=380, icon=ft.Icons.CHECK_CIRCLE_OUTLINED)
    verify_btn_ref["control"] = verify_button

    page.add(
        card_wrapper(
            ft.Column(
                controls=[
                    ft.Icon(ft.Icons.SHIELD_OUTLINED, size=60, color=PRIMARY),
                    ft.Text("Vérification MFA", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Text(f"Code envoyé à {email}", size=12, color=SECONDARY),
                    ft.Container(height=5),
                    ft.Divider(color=SECONDARY, height=1),
                    ft.Container(height=5),
                    code_field,
                    message,
                    verify_button,
                    ft.Container(height=5),
                    ft.TextButton(
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.ARROW_BACK, size=14, color=SECONDARY),
                                ft.Text("Retour à la connexion", size=12, color=SECONDARY)
                            ],
                            spacing=6
                        ),
                        on_click=lambda e: page_login(page, on_success, on_register)
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=14
            )
        )
    )
    page.update()


def page_register(page: ft.Page, on_login_click):
    page.overlay.clear()
    page.controls.clear()

    nom_field = ft.TextField(
        label="Nom", prefix_icon=ft.Icons.PERSON_OUTLINED,
        width=380, border_radius=10, border_color=SECONDARY,
        focused_border_color=PRIMARY, bgcolor=BG_DARK,
        color=ft.Colors.WHITE, label_style=ft.TextStyle(color=SECONDARY),
        cursor_color=PRIMARY,
    )
    prenom_field = ft.TextField(
        label="Prénom", prefix_icon=ft.Icons.PERSON_OUTLINED,
        width=380, border_radius=10, border_color=SECONDARY,
        focused_border_color=PRIMARY, bgcolor=BG_DARK,
        color=ft.Colors.WHITE, label_style=ft.TextStyle(color=SECONDARY),
        cursor_color=PRIMARY,
    )
    email_field = ft.TextField(
        label="Adresse email", prefix_icon=ft.Icons.EMAIL_OUTLINED,
        width=380, border_radius=10, border_color=SECONDARY,
        focused_border_color=PRIMARY, bgcolor=BG_DARK,
        color=ft.Colors.WHITE, label_style=ft.TextStyle(color=SECONDARY),
        cursor_color=PRIMARY,
    )
    phone_field = ft.TextField(
        label="Téléphone (optionnel)", prefix_icon=ft.Icons.PHONE_OUTLINED,
        width=380, border_radius=10, border_color=SECONDARY,
        focused_border_color=PRIMARY, bgcolor=BG_DARK,
        color=ft.Colors.WHITE, label_style=ft.TextStyle(color=SECONDARY),
        cursor_color=PRIMARY,
    )
    password_field = ft.TextField(
        label="Mot de passe", prefix_icon=ft.Icons.LOCK_OUTLINED,
        password=True, can_reveal_password=True,
        width=380, border_radius=10, border_color=SECONDARY,
        focused_border_color=PRIMARY, bgcolor=BG_DARK,
        color=ft.Colors.WHITE, label_style=ft.TextStyle(color=SECONDARY),
        cursor_color=PRIMARY,
    )
    confirm_field = ft.TextField(
        label="Confirmer le mot de passe", prefix_icon=ft.Icons.LOCK_OUTLINED,
        password=True, can_reveal_password=True,
        width=380, border_radius=10, border_color=SECONDARY,
        focused_border_color=PRIMARY, bgcolor=BG_DARK,
        color=ft.Colors.WHITE, label_style=ft.TextStyle(color=SECONDARY),
        cursor_color=PRIMARY,
    )
    message = ft.Text("", size=13, color=ft.Colors.RED_400)
    reg_btn_ref = {"control": None}

    def set_msg(text, kind="error"):
        colors = {"error": ft.Colors.RED_400, "info": ft.Colors.AMBER_400, "ok": ft.Colors.GREEN_400}
        message.color = colors.get(kind, ft.Colors.RED_400)
        message.value = text
        page.update()

    def set_loading(v):
        reg_btn_ref["control"].bgcolor = SECONDARY + "50" if v else PRIMARY
        reg_btn_ref["control"].on_click = None if v else on_register
        reg_btn_ref["control"].content = ft.Row(
            controls=(
                [ft.ProgressRing(width=16, height=16, stroke_width=2, color=ft.Colors.WHITE)] if v
                else [ft.Icon(ft.Icons.PERSON_ADD_OUTLINED, color=ft.Colors.WHITE, size=16)]
            ) + [ft.Text("Inscription..." if v else "Créer mon compte",
                         color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, size=14)],
            alignment=ft.MainAxisAlignment.CENTER, spacing=8
        )
        page.update()

    def do_register():
        try:
            res = api.register_client({
                "email": email_field.value.strip(),
                "password": password_field.value,
                "first_name": prenom_field.value.strip(),
                "last_name": nom_field.value.strip(),
                "phone": phone_field.value.strip() if phone_field.value else "",
            })
            if res.status_code == 200:
                data = res.json()
                if "error" in data:
                    set_loading(False)
                    set_msg(data["error"])
                else:
                    set_loading(False)
                    set_msg("✅ Compte créé ! Vous pouvez vous connecter.", "ok")
                    import time
                    time.sleep(1.5)
                    on_login_click()
            else:
                set_loading(False)
                try:
                    err = res.json()
                    set_msg(str(err))
                except Exception:
                    set_msg(f"Erreur serveur : {res.status_code}")
        except Exception as ex:
            set_loading(False)
            set_msg(f"Erreur : {str(ex)}")

    def on_register(e=None):
        if not all([nom_field.value, prenom_field.value, email_field.value, password_field.value]):
            set_msg("Veuillez remplir tous les champs obligatoires")
            return
        if password_field.value != confirm_field.value:
            set_msg("Les mots de passe ne correspondent pas")
            return
        if len(password_field.value) < 6:
            set_msg("Le mot de passe doit faire au moins 6 caractères")
            return
        set_loading(True)
        set_msg("Inscription en cours...", "info")
        page.run_thread(do_register)

    reg_button = btn("Créer mon compte", on_register, width=380, icon=ft.Icons.PERSON_ADD_OUTLINED)
    reg_btn_ref["control"] = reg_button

    page.add(
        card_wrapper(
            ft.Column(
                controls=[
                    ft.Icon(ft.Icons.PERSON_ADD_OUTLINED, size=60, color=PRIMARY),
                    ft.Text("Créer un compte", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Text("Portail citoyen — Pointe-Noire", size=12, color=SECONDARY),
                    ft.Container(height=5),
                    ft.Divider(color=SECONDARY, height=1),
                    ft.Container(height=5),
                    ft.Row(
                        controls=[prenom_field],
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    nom_field,
                    email_field,
                    phone_field,
                    password_field,
                    confirm_field,
                    message,
                    reg_button,
                    ft.Divider(color=SECONDARY + "30", height=1),
                    ft.Row(
                        controls=[
                            ft.Text("Déjà un compte ?", size=12, color=SECONDARY),
                            ft.TextButton(
                                content=ft.Text("Se connecter", size=12, color=PRIMARY,
                                                weight=ft.FontWeight.BOLD),
                                on_click=lambda e: on_login_click()
                            )
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=6
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
                scroll=ft.ScrollMode.AUTO,
            ),
            width=520
        )
    )
    page.update()
