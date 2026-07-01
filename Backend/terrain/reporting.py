from ninja import Router
from terrain.models import Caveau, Bloc, Zone
from reservations.models import Reservation, Concession
from facturation.models import Facture, Paiement
from django.db.models import Sum, Count
from users.auth import AdminOnly
import csv
import openpyxl
from django.http import HttpResponse

router = Router()

@router.get("/dashboard", auth=AdminOnly())
def dashboard(request):
    total_caveaux = Caveau.objects.count()
    disponibles = Caveau.objects.filter(statut="DISPONIBLE").count()
    occupes = Caveau.objects.filter(statut="OCCUPE").count()
    reserves = Caveau.objects.filter(statut="RESERVE").count()
    total_reservations = Reservation.objects.count()
    en_attente = Reservation.objects.filter(statut="EN_ATTENTE").count()
    validees = Reservation.objects.filter(statut="VALIDEE").count()
    total_factures = Facture.objects.aggregate(Sum('montant'))['montant__sum'] or 0
    total_paye = Facture.objects.filter(statut="PAYEE").aggregate(Sum('montant'))['montant__sum'] or 0
    return {
        "caveaux": {
            "total": total_caveaux,
            "disponibles": disponibles,
            "occupes": occupes,
            "reserves": reserves,
            "taux_occupation": round((occupes / total_caveaux * 100), 2) if total_caveaux > 0 else 0
        },
        "reservations": {
            "total": total_reservations,
            "en_attente": en_attente,
            "validees": validees,
        },
        "finances": {
            "total_facture": float(total_factures),
            "total_paye": float(total_paye),
            "total_impaye": float(total_factures - total_paye)
        }
    }

@router.get("/stats-par-bloc", auth=AdminOnly())
def stats_par_bloc(request):
    blocs = Bloc.objects.all()
    result = []
    for bloc in blocs:
        total = Caveau.objects.filter(bloc=bloc).count()
        occupes = Caveau.objects.filter(bloc=bloc, statut="OCCUPE").count()
        result.append({
            "bloc": bloc.nom,
            "zone": bloc.zone.nom,
            "total": total,
            "occupes": occupes,
            "taux": round((occupes / total * 100), 2) if total > 0 else 0
        })
    return result

@router.get("/export/csv", auth=AdminOnly())
def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="registre_funeraire.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Défunt', 'Caveau', 'Bloc', 'Zone', 'Statut', 'Date demande', 'Date validation'])
    reservations = Reservation.objects.select_related('caveau__bloc__zone').all()
    for r in reservations:
        writer.writerow([
            r.id,
            f"{r.prenom_defunt} {r.nom_defunt}",
            r.caveau.numero,
            r.caveau.bloc.nom,
            r.caveau.bloc.zone.nom,
            r.statut,
            r.date_demande.strftime("%d/%m/%Y"),
            r.date_validation.strftime("%d/%m/%Y") if r.date_validation else ""
        ])
    return response

@router.get("/export/excel", auth=AdminOnly())
def export_excel(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Registre Funéraire"
    ws.append(['ID', 'Défunt', 'Caveau', 'Bloc', 'Zone', 'Statut', 'Date demande', 'Date validation'])
    reservations = Reservation.objects.select_related('caveau__bloc__zone').all()
    for r in reservations:
        ws.append([
            r.id,
            f"{r.prenom_defunt} {r.nom_defunt}",
            r.caveau.numero,
            r.caveau.bloc.nom,
            r.caveau.bloc.zone.nom,
            r.statut,
            r.date_demande.strftime("%d/%m/%Y"),
            r.date_validation.strftime("%d/%m/%Y") if r.date_validation else ""
        ])
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="registre_funeraire.xlsx"'
    wb.save(response)
    return response