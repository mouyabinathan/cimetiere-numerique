from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io

def generer_facture_pdf(facture):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Titre
    # En-tête cimetière
    elements.append(Paragraph("CIMETIERE MUNICIPAL DE POINTE-NOIRE", styles['Title']))
    elements.append(Paragraph("Avenue de l'Indépendance - Pointe-Noire, Congo", styles['Normal']))
    elements.append(Paragraph("Tél: +242 06 910 3715", styles['Normal']))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("FACTURE", styles['Title']))
    elements.append(Spacer(1, 20))

    # Infos facture
    data = [
        ["Numéro de facture", facture.numero],
        ["Date d'émission", facture.date_emission.strftime("%d/%m/%Y")],
        ["Statut", facture.statut],
        ["Client", facture.reservation.client.username],
        ["Défunt", f"{facture.reservation.prenom_defunt} {facture.reservation.nom_defunt}"],
        ["Caveau", facture.reservation.caveau.numero],
        ["Montant total", f"{facture.montant} FCFA"],
    ]

    table = Table(data, colWidths=[200, 300])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))

    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer