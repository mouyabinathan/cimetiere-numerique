API_URL = "https://cimetiere-numerique.onrender.com"
LOGIN_URL = f"{API_URL}/api/users/login"
PRIMARY   = "#0033FF"
SECONDARY = "#977DFF"
DARK      = "#00033D"
BG_DARK   = "#0A0A1A"
BG_CARD   = "#0D0D20"

STATUT_COLORS = {
    "DISPONIBLE":    "#00CC77",
    "OCCUPE":        "#FF4444",
    "RESERVE":       "#FF9922",
    "INEXPLOITABLE": "#555555",
}
STATUT_LABELS = {
    "DISPONIBLE":    "Disponible",
    "OCCUPE":        "Occupé",
    "RESERVE":       "Réservé",
    "INEXPLOITABLE": "Inexploitable",
}

RESA_STATUT_COLORS = {
    "EN_ATTENTE": "#FF9922",
    "VALIDEE":    "#00CC77",
    "REFUSEE":    "#FF4444",
    "ANNULEE":    "#555555",
}
RESA_STATUT_LABELS = {
    "EN_ATTENTE": "En attente",
    "VALIDEE":    "Validée",
    "REFUSEE":    "Refusée",
    "ANNULEE":    "Annulée",
}

CONC_STATUT_COLORS = {
    "ACTIVE":   "#00CC77",
    "EXPIREE":  "#FF9922",
    "RESILIEE": "#FF4444",
}
CONC_STATUT_LABELS = {
    "ACTIVE":   "Active",
    "EXPIREE":  "Expirée",
    "RESILIEE": "Résiliée",
}
CONC_TYPE_LABELS = {
    "TEMPORAIRE":  "Temporaire",
    "PERPETUELLE": "Perpétuelle",
}

FACT_STATUT_COLORS = {
    "EN_ATTENTE": "#FF9922",
    "PAYEE":      "#00CC77",
    "ANNULEE":    "#555555",
}
FACT_STATUT_LABELS = {
    "EN_ATTENTE": "En attente",
    "PAYEE":      "Payée",
    "ANNULEE":    "Annulée",
}
