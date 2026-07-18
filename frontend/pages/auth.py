import flet as ft
from config import PRIMARY, SECONDARY, BG_DARK
from utils.responsivite import is_mobile, get_responsive_padding

def page_splash(page: ft.Page):
    """Splash screen responsive."""
    page.controls.clear()
    mobile = is_mobile(page)
    
    page.add(
        ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("⚰️", size=48 if not mobile else 36),
                    ft.Text(
                        "CimétièrePRO",
                        size=24 if not mobile else 18,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE
                    ),
                    ft.ProgressRing(color=PRIMARY, width=30, height=30),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=12,
            ),
            alignment=ft.Alignment(0, 0),
            expand=True,
            bgcolor=BG_DARK,
        )
    )
    page.update()

def page_login(page: ft.Page, on_success, on_register_click):
    """Page de login responsive."""
    page.controls.clear()
    mobile = is_mobile(page)
    
    # Champs
    email_field = ft.TextField(
        hint_text="Email",
        prefix_icon=ft.Icons.EMAIL_OUTLINED,
        width=300 if not mobile else 280,
        height=44,
    )
    
    password_field = ft.TextField(
        hint_text="Mot de passe",
        prefix_icon=ft.Icons.LOCK_OUTLINED,
        password=True,
        can_reveal_password=True,
        width=300 if not mobile else 280,
        height=44,
    )
    
    def on_login_click(e):
        # Logique de login
        on_success({"token": "fake", "role": "admin", "nom": "Admin", "email": "admin@test.com"})
    
    page.add(
        ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(height=40),
                    ft.Text("🔑", size=40 if not mobile else 32),
                    ft.Text(
                        "Connexion",
                        size=24 if not mobile else 20,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE,
                    ),
                    ft.Text(
                        "CimétièrePRO — Pointe-Noire",
                        size=13 if not mobile else 11,
                        color=SECONDARY,
                    ),
                    ft.Container(height=20),
                    email_field,
                    password_field,
                    ft.Container(
                        content=ft.ElevatedButton(
                            "Se connecter",
                            on_click=on_login_click,
                            bgcolor=PRIMARY,
                            color=ft.Colors.WHITE,
                            width=300 if not mobile else 280,
                            height=44,
                        ),
                        padding=ft.Padding.only(top=10),
                    ),
                    ft.Row(
                        controls=[
                            ft.Text("Pas de compte ?", color=SECONDARY),
                            ft.TextButton(
                                "S'inscrire",
                                on_click=on_register_click,
                                style=ft.ButtonStyle(color=PRIMARY),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
            ),
            alignment=ft.Alignment(0, 0),
            expand=True,
            bgcolor=BG_DARK,
        )
    )
    page.update()

def page_register(page: ft.Page, on_register_success):
    """Page d'inscription responsive."""
    page.controls.clear()
    mobile = is_mobile(page)
    
    # Similaire à login mais avec plus de champs
    page.add(
        ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("📝", size=40 if not mobile else 32),
                    ft.Text(
                        "Inscription",
                        size=24 if not mobile else 20,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE,
                    ),
                    ft.TextField(
                        hint_text="Nom complet",
                        width=300 if not mobile else 280,
                        height=44,
                    ),
                    ft.TextField(
                        hint_text="Email",
                        width=300 if not mobile else 280,
                        height=44,
                    ),
                    ft.TextField(
                        hint_text="Mot de passe",
                        password=True,
                        width=300 if not mobile else 280,
                        height=44,
                    ),
                    ft.Container(
                        content=ft.ElevatedButton(
                            "S'inscrire",
                            on_click=lambda e: on_register_success(),
                            bgcolor=PRIMARY,
                            color=ft.Colors.WHITE,
                            width=300 if not mobile else 280,
                            height=44,
                        ),
                        padding=ft.Padding.only(top=10),
                    ),
                    ft.TextButton(
                        "Déjà un compte ? Se connecter",
                        on_click=lambda e: on_register_success(),
                        style=ft.ButtonStyle(color=PRIMARY),
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
            ),
            alignment=ft.Alignment(0, 0),
            expand=True,
            bgcolor=BG_DARK,
        )
    )
    page.update()