import httpx
from config import API_URL

client = httpx.Client(timeout=120.0)

def get_headers(token):
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}

# ---- AUTH ----
def login(email, password):
    return client.post(f"{API_URL}/users/login", json={"email": email, "password": password})

def verify_mfa(email, code):
    return client.post(f"{API_URL}/users/verify-mfa", json={"email": email, "code": code})

# ---- TERRAIN ----
def get_carte(token):
    if not token:
        return None
    return client.get(f"{API_URL}/terrain/carte", headers=get_headers(token))

def get_carte_stats(token):
    if not token:
        return None
    return client.get(f"{API_URL}/terrain/carte/stats", headers=get_headers(token))

def get_caveaux(token):
    if not token:
        return None
    return client.get(f"{API_URL}/terrain/caveaux", headers=get_headers(token))

def get_zones(token):
    if not token:
        return None
    return client.get(f"{API_URL}/terrain/zones", headers=get_headers(token))

def get_blocs(token):
    if not token:
        return None
    return client.get(f"{API_URL}/terrain/blocs", headers=get_headers(token))

def create_zone(token, data):
    if not token:
        return None
    return client.post(f"{API_URL}/terrain/zones", headers=get_headers(token), json=data)

def create_bloc(token, data):
    if not token:
        return None
    return client.post(f"{API_URL}/terrain/blocs", headers=get_headers(token), json=data)

def create_caveau(token, data):
    if not token:
        return None
    return client.post(f"{API_URL}/terrain/caveaux", headers=get_headers(token), json=data)

# ---- RESERVATIONS ----
def get_reservations(token):
    if not token:
        return None
    return client.get(f"{API_URL}/reservations/", headers=get_headers(token))

def create_reservation(token, data):
    if not token:
        return None
    return client.post(f"{API_URL}/reservations/", headers=get_headers(token), json=data)

def valider_reservation(token, reservation_id, statut):
    if not token:
        return None
    return client.put(
        f"{API_URL}/reservations/{reservation_id}/valider",
        headers=get_headers(token),
        json={"statut": statut}
    )

# ---- CONCESSIONS ----
def get_concessions(token):
    if not token:
        return None
    return client.get(f"{API_URL}/reservations/concessions/list", headers=get_headers(token))

def create_concession(token, data):
    if not token:
        return None
    return client.post(f"{API_URL}/reservations/concessions/create", headers=get_headers(token), json=data)

def resilier_concession(token, concession_id):
    if not token:
        return None
    return client.put(f"{API_URL}/reservations/concessions/{concession_id}/resilier", headers=get_headers(token))

# ---- EXHUMATIONS ----
def get_exhumations(token):
    if not token:
        return None
    return client.get(f"{API_URL}/reservations/exhumations/list", headers=get_headers(token))

def create_exhumation(token, data):
    if not token:
        return None
    return client.post(f"{API_URL}/reservations/exhumations/create", headers=get_headers(token), json=data)

def valider_exhumation(token, exhumation_id, data):
    if not token:
        return None
    return client.put(
        f"{API_URL}/reservations/exhumations/{exhumation_id}/valider",
        headers=get_headers(token),
        json=data
    )

# ---- FACTURATION ----
def get_factures(token):
    if not token:
        return None
    return client.get(f"{API_URL}/facturation/factures", headers=get_headers(token))

def create_facture(token, reservation_id, montant):
    if not token:
        return None
    return client.post(
        f"{API_URL}/facturation/factures",
        headers=get_headers(token),
        params={"reservation_id": reservation_id, "montant": montant}
    )

def create_paiement(token, data):
    if not token:
        return None
    return client.post(f"{API_URL}/facturation/paiements", headers=get_headers(token), json=data)

def get_facture_pdf(token, facture_id):
    if not token:
        return None
    return client.get(f"{API_URL}/facturation/factures/{facture_id}/pdf", headers=get_headers(token))

# ---- REPORTING ----
def get_reporting_dashboard(token):
    if not token:
        return None
    return client.get(f"{API_URL}/reporting/dashboard", headers=get_headers(token))

def get_stats_par_bloc(token):
    if not token:
        return None
    return client.get(f"{API_URL}/reporting/stats-par-bloc", headers=get_headers(token))

def export_csv(token):
    if not token:
        return None
    return client.get(f"{API_URL}/reporting/export/csv", headers=get_headers(token))

def export_excel(token):
    if not token:
        return None
    return client.get(f"{API_URL}/reporting/export/excel", headers=get_headers(token))

# ---- USERS ----
def get_users(token):
    if not token:
        return None
    return client.get(f"{API_URL}/users/list", headers=get_headers(token))

def create_user(token, data):
    if not token:
        return None
    return client.post(f"{API_URL}/users/create", headers=get_headers(token), json=data)

def register_client(data):
    return client.post(f"{API_URL}/users/register", json=data)