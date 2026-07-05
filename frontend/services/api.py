import httpx
from config import API_URL

client = httpx.Client(timeout=30.0)


def get_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ---- AUTH ----
def login(email: str, password: str):
    return client.post(f"{API_URL}/users/login", json={"email": email, "password": password})

def verify_mfa(email: str, code: str):
    return client.post(f"{API_URL}/users/verify-mfa", json={"email": email, "code": code})


# ---- TERRAIN ----
def get_carte(token):
    return client.get(f"{API_URL}/terrain/carte", headers=get_headers(token))

def get_carte_stats(token):
    return client.get(f"{API_URL}/terrain/carte/stats", headers=get_headers(token))

def get_caveaux(token):
    return client.get(f"{API_URL}/terrain/caveaux", headers=get_headers(token))

def get_zones(token):
    return client.get(f"{API_URL}/terrain/zones", headers=get_headers(token))

def get_blocs(token):
    return client.get(f"{API_URL}/terrain/blocs", headers=get_headers(token))

def create_zone(token, data: dict):
    return client.post(f"{API_URL}/terrain/zones", headers=get_headers(token), json=data)

def create_bloc(token, data: dict):
    return client.post(f"{API_URL}/terrain/blocs", headers=get_headers(token), json=data)

def create_caveau(token, data: dict):
    return client.post(f"{API_URL}/terrain/caveaux", headers=get_headers(token), json=data)


# ---- RESERVATIONS ----
def get_reservations(token):
    return client.get(f"{API_URL}/reservations/", headers=get_headers(token))

def create_reservation(token, data: dict):
    return client.post(f"{API_URL}/reservations/", headers=get_headers(token), json=data)

def valider_reservation(token, reservation_id: int, statut: str):
    return client.put(
        f"{API_URL}/reservations/{reservation_id}/valider",
        headers=get_headers(token),
        json={"statut": statut}
    )


# ---- CONCESSIONS ----
def get_concessions(token):
    return client.get(f"{API_URL}/reservations/concessions/list", headers=get_headers(token))

def create_concession(token, data: dict):
    return client.post(f"{API_URL}/reservations/concessions/create", headers=get_headers(token), json=data)

def resilier_concession(token, concession_id: int):
    return client.put(f"{API_URL}/reservations/concessions/{concession_id}/resilier", headers=get_headers(token))


# ---- EXHUMATIONS ----
def get_exhumations(token):
    return client.get(f"{API_URL}/reservations/exhumations/list", headers=get_headers(token))

def create_exhumation(token, data: dict):
    return client.post(f"{API_URL}/reservations/exhumations/create", headers=get_headers(token), json=data)

def valider_exhumation(token, exhumation_id: int, data: dict):
    return client.put(
        f"{API_URL}/reservations/exhumations/{exhumation_id}/valider",
        headers=get_headers(token),
        json=data
    )


# ---- FACTURATION ----
def get_factures(token):
    return client.get(f"{API_URL}/facturation/factures", headers=get_headers(token))

def create_facture(token, reservation_id: int, montant: float):
    return client.post(
        f"{API_URL}/facturation/factures",
        headers=get_headers(token),
        params={"reservation_id": reservation_id, "montant": montant}
    )

def create_paiement(token, data: dict):
    return client.post(f"{API_URL}/facturation/paiements", headers=get_headers(token), json=data)

def get_facture_pdf(token, facture_id: int):
    return client.get(f"{API_URL}/facturation/factures/{facture_id}/pdf", headers=get_headers(token))


# ---- REPORTING ----
def get_reporting_dashboard(token):
    return client.get(f"{API_URL}/reporting/dashboard", headers=get_headers(token))

def get_stats_par_bloc(token):
    return client.get(f"{API_URL}/reporting/stats-par-bloc", headers=get_headers(token))

def export_csv(token):
    return client.get(f"{API_URL}/reporting/export/csv", headers=get_headers(token))

def export_excel(token):
    return client.get(f"{API_URL}/reporting/export/excel", headers=get_headers(token))


# ---- USERS ----
def get_users(token):
    return client.get(f"{API_URL}/users/list", headers=get_headers(token))

def create_user(token, data: dict):
    return client.post(f"{API_URL}/users/create", headers=get_headers(token), json=data)

def register_client(data: dict):
    return client.post(f"{API_URL}/users/register", json=data)