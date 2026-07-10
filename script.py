from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter

# ============ 1. Configuration ============
doc = SimpleDocTemplate(
    "Guide_Utilisateur_CimetierePRO.pdf",
    pagesize=A4,
    rightMargin=20*mm,
    leftMargin=20*mm,
    topMargin=20*mm,
    bottomMargin=20*mm,
)

styles = getSampleStyleSheet()
style_normal = styles["Normal"]
style_heading1 = styles["Heading1"]
style_heading2 = styles["Heading2"]
style_heading3 = styles["Heading3"]

# Personnalisation des styles
style_heading1.fontSize = 18
style_heading1.spaceAfter = 10
style_heading2.fontSize = 14
style_heading2.spaceAfter = 8
style_heading3.fontSize = 12
style_heading3.spaceAfter = 6
style_normal.fontSize = 10
style_normal.leading = 14

# ============ 2. Contenu ============
story = []

# --- Titre principal ---
story.append(Paragraph("📘 GUIDE D'UTILISATION", style_heading1))
story.append(Paragraph("CimetièrePRO - Gestion Funéraire", style_heading2))
story.append(Paragraph("Pointe-Noire, Congo", style_normal))
story.append(Spacer(1, 12*mm))

# --- 1. Présentation ---
story.append(Paragraph("1. PRÉSENTATION GÉNÉRALE", style_heading1))
story.append(Paragraph("""
CimetièrePRO est une application web de gestion complète des espaces funéraires.
Elle permet la gestion cartographique des caveaux, les réservations, les concessions,
les exhumations, la facturation et le reporting.
""", style_normal))
story.append(Paragraph("Accès : https://cimetiere-numerique-1.onrender.com", style_normal))
story.append(Spacer(1, 6*mm))

# --- 2. Connexion ---
story.append(Paragraph("2. PREMIÈRE CONNEXION", style_heading1))
story.append(Paragraph("2.1 Création d'un compte", style_heading2))
story.append(Paragraph("""
- Clique sur 'S'inscrire'
- Remplis le formulaire (Nom, Prénom, Email, Mot de passe, Téléphone)
- Clique sur 'Créer mon compte'
""", style_normal))
story.append(Paragraph("2.2 Connexion", style_heading2))
story.append(Paragraph("""
- Saisis ton email et mot de passe
- Clique sur 'Se connecter'
- Si MFA activé, entre le code reçu par email
""", style_normal))
story.append(Spacer(1, 6*mm))

# --- 3. Interface ---
story.append(Paragraph("3. INTERFACE PRINCIPALE", style_heading1))
story.append(Paragraph("""
Le menu latéral donne accès à toutes les fonctionnalités :
Tableau de bord, Cartographie, Réservations, Concessions, Facturation,
Exhumations, Reporting, Utilisateurs (admin) et Paramètres.
""", style_normal))
story.append(Spacer(1, 6*mm))

# --- 4. Terrain ---
story.append(Paragraph("4. GESTION DU TERRAIN (PARAMÈTRES)", style_heading1))
story.append(Paragraph("4.1 Créer une Zone", style_heading2))
story.append(Paragraph("""
Aller dans Paramètres → onglet Zones.
Remplir : Nom, Description (optionnel), Exploitable (cocher)
Cliquer sur 'Créer la zone'
""", style_normal))
story.append(Paragraph("4.2 Créer un Bloc", style_heading2))
story.append(Paragraph("""
Aller dans Paramètres → onglet Blocs.
Sélectionner la Zone parente.
Saisir le Nom du bloc.
Cliquer sur 'Créer le bloc'
""", style_normal))
story.append(Paragraph("4.3 Créer un Caveau", style_heading2))
story.append(Paragraph("""
Aller dans Paramètres → onglet Caveaux.
Sélectionner le Bloc.
Saisir : Numéro, Statut initial, coordonnées GPS (optionnel), Longueur/Largeur.
Cliquer sur 'Créer le caveau'
""", style_normal))
story.append(Spacer(1, 6*mm))

# --- 5. Réservations ---
story.append(Paragraph("5. RÉSERVATIONS", style_heading1))
story.append(Paragraph("5.1 Effectuer une réservation", style_heading2))
story.append(Paragraph("""
Aller dans Réservations.
Sélectionner un caveau disponible sur la carte.
Remplir : Nom, Prénom du défunt, Date de décès, Notes (optionnel).
Soumettre la demande.
""", style_normal))
story.append(Paragraph("5.2 Valider une réservation (admin/secretariat)", style_heading2))
story.append(Paragraph("""
Aller dans Réservations → liste des demandes.
Cliquer sur une demande en attente (statut orange).
Cliquer sur 'Valider' ou 'Refuser'.
Une facture est générée automatiquement.
""", style_normal))
story.append(Spacer(1, 6*mm))

