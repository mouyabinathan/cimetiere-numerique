import flet as ft
import os, tempfile, subprocess
from config import PRIMARY, SECONDARY, BG_DARK, BG_CARD, FACT_STATUT_COLORS, FACT_STATUT_LABELS
from components.sidebar import build_sidebar
from components.header import build_header
from components.widgets import btn
import services.api as api


def page_facturation(page: ft.Page, state: dict, nav):
    page.overlay.clear()
    page.controls.clear()
    page.add(
        ft.Row(
            controls=[
                build_sidebar(page, state, "facturation", nav),
                ft.Column(
                    controls=[
                        build_header(page, state),
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.ProgressRing(color=PRIMARY, width=40, height=40),
                                    ft.Text("Chargement des factures...", size=13, color=SECONDARY)
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
        res_fact = api.get_factures(state["token"])
        if res_fact.status_code in (401, 403):
            _erreur(page, state, nav, "Accès refusé — droits insuffisants")
            return
        if res_fact.status_code != 200:
            _erreur(page, state, nav, f"Erreur serveur : {res_fact.status_code}")
            return
        try:
            res_resa = api.get_reservations(state["token"])
            resa_data = res_resa.json() if res_resa.status_code == 200 else []
        except Exception:
            resa_data = []
        _construire(page, state, nav, res_fact.json(), resa_data)
    except Exception as ex:
        _erreur(page, state, nav, str(ex))


def _erreur(page, state, nav, msg):
    page.overlay.clear()
    page.controls.clear()
    page.add(
        ft.Row(
            controls=[
                build_sidebar(page, state, "facturation", nav),
                ft.Column(
                    controls=[
                        build_header(page, state),
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Icon(ft.Icons.ERROR_OUTLINE, size=50, color=ft.Colors.RED_400),
                                    ft.Text(msg, size=13, color=ft.Colors.RED_400),
                                    btn("Réessayer", lambda e: page_facturation(page, state, nav), width=200)
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


def _construire(page, state, nav, factures, reservations):
    feedback   = ft.Text("", size=12, color=ft.Colors.RED_400)
    resa_index = {r["id"]: r for r in reservations}
    fact_ids   = {f["reservation_id"] for f in factures}
    resa_dispo = [r for r in reservations if r["statut"] == "VALIDEE" and r["id"] not in fact_ids]

    def do_pdf(facture_id, numero):
        try:
            res = api.get_facture_pdf(state["token"], facture_id)
            if res.status_code == 200:
                fname = f"facture_{numero}.pdf"
                tmp   = os.path.join(tempfile.gettempdir(), fname)
                with open(tmp, "wb") as f:
                    f.write(res.content)
                if os.name == "nt":
                    os.startfile(tmp)
                else:
                    subprocess.Popen(["xdg-open", tmp])
                feedback.value = f"✅ PDF ouvert : {tmp}"
                feedback.color = ft.Colors.GREEN_400
            else:
                feedback.value = f"Erreur PDF : {res.status_code}"
                feedback.color = ft.Colors.RED_400
            page.update()
        except Exception as ex:
            feedback.value = str(ex)
            feedback.color = ft.Colors.RED_400
            page.update()

    def do_paiement(facture_id, canal, montant, reference):
        try:
            res = api.create_paiement(state["token"], {
                "facture_id": facture_id,
                "canal":      canal,
                "montant":    float(montant),
                "reference":  reference or ""
            })
            if res.status_code == 200:
                page_facturation(page, state, nav)
            else:
                feedback.value = f"Erreur paiement : {res.status_code}"
                feedback.color = ft.Colors.RED_400
                page.update()
        except Exception as ex:
            feedback.value = str(ex)
            feedback.color = ft.Colors.RED_400
            page.update()

    def ouvrir_dialog_paiement(facture):
        canal_dd  = ft.Dropdown(
            label="Canal de paiement", value="MTN",
            options=[
                ft.dropdown.Option(key="MTN",      text="MTN Mobile Money"),
                ft.dropdown.Option(key="AIRTEL",   text="Airtel Money"),
                ft.dropdown.Option(key="ESPECES",  text="Espèces"),
                ft.dropdown.Option(key="VIREMENT", text="Virement bancaire"),
            ],
            width=380, border_color=SECONDARY, color=ft.Colors.WHITE, bgcolor=BG_DARK,
        )
        montant_f = ft.TextField(label="Montant (FCFA)", value=str(facture["montant"]),
                                 width=380, border_color=SECONDARY,
                                 color=ft.Colors.WHITE, bgcolor=BG_DARK)
        ref_f     = ft.TextField(label="Référence (optionnel)", width=380,
                                 border_color=SECONDARY, color=ft.Colors.WHITE, bgcolor=BG_DARK,
                                 hint_text="ex : TXN-2026-001",
                                 hint_style=ft.TextStyle(color=SECONDARY + "60"))
        pay_msg   = ft.Text("", size=12, color=ft.Colors.RED_400)
        dlg_ref   = {"dlg": None}

        def on_pay(e):
            if not canal_dd.value or not montant_f.value:
                pay_msg.value = "Veuillez remplir tous les champs"
                pay_msg.color = ft.Colors.RED_400
                page.update()
                return
            pay_msg.value = "Paiement en cours..."
            pay_msg.color = ft.Colors.AMBER_400
            page.update()

            def do_pay_and_close():
                import time
                do_paiement(facture["id"], canal_dd.value, montant_f.value, ref_f.value)
                # do_paiement recharge déjà la page, le dialog sera nettoyé par overlay.clear()

            dlg_ref["dlg"].open = False
            page.update()
            page.run_thread(do_pay_and_close)

        dlg = ft.AlertDialog(
            modal=True, bgcolor=BG_CARD,
            shape=ft.RoundedRectangleBorder(radius=14),
            title=ft.Row(controls=[
                ft.Icon(ft.Icons.PAYMENT_OUTLINED, color=PRIMARY, size=20),
                ft.Text(f"Paiement — {facture['numero']}", size=15,
                        weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ], spacing=8),
            content=ft.Column(
                controls=[
                    ft.Row(controls=[
                        ft.Text("Montant dû :", size=12, color=SECONDARY),
                        ft.Text(f"{facture['montant']} FCFA", size=14,
                                weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ], spacing=8),
                    ft.Divider(color=SECONDARY + "30", height=1),
                    canal_dd, montant_f, ref_f, pay_msg,
                    ft.Container(
                        content=ft.Row(controls=[
                            ft.Icon(ft.Icons.CHECK, color=ft.Colors.WHITE, size=14),
                            ft.Text("Confirmer le paiement", color=ft.Colors.WHITE,
                                    weight=ft.FontWeight.BOLD, size=13)
                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
                        width=380, height=44, bgcolor="#00CC77",
                        border_radius=10, alignment=ft.Alignment(0, 0),
                        on_click=on_pay, ink=True,
                    ),
                ],
                spacing=12, width=400, tight=True,
            ),
            actions=[
                ft.TextButton(
                    content=ft.Text("Annuler", color=SECONDARY, size=12),
                    on_click=lambda e: (setattr(dlg, "open", False), page.update())
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        dlg_ref["dlg"] = dlg
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    def card_facture(f):
        couleur  = FACT_STATUT_COLORS.get(f["statut"], "#555555")
        label    = FACT_STATUT_LABELS.get(f["statut"], f["statut"])
        resa     = resa_index.get(f["reservation_id"], {})
        defunt   = f"{resa.get('prenom_defunt','—')} {resa.get('nom_defunt','—')}"
        date_em  = f["date_emission"][:10]

        actions = [
            ft.Container(
                content=ft.Row(controls=[
                    ft.Icon(ft.Icons.PICTURE_AS_PDF_OUTLINED, size=13, color=ft.Colors.WHITE),
                    ft.Text("PDF", size=11, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
                ], spacing=6),
                bgcolor="#4D7FFF", border_radius=8,
                padding=ft.Padding.symmetric(horizontal=10, vertical=7),
                ink=True,
                on_click=lambda e, fid=f["id"], num=f["numero"]: page.run_thread(do_pdf, fid, num)
            )
        ]
        if f["statut"] == "EN_ATTENTE":
            actions.insert(0, ft.Container(
                content=ft.Row(controls=[
                    ft.Icon(ft.Icons.PAYMENT_OUTLINED, size=13, color=ft.Colors.WHITE),
                    ft.Text("Payer", size=11, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
                ], spacing=6),
                bgcolor="#00CC77", border_radius=8,
                padding=ft.Padding.symmetric(horizontal=10, vertical=7),
                ink=True,
                on_click=lambda e, fac=f: ouvrir_dialog_paiement(fac)
            ))

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(width=4, height=70, bgcolor=couleur, border_radius=2),
                    ft.Column(
                        controls=[
                            ft.Row(controls=[
                                ft.Text(f["numero"], size=14, weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.WHITE),
                                ft.Container(content=ft.Text(label, size=10, color=ft.Colors.WHITE),
                                             bgcolor=couleur, border_radius=6,
                                             padding=ft.Padding.symmetric(horizontal=8, vertical=2)),
                            ], spacing=8),
                            ft.Row(controls=[
                                ft.Icon(ft.Icons.PERSON_OUTLINED, size=12, color=SECONDARY),
                                ft.Text(defunt, size=11, color=SECONDARY),
                                ft.Icon(ft.Icons.CALENDAR_TODAY_OUTLINED, size=12, color=SECONDARY),
                                ft.Text(f"Émise le {date_em}", size=11, color=SECONDARY),
                            ], spacing=6),
                            ft.Row(controls=[
                                ft.Icon(ft.Icons.PAYMENTS_OUTLINED, size=12, color=SECONDARY),
                                ft.Text(f"{f['montant']} FCFA", size=13,
                                        color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                                *(
                                    [ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINED, size=12, color="#00CC77"),
                                     ft.Text(f"Payée le {f['date_paiement'][:10]}", size=11, color="#00CC77")]
                                    if f.get("date_paiement") else []
                                ),
                            ], spacing=6),
                        ],
                        spacing=4, expand=True
                    ),
                    ft.Row(controls=actions, spacing=8)
                ],
                spacing=14,
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            ),
            bgcolor=BG_CARD, border_radius=10, padding=14,
            border=ft.Border.all(1, SECONDARY + "20"),
        )

    total        = len(factures)
    en_attente   = len([f for f in factures if f["statut"] == "EN_ATTENTE"])
    payees       = len([f for f in factures if f["statut"] == "PAYEE"])
    montant_total = sum(float(f["montant"]) for f in factures if f["statut"] == "PAYEE")

    kpis = ft.Row(controls=[
        ft.Container(content=ft.Column(controls=[
            ft.Text(str(en_attente), size=24, weight=ft.FontWeight.BOLD, color="#FF9922"),
            ft.Text("En attente", size=10, color=SECONDARY)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
        bgcolor=BG_CARD, border_radius=10,
        padding=ft.Padding.symmetric(horizontal=20, vertical=12),
        border=ft.Border.all(1, "#FF9922" + "40"), expand=True),

        ft.Container(content=ft.Column(controls=[
            ft.Text(str(payees), size=24, weight=ft.FontWeight.BOLD, color="#00CC77"),
            ft.Text("Payées", size=10, color=SECONDARY)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
        bgcolor=BG_CARD, border_radius=10,
        padding=ft.Padding.symmetric(horizontal=20, vertical=12),
        border=ft.Border.all(1, "#00CC77" + "40"), expand=True),

        ft.Container(content=ft.Column(controls=[
            ft.Text(str(total), size=24, weight=ft.FontWeight.BOLD, color=SECONDARY),
            ft.Text("Total", size=10, color=SECONDARY)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
        bgcolor=BG_CARD, border_radius=10,
        padding=ft.Padding.symmetric(horizontal=20, vertical=12),
        border=ft.Border.all(1, SECONDARY + "40"), expand=True),

        ft.Container(content=ft.Column(controls=[
            ft.Text(f"{int(montant_total):,}".replace(",", " "),
                    size=18, weight=ft.FontWeight.BOLD, color="#4D7FFF"),
            ft.Text("FCFA encaissés", size=10, color=SECONDARY)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
        bgcolor=BG_CARD, border_radius=10,
        padding=ft.Padding.symmetric(horizontal=20, vertical=12),
        border=ft.Border.all(1, "#4D7FFF" + "40"), expand=True),
    ], spacing=12)

    # Formulaire nouvelle facture
    dlg_f_ref = {"dlg": None}

    def open_form_fact(e):
        # Champs créés localement à chaque ouverture
        resa_dd_f = ft.Dropdown(
            label="Réservation validée",
            options=[ft.dropdown.Option(
                key=str(r["id"]),
                text=f"#{r['id']} — {r['prenom_defunt']} {r['nom_defunt']} (Caveau #{r['caveau_id']})"
            ) for r in resa_dispo],
            width=400, border_color=SECONDARY, color=ft.Colors.WHITE, bgcolor=BG_DARK,
        )
        montant_ff = ft.TextField(
            label="Montant (FCFA)", width=400,
            border_color=SECONDARY, color=ft.Colors.WHITE, bgcolor=BG_DARK,
            hint_text="ex : 150000",
            hint_style=ft.TextStyle(color=SECONDARY + "60")
        )
        form_msg_f = ft.Text("", size=12, color=ft.Colors.RED_400)

        def close_fact(e=None):
            dlg_f_ref["dlg"].open = False
            page.update()

        def do_create_fact():
            import time
            resa_id = resa_dd_f.value
            montant = montant_ff.value
            try:
                res = api.create_facture(state["token"], int(resa_id), float(montant))
                if res.status_code == 200:
                    time.sleep(0.1)
                    page_facturation(page, state, nav)
            except Exception:
                pass

        def on_create_fact(e):
            if not resa_dd_f.value or not montant_ff.value:
                form_msg_f.value = "Veuillez remplir tous les champs"
                form_msg_f.color = ft.Colors.RED_400
                page.update()
                return
            # Fermer le dialog AVANT le thread
            dlg_f_ref["dlg"].open = False
            page.update()
            import threading
            threading.Thread(target=do_create_fact, daemon=True).start()

        form_col = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text("Nouvelle facture", size=16,
                                weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE_OUTLINED, icon_color=SECONDARY,
                            on_click=close_fact
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Divider(color=SECONDARY + "30", height=1),
                resa_dd_f if resa_dispo else ft.Row(controls=[
                    ft.Icon(ft.Icons.WARNING_AMBER_OUTLINED, size=16, color="#FF9922"),
                    ft.Text("Aucune réservation validée sans facture", size=12, color="#FF9922")
                ], spacing=6),
                montant_ff, form_msg_f,
                btn("Créer la facture", on_create_fact, width=400,
                    icon=ft.Icons.RECEIPT_OUTLINED, disabled=(not resa_dispo))
            ],
            spacing=12, tight=True
        )
        dlg = ft.AlertDialog(
            modal=True, bgcolor=BG_CARD,
            content=ft.Container(content=form_col, width=440),
            shape=ft.RoundedRectangleBorder(radius=14),
        )
        dlg_f_ref["dlg"] = dlg
        page.overlay.append(dlg)
        dlg.open = True
        page.update()


    main_content = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Column(controls=[
                            ft.Text("Facturation", size=20, weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.WHITE),
                            ft.Text(f"{total} facture(s) émise(s)", size=12, color=SECONDARY),
                        ], spacing=2),
                        ft.Container(
                            content=ft.Row(controls=[
                                ft.Icon(ft.Icons.ADD, size=14, color=ft.Colors.WHITE),
                                ft.Text("Nouvelle facture", size=12, color=ft.Colors.WHITE)
                            ], spacing=6),
                            bgcolor=PRIMARY, border_radius=8,
                            padding=ft.Padding.symmetric(horizontal=14, vertical=8),
                            ink=True, on_click=open_form_fact
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                kpis,
                feedback,
                ft.Column(
                    controls=[card_facture(f) for f in factures] if factures else [
                        ft.Container(
                            content=ft.Column(controls=[
                                ft.Icon(ft.Icons.RECEIPT_OUTLINED, size=40, color=SECONDARY),
                                ft.Text("Aucune facture émise", size=13, color=SECONDARY)
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                            alignment=ft.Alignment(0, 0), padding=40
                        )
                    ],
                    spacing=10,
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
                build_sidebar(page, state, "facturation", nav),
                ft.Column(controls=[build_header(page, state), main_content], spacing=0, expand=True)
            ],
            spacing=0,
            expand=True
        )
    )
    page.update()