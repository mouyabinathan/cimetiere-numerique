import flet as ft
from config import PRIMARY, SECONDARY, BG_CARD, BG_DARK

def create_drawer(page: ft.Page, state: dict, nav_func, is_mobile: bool):
    """Crée et retourne un NavigationDrawer adapté à votre application."""
    
    def on_drawer_change(e):
        index = e.control.selected_index
        routes = ["dashboard", "carte", "reservations", "concessions", 
                  "facturation", "exhumations", "reporting", "parametres", "users"]
        if index < len(routes):
            nav_func(routes[index])
            if is_mobile:
                page.close_drawer()  # Utiliser close_drawer au lieu de close

    drawer = ft.NavigationDrawer(
        on_change=on_drawer_change,
        controls=[
            ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Text(
                            state.get("user_initials", "?"),
                            size=28,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE
                        ),
                        width=60,
                        height=60,
                        bgcolor=PRIMARY,
                        border_radius=30,
                        alignment=ft.Alignment(0, 0),
                    ),
                    ft.Text(
                        state.get("user_nom", "Utilisateur"),
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE,
                    ),
                    ft.Text(
                        state.get("user_email", "email@exemple.com"),
                        size=12,
                        color=SECONDARY,
                    ),
                ]),
                padding=ft.Padding.symmetric(vertical=20, horizontal=16),
                bgcolor=BG_DARK,
            ),
            ft.Divider(height=1, thickness=1, color=SECONDARY + "30"),
            ft.NavigationDrawerDestination(
                icon=ft.icons.DASHBOARD_OUTLINED,
                selected_icon=ft.icons.DASHBOARD,
                label="Tableau de bord",
            ),
            ft.NavigationDrawerDestination(
                icon=ft.icons.MAP_OUTLINED,
                selected_icon=ft.icons.MAP,
                label="Cartographie",
            ),
            ft.NavigationDrawerDestination(
                icon=ft.icons.BOOKMARK_OUTLINED,
                selected_icon=ft.icons.BOOKMARK,
                label="Réservations",
            ),
            ft.NavigationDrawerDestination(
                icon=ft.icons.LOCATION_CITY_OUTLINED,
                selected_icon=ft.icons.LOCATION_CITY,
                label="Concessions",
            ),
            ft.NavigationDrawerDestination(
                icon=ft.icons.PAYMENT_OUTLINED,
                selected_icon=ft.icons.PAYMENT,
                label="Facturation",
            ),
            ft.NavigationDrawerDestination(
                icon=ft.icons.HISTORY_OUTLINED,
                selected_icon=ft.icons.HISTORY,
                label="Exhumations",
            ),
            ft.NavigationDrawerDestination(
                icon=ft.icons.ANALYTICS_OUTLINED,
                selected_icon=ft.icons.ANALYTICS,
                label="Reporting",
            ),
            ft.Divider(height=1, thickness=1, color=SECONDARY + "30"),
            ft.NavigationDrawerDestination(
                icon=ft.icons.SETTINGS_OUTLINED,
                selected_icon=ft.icons.SETTINGS,
                label="Paramètres",
            ),
            ft.NavigationDrawerDestination(
                icon=ft.icons.PEOPLE_OUTLINED,
                selected_icon=ft.icons.PEOPLE,
                label="Utilisateurs",
            ),
            ft.Divider(height=1, thickness=1, color=SECONDARY + "30"),
            ft.Container(
                content=ft.ListTile(
                    leading=ft.Icon(ft.icons.LOGOUT, color=ft.Colors.RED_400),
                    title=ft.Text("Déconnexion", color=ft.Colors.RED_400),
                    on_click=lambda e: nav_func("logout"),
                ),
                padding=ft.Padding.symmetric(vertical=4, horizontal=0),
            ),
        ],
    )
    
    page.drawer = drawer
    return drawer

def get_sidebar_menu(page: ft.Page, state: dict, nav_func, is_mobile: bool):
    """Retourne le menu latéral pour desktop."""
    if is_mobile:
        return None
    
    active_route = "dashboard"
    
    menu_items = [
        (ft.icons.DASHBOARD_OUTLINED, "Tableau de bord", "dashboard"),
        (ft.icons.MAP_OUTLINED, "Cartographie", "carte"),
        (ft.icons.BOOKMARK_OUTLINED, "Réservations", "reservations"),
        (ft.icons.LOCATION_CITY_OUTLINED, "Concessions", "concessions"),
        (ft.icons.PAYMENT_OUTLINED, "Facturation", "facturation"),
        (ft.icons.HISTORY_OUTLINED, "Exhumations", "exhumations"),
        (ft.icons.ANALYTICS_OUTLINED, "Reporting", "reporting"),
        (ft.icons.SETTINGS_OUTLINED, "Paramètres", "parametres"),
        (ft.icons.PEOPLE_OUTLINED, "Utilisateurs", "users"),
    ]
    
    return ft.Container(
        content=ft.Column([
            ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Text(
                            state.get("user_initials", "?"),
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE,
                        ),
                        width=50,
                        height=50,
                        bgcolor=PRIMARY,
                        border_radius=25,
                        alignment=ft.Alignment(0, 0),
                    ),
                    ft.Text(
                        state.get("user_nom", "Utilisateur"),
                        size=14,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE,
                    ),
                    ft.Text(
                        state.get("user_email", ""),
                        size=11,
                        color=SECONDARY,
                    ),
                ]),
                padding=ft.Padding.symmetric(vertical=16, horizontal=12),
                bgcolor=BG_DARK,
            ),
            ft.Divider(height=1, color=SECONDARY + "30"),
            ft.Column([
                ft.Container(
                    content=ft.ListTile(
                        leading=ft.Icon(icon, color=PRIMARY if route == active_route else SECONDARY),
                        title=ft.Text(
                            label,
                            color=ft.Colors.WHITE if route == active_route else SECONDARY,
                            weight=ft.FontWeight.BOLD if route == active_route else ft.FontWeight.NORMAL,
                        ),
                        on_click=lambda e, r=route: nav_func(r),
                        bgcolor=PRIMARY + "30" if route == active_route else ft.Colors.TRANSPARENT,
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                    padding=ft.Padding.symmetric(horizontal=8, vertical=2),
                )
                for icon, label, route in menu_items
            ]),
            ft.Divider(height=1, color=SECONDARY + "30"),
            ft.Container(
                content=ft.ListTile(
                    leading=ft.Icon(ft.icons.LOGOUT, color=ft.Colors.RED_400),
                    title=ft.Text("Déconnexion", color=ft.Colors.RED_400),
                    on_click=lambda e: nav_func("logout"),
                ),
                padding=ft.Padding.symmetric(horizontal=8, vertical=8),
            ),
        ]),
        width=240,
        bgcolor=BG_CARD,
        padding=0,
    )