# --- 6. Concessions ---
story.append(Paragraph("6. CONCESSIONS", style_heading1))
story.append(Paragraph("6.1 Créer une concession", style_heading2))
story.append(Paragraph("""
Aller dans Concessions.
Cliquer sur 'Nouvelle concession'.
Remplir : Réservation associée, Type (Temporaire/Perpétuelle),
Date de début, Durée (années), Montant.
Valider.
""", style_normal))
story.append(Spacer(1, 6*mm))

# --- 7. Facturation ---
story.append(Paragraph("7. FACTURATION", style_heading1))
story.append(Paragraph("""
Génération automatique de facture après validation d'une réservation.

Pour enregistrer un paiement :
Aller dans Facturation → sélectionner une facture en attente.
Cliquer sur 'Enregistrer un paiement'.
Remplir : Canal, Montant, Référence (optionnel).
Valider.
""", style_normal))
story.append(Paragraph("Téléchargement PDF : Cliquer sur 'Télécharger PDF' sur la facture.", style_normal))
story.append(Spacer(1, 6*mm))

# --- 8. Exhumations ---
story.append(Paragraph("8. EXHUMATIONS", style_heading1))
story.append(Paragraph("""
Aller dans Exhumations → 'Nouvelle demande'.
Remplir : Réservation associée, Motif, Date souhaitée.
Valider.

Validation (admin) : Vérifier la demande → 'Valider' ou 'Refuser'.
""", style_normal))
story.append(Spacer(1, 6*mm))

# --- 9. Reporting ---
story.append(Paragraph("9. REPORTING", style_heading1))
story.append(Paragraph("""
Visualiser les statistiques : taux d'occupation, revenus, saturation.
Exporter les données en CSV ou Excel.
""", style_normal))
story.append(Spacer(1, 6*mm))

# --- 10. Utilisateurs ---
story.append(Paragraph("10. GESTION DES UTILISATEURS (ADMIN)", style_heading1))
story.append(Paragraph("""
Aller dans Utilisateurs → 'Nouvel utilisateur'.
Remplir : Email, Nom, Prénom, Mot de passe, Rôle (ADMIN, SECRETARIAT, AGENT, CLIENT).
Valider.
""", style_normal))
story.append(Spacer(1, 6*mm))

# --- 11. Bonnes pratiques ---
story.append(Paragraph("11. BONNES PRATIQUES", style_heading1))
story.append(Paragraph("""
- Change ton mot de passe régulièrement
- Ne partage pas tes identifiants
- Vérifie les coordonnées GPS avant validation
- Relis les informations avant de valider une réservation
""", style_normal))
story.append(Spacer(1, 6*mm))

# --- 12. Dépannage ---
story.append(Paragraph("12. DÉPANNAGE", style_heading1))
story.append(Paragraph("""
Problème : 'Erreur de connexion au serveur'
→ Vérifie ton accès internet, recharge la page.

Problème : 'Code MFA non reçu'
→ Vérifie tes spams, vérifie l'email, demande un nouveau code.

Problème : Page blanche
→ Vide le cache du navigateur, utilise un navigateur récent.
""", style_normal))
story.append(Spacer(1, 6*mm))

# --- 13. Contact ---
story.append(Paragraph("13. CONTACT ET SUPPORT", style_heading1))
story.append(Paragraph("""
Email : bienvenupc1@gmail.com
Téléphone : 06 910 3715 / 05 322 1067
Site : https://cimetiere-numerique.onrender.com
""", style_normal))
story.append(Spacer(1, 6*mm))

# --- 14. Glossaire ---
story.append(Paragraph("14. GLOSSAIRE", style_heading1))
story.append(Paragraph("""
Caveau : Emplacement funéraire (tombe, columbarium)
Concession : Contrat d'occupation d'un caveau
Exhumation : Extraction de restes d'un caveau
MFA : Authentification à double facteur
""", style_normal))
story.append(Spacer(1, 6*mm))

story.append(Paragraph("FIN DU GUIDE - CimetièrePRO - Pointe-Noire, Congo", style_normal))

# ============ 3. Construction du PDF ============
doc.build(story)
print("✅ PDF généré : Guide_Utilisateur_CimetierePRO.pdf")