from django.shortcuts import render, redirect, get_object_or_404
from .models import Etudiant, Choix_filiere,Departement,Promotion, Faculte
from .forms import EtudiantForm1, ChoixFiliereForm
from django.http import HttpResponse, JsonResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from django.contrib.auth.decorators import login_required

# Première étape : formulaire pour les informations de l'étudiant

def etudiant_form1(request):
    if request.method == 'POST':
        form = EtudiantForm1(request.POST)
        if form.is_valid():
            etudiant = form.save()
            request.session['etudiant_id'] = etudiant.id  # On stocke l'ID de l'étudiant dans la session
            return redirect('filiere_choix')  # Redirection vers le choix de filière
    else:
        form = EtudiantForm1()
    return render(request, 'inscription.html', {'form': form})

# Deuxième étape : formulaire pour le choix de la filière


def filiere_choix(request):
    etudiant_id = request.session.get('etudiant_id')
    if not etudiant_id:
        return redirect('etudiant_form1')  # Si l'étudiant n'a pas été créé, rediriger vers le premier formulaire
    
    etudiant = get_object_or_404(Etudiant, id=etudiant_id)
    
    if request.method == 'POST':
        form = ChoixFiliereForm(request.POST)
        if form.is_valid():
            choix_filiere = form.save(commit=False)
            choix_filiere.etudiant = etudiant  # Associer le choix de filière à l'étudiant
            choix_filiere.save()
            return redirect('felicitation')  # Redirection vers la génération du PDF
    else:
        form = ChoixFiliereForm()
    
    return render(request, 'choix_filiere.html', {'form': form})

# Vue pour générer le PDF après le choix de filière


def get_departements(request):
    faculte_id = request.GET.get('faculte')
    departements = Departement.objects.filter(faculte_id=faculte_id).all()
    return JsonResponse(list(departements.values('id', 'nom')), safe=False)

def get_promotions(request):
    departement_id = request.GET.get('departement')
    promotions = Promotion.objects.filter(departement_id=departement_id).all()
    return JsonResponse(list(promotions.values('id', 'nom')), safe=False)



from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from io import BytesIO
from django.http import HttpResponse
from django.shortcuts import redirect
from .models import Etudiant, Choix_filiere




def generer_pdf(request):
    etudiant_id = request.session.get('etudiant_id')
    if not etudiant_id:
        return redirect('etudiant_form1')  # Si pas d'étudiant, rediriger vers le premier formulaire

    etudiant = get_object_or_404(Etudiant, id=etudiant_id)
    choix_filiere = get_object_or_404(Choix_filiere, etudiant=etudiant)

    # Création du PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="inscription_{etudiant.nom}_{etudiant.prenom}.pdf"'

    # Configuration du PDF
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # ------------------- Première page : Informations Générales -------------------
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 100, "        FICHE ACADEMIQUE 2024-2025")

    c.setFont("Helvetica", 12)
    c.drawString(100, height - 130, "Premier tour")
    c.drawString(100, height - 150, "Imprimer cette page en deux exemplaires")
    c.drawString(100, height - 170, "Déposer son dossier complet à l’apparitorat central.")
    

    # Liste des éléments du dossier
    c.drawString(100, height - 210, "Liste des éléments du dossier :")
    elements_dossier = [
        "Formulaire de préinscription + le code élève à 14 chiffres",
        "Copie du reçu de paiement de frais de préinscription",
        "Palmarès, journal (édition 2022-2022)",
        "une copie du diplôme (de la première édition",
        "des examens d'Etat jusqu'en 2021)",
        "Copie de l'acte de naissance",
        "Original de l'attestation de bonne vie et moeurs et du civisme",
        "Original de l'attestation de résidence signée par un notable ",
        "Original du rapport médical fourni par une Médecin",
        "Deux photos passeport récentes (avec un fond blanc)"
    ]

    y_position = height - 230
    for element in elements_dossier:
        c.drawString(100, y_position, f"• {element}")
        y_position -= 20

    # Informations du candidat
    c.drawString(100, height - 440, "Le dossier est à déposer à la coordination centrale")
    
    c.drawString(100, height - 460, "...........................POUR TOUT CONTACT.....................")

    c.drawString(100, height - 480, "Contact : +243 997240522 / +243............... /")
    c.drawString(100, height - 500, "Email: informationetudiant@uma.ac.cd")

    c.showPage()

    # Page 2 - Informations personnelles
    # ------------------- Première page : Informations Générales -------------------
    c.setFont("Helvetica-Bold", 13)
    c.drawString(100, height - 50, "----------INFORMATIONS PERSONNELLES----------------")

    c.setFont("Helvetica", 12)
    c.drawString(100, height - 80, f"Lieu de naissance : {etudiant.lieu_naissance}")
    c.drawString(100, height - 100, f"Date de naissance : {etudiant.date_naissance.strftime('%d/%m/%Y')}")
    c.drawString(100, height - 120, f"Sexe : {etudiant.sexe}")
    c.drawString(100, height - 140, f"Nationalité : {etudiant.nationalite}")
    c.drawString(100, height - 160, f"Téléphone : {etudiant.telephone}")
    c.drawString(100, height - 180, f"Études secondaires : {etudiant.ecole}")
    c.drawString(100, height - 200, f"Secteur : {etudiant.secteur}")
    c.drawString(100, height - 220, f"Pourcentage : {etudiant.pourcentage}%")
    c.drawString(100, height - 240, f"Année d'obtention du diplôme : {etudiant.annee_obtention_diplome}")
    c.drawString(100, height - 260, f"Province origine : {etudiant.province_origine}")
    c.drawString(100, height - 280, f"Territoire : {etudiant.territoire_district}")
    c.drawString(100, height - 300, f"Adresse_mail : {etudiant.adresse_mail}")
    c.drawString(100, height - 340, f"Nom, post_nom et prénom : {etudiant.nom}_{etudiant.post_nom}_{etudiant.prenom}")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, height - 370, "----------CHOIX CANDIDAT A L'UNIVERSITE DE MANONO----------------")
    c.setFont("Helvetica", 12)
    c.drawString(100, height - 390, f"Faculté : {choix_filiere.faculte}")
    c.drawString(100, height - 410, f"Departement : {choix_filiere.departement}")
    c.drawString(100, height - 430, f"Promotion : {choix_filiere.promotion}")
    c.drawString(100, height - 450, f"identifiant : {2024}{choix_filiere.faculte.id}{choix_filiere.departement.id}{choix_filiere.promotion.id}{etudiant_id}")

    # Fin de la deuxième page
    c.showPage()
    

    # ------------------- Troisième page : Acte d'engagement -------------------
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 100, "                    ACTE D’ENGAGEMENT")

    c.setFont("Helvetica", 12)
    c.drawString(100, height - 140, "Je soussigné ....................................................")
    c.drawString(100, height - 160, "M’engage à observer scrupuleusement et sans conditions ")
    c.drawString(100, height - 180, "le règlement général applicable aux étudiants de l’Université de manono")
    c.drawString(100, height - 200, "tel que prévu par les dispositions légales en la matière.")

    c.drawString(100, height - 220, "d'ore et déjà : .")

    # Liste des engagements
    engagements = [
        "Je renonce à être l’auteur de tract ou document ;",
        "Je m’abstiens de contribuer à l’installation de la débauche sur le campus universitaire ;",
        "Je renonce aux pratiques barbares frisant l’immoralité telle que la « bleusaille » ;",
        "Je n’entreprendrai aucune action susceptible de perturber le déroulement des",
        "enseignements, des évaluations, des séances de délibérations, etc.",
        "Je ne constituerai pas le relais des personnes extérieures à l’Université dans le but d’en",
        "entraver le fonctionnement harmonieux ;",
        "Je n’organiserai aucune activité non autorisée par l’autorité de l’Université sur les sites",
    ]

    y_position = height - 240
    for engagement in engagements:
        c.drawString(100, y_position, f"• {engagement}")
        y_position -= 20
    
    c.drawString(100, height - 430, f"Fait à Manono, le ............./.............../..............")
    c.drawString(100, height - 450, f"Nom et signature : {etudiant.nom} {etudiant.post_nom} {etudiant.prenom}")


    # Finaliser le PDF
    c.showPage()
    c.save()

    # Retour du PDF en réponse HTTP
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="fiche_academique_2024-2025_{etudiant.nom}_{etudiant.post_nom}{etudiant.prenom}.pdf"'
    
    return response

    #response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    #response['Content-Disposition'] = 'attachment; filename="fiche_academique.pdf"'
    

def felicitation(request):
    return render(request, 'felicitation.html')



"""""from django.shortcuts import render, redirect
from .forms import EtudiantForm1, ChoixFiliereForm
from .models import Etudiant, Departement, Promotion
from django.http import JsonResponse
from datetime import time



def etudiant_form1(request):
    if request.method == 'POST':
        form = EtudiantForm1(request.POST)
        if form.is_valid():
            etudiant = form.save()
            request.session['etudiant_id'] = etudiant.id
            return redirect('filiere_choix')
    else:
        form = EtudiantForm1()
    return render(request, 'inscription.html', {'form': form})


def filiere_choix(request):
    if request.method == 'POST':
        form = ChoixFiliereForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('generer_pdf')  # Remplacez par la redirection appropriée
    else:
        form = ChoixFiliereForm()
    return render(request, 'choix_filiere.html', {'form': form})

def confirmation(request):
    return render(request, 'confirmation.html')

def get_departements(request):
    faculte_id = request.GET.get('faculte')
    departements = Departement.objects.filter(faculte_id=faculte_id).all()
    return JsonResponse(list(departements.values('id', 'nom')), safe=False)

def get_promotions(request):
    departement_id = request.GET.get('departement')
    promotions = Promotion.objects.filter(departement_id=departement_id).all()
    return JsonResponse(list(promotions.values('id', 'nom')), safe=False)





from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from io import BytesIO
from django.http import HttpResponse
from django.shortcuts import redirect
from .models import Etudiant, Choix_filiere

def generer_pdf(request):
    etudiant_id = request.session.get('etudiant_id')

    if etudiant_id is None:
        return redirect('etudiant_form1')  # Redirigez si l'étudiant n'est pas trouvé
    
    
    etudiant = Etudiant.objects.get(id=etudiant_id)

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # ------------------- Première page : Informations Générales -------------------
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 100, "FICHE ACADEMIQUE 2022-2023")

    c.setFont("Helvetica", 12)
    c.drawString(100, height - 130, "Premier tour")
    c.drawString(100, height - 150, "Imprimer cette page en deux exemplaires")
    c.drawString(100, height - 170, "Déposer son dossier complet à l’apparitorat central.")

    # Liste des éléments du dossier
    elements_dossier = [
        "Formulaire de préinscription + le code élève à 14 chiffres",
        "Copie du reçu de paiement de frais de préinscription",
        "Palmarès, journal (édition 2015, 2022), une copie du diplôme (de la première édition",
        "des examens d'Etat jusqu'en 2021)",
        "Copie de l'acte de naissance",
        "Original de l'attestation de bonne vie et moeurs et du civisme",
        "Original de l'attestation de résidence signée par un notable de Lubumbashi",
        "Original du rapport médical fourni par les Cliniques Universitaires de Lubumbashi",
        "Deux photos passeport récentes (avec un fond blanc)"
    ]

    y_position = height - 210
    for element in elements_dossier:
        c.drawString(100, y_position, f"• {element}")
        y_position -= 20

    # Informations du candidat
    c.drawString(100, height - 400, "Le dossier est à déposer à l'apparitorat central")
    
    c.drawString(100, height - 420, "...........................POUR TOUT CONTACT.....................")

    c.drawString(100, height - 440, "Tél : +243822350147 / +243990896424 / +243821222840")
    c.drawString(100, height - 460, "Email: informationetudiant@unilu.ac.cd")

    c.showPage()

    # Page 2 - Informations personnelles
    # ------------------- Première page : Informations Générales -------------------
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, height - 50, "----------INFORMATIONS PERSONNELLES----------------")

    c.setFont("Helvetica", 12)
    c.drawString(100, height - 80, f"Lieu de naissance : {etudiant.lieu_naissance}")
    c.drawString(100, height - 100, f"Date de naissance : {etudiant.date_naissance.strftime('%d/%m/%Y')}")
    c.drawString(100, height - 120, f"Sexe : {etudiant.sexe}")
    c.drawString(100, height - 140, f"Nationalité : {etudiant.nationalite}")
    c.drawString(100, height - 160, f"Téléphone : {etudiant.telephone}")
    c.drawString(100, height - 180, f"Études secondaires : {etudiant.ecole}")
    c.drawString(100, height - 200, f"Secteur : {etudiant.option}")
    c.drawString(100, height - 220, f"Pourcentage : {etudiant.pourcentage}%")
    c.drawString(100, height - 240, f"Année d'obtention du diplôme : {etudiant.annee_obtention_diplome}")
    c.drawString(100, height - 260, f"Province de l'école : {etudiant.province_educationnelle}")
    c.drawString(100, height - 280, f"Province de l'école : {etudiant.territoire_district}")
    c.drawString(100, height - 300, f"Province de l'école : {etudiant.adresse_mail}")
    c.drawString(100, height - 340, f"Nom, post_nom et prénom : {etudiant.nom}_{etudiant.post_nom}_{etudiant.prenom}")
    
    c.setFont("Helvetica-Bold", 13)
    c.drawString(100, height - 370, "----------CHOIX CANDIDAT----------------")
    c.setFont("Helvetica", 12)
    c.drawString(100, height - 390, f"Province de l'école : _{etudiant.prenom}")

    # Fin de la deuxième page
    c.showPage()
    

    # ------------------- Troisième page : Acte d'engagement -------------------
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 100, "ACTE D’ENGAGEMENT")

    c.setFont("Helvetica", 12)
    c.drawString(100, height - 140, "Je soussigné ...................................................")
    c.drawString(100, height - 160, "  M’engage à observer scrupuleusement et sans conditions ")
    c.drawString(100, height - 180, "      le règlement général applicable aux étudiants de l’Université de manono")
    c.drawString(100, height - 200, "      tel que prévu par les dispositions légales en la matière.")

    c.drawString(100, height - 200, "d'ore et déjà: .")

    # Liste des engagements
    engagements = [
        "Je renonce à être l’auteur de tract ou document séditieux incitatif aux troubles de",
        "quelque nature que ce soit ;",
        "Je m’abstiens de contribuer à l’installation de la débauche sur le campus universitaire ;",
        "Je renonce aux pratiques barbares frisant l’immoralité telle que la « bleusaille » ;",
        "Je n’entreprendrai aucune action susceptible de perturber le déroulement des",
        "enseignements, des évaluations, des séances de délibérations, etc.",
        "Je ne constituerai pas le relais des personnes extérieures à l’Université dans le but d’en",
        "entraver le fonctionnement harmonieux ;",
        "Je n’organiserai aucune activité non autorisée par l’autorité de l’Université sur les sites",
    ]

    y_position = height - 240
    for engagement in engagements:
        c.drawString(100, y_position, f"• {engagement}")
        y_position -= 20

    # Finaliser le PDF
    c.showPage()
    c.save()

    # Retour du PDF en réponse HTTP
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="fiche_academique.pdf"'
    return response



"""""

""""from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from io import BytesIO
from django.http import HttpResponse
from django.shortcuts import redirect
from .models import Etudiant

def generer_pdf(request):
    etudiant_id = request.session.get('etudiant_id')
    if etudiant_id is None:
        return redirect('etudiant_form1')  # Redirigez si l'étudiant n'est pas trouvé
    
    etudiant = Etudiant.objects.get(id=etudiant_id)
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Personnalisation de la mise en page
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, height - 50, "FICHE ACADEMIQUE 2022-2023")
    p.setFont("Helvetica", 12)
    p.drawString(100, height - 70, "Premier tour")
    
    p.setFont("Helvetica-Oblique", 10)
    p.drawString(100, height - 90, "Imprimer cette page en deux exemplaires")
    p.drawString(100, height - 110, "Déposer son dossier complet à l'apparitorat central.")

    # Liste des éléments du dossier sous forme de puces
    dossier_elements = [
        "Formulaire de préinscription + le code élève à 14 chiffres",
        "Copie du reçu de paiement de frais de préinscription",
        "Palmarès, journal (édition 2015, 2022), une copie du diplôme",
        "Copie de l'acte de naissance",
        "Original de l'attestation de bonne vie et mœurs et du civisme",
        "Original de l'attestation de résidence signée par un notable de Lubumbashi",
        "Original du rapport médical fourni par les Cliniques Universitaires de Lubumbashi",
        "Deux Photos passeport récentes (avec un fond blanc)",
        "L'acte d'engagement rempli et signé",
    ]
    
    p.setFont("Helvetica", 12)
    text_position = height - 150  # Départ du texte

    p.drawString(100, text_position, "Voici les éléments qui constituent le dossier :")
    
    # Ajouter chaque élément sous forme de puces
    for item in dossier_elements:
        text_position -= 20
        p.drawString(120, text_position, f"• {item}")

    # Fin de la première page
    p.showPage()

    # Page 2 - Informations personnelles
    p.setFont("Helvetica", 12)
    p.drawString(100, height - 50, "Informations personnelles")
    p.drawString(100, height - 70, f"Lieu de naissance : {etudiant.lieu_naissance}")
    p.drawString(100, height - 90, f"Date de naissance : {etudiant.date_naissance.strftime('%d/%m/%Y')}")
    p.drawString(100, height - 110, f"Sexe : {etudiant.sexe}")
    p.drawString(100, height - 130, f"Nationalité : {etudiant.nationalite}")
    p.drawString(100, height - 150, f"Téléphone : {etudiant.telephone}")
    p.drawString(100, height - 170, f"Études secondaires : {etudiant.ecole}")
    p.drawString(100, height - 190, f"Secteur : {etudiant.option}")
    p.drawString(100, height - 210, f"Pourcentage : {etudiant.pourcentage}%")
    p.drawString(100, height - 230, f"Année d'obtention du diplôme : {etudiant.annee_obtention_diplome}")
    p.drawString(100, height - 250, f"Province de l'école : {etudiant.province_educationnelle}")

    # Fin de la deuxième page
    p.showPage()

    # Page 3 - Acte d'engagement
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, height - 50, "ACTE D’ENGAGEMENT")
    
    p.setFont("Helvetica", 12)
    p.drawString(100, height - 70, "Je soussigné(e) :………………………………………………………………………")
    p.drawString(100, height - 90, "………………………………………………………………………………………………………………………………………")
    p.drawString(100, height - 110, "M’engage à observer scrupuleusement et sans conditions le règlement général applicable")
    p.drawString(100, height - 130, "aux étudiants de l’Université de Lubumbashi tel que prévu par les dispositions légales en la matière.")
    p.drawString(100, height - 150, "D’ores et déjà :")
    p.drawString(100, height - 170, "Je renonce à être l’auteur de tract ou document séditieux incitatif aux troubles de quelque nature que ce soit;")
    p.drawString(100, height - 190, "Je m’abstiens de contribuer à l’installation de la débauche sur le campus universitaire ;")
    p.drawString(100, height - 210, "Je renonce aux pratiques barbares frisant l’immoralité telle que la « bleusaille » ;")
    p.drawString(100, height - 230, "Je n’entreprendrai aucune action susceptible de perturber le déroulement des enseignements,")
    p.drawString(100, height - 250, "des évaluations, des séances de délibérations etc.,")
    p.drawString(100, height - 270, "Je ne constituerai pas le relais des personnes extérieures à l’Université et au pays qui seraient tentées d’entraîner les étudiants dans des aventures catastrophiques.")
    p.drawString(100, height - 290, f"Fait à Lubumbashi, le {etudiant.date_naissance.strftime('%d/%m/%Y')}")
    p.drawString(100, height - 310, f"Nom et signature : {etudiant.nom} {etudiant.post_nom} {etudiant.prenom}")

    # Fin de la troisième page
    p.showPage()
    p.save()

    # Retour du PDF en réponse HTTP
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="fiche_academique.pdf"'
    return response

"""""

"""""from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfgen import canvas
from io import BytesIO
from django.http import HttpResponse
from django.shortcuts import redirect
from .models import Etudiant

def generer_pdf(request):
    etudiant_id = request.session.get('etudiant_id')
    if etudiant_id is None:
        return redirect('etudiant_form1')  # Redirigez si l'étudiant n'est pas trouvé
    
    etudiant = Etudiant.objects.get(id=etudiant_id)
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Personnalisation de la mise en page
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, height - 50, "FICHE ACADEMIQUE 2022-2023")
    p.setFont("Helvetica", 12)
    p.drawString(100, height - 70, "Premier tour")
    
    p.setFont("Helvetica-Oblique", 10)
    p.drawString(100, height - 90, "Imprimer cette page en deux exemplaires")
    p.drawString(100, height - 110, "Déposer son dossier complet à l'apparitorat central.")

    # Ajout des éléments du dossier sous forme de tableau pour un meilleur alignement
    dossier_elements = [
        ["Élément requis", "Statut"],
        ["Formulaire de préinscription + le code élève à 14 chiffres", "Non soumis"],
        ["Copie du reçu de paiement de frais de préinscription", "Non soumis"],
        ["Palmarès, journal (édition 2015, 2022), une copie du diplôme", "Non soumis"],
        ["Copie de l'acte de naissance", "Non soumis"],
        ["Original de l'attestation de bonne vie et mœurs et du civisme", "Non soumis"],
        ["Original de l'attestation de résidence signée par un notable de Lubumbashi", "Non soumis"],
        ["Original du rapport médical fourni par les Cliniques Universitaires de Lubumbashi", "Non soumis"],
        ["Deux Photos passeport récentes (avec un fond blanc)", "Non soumis"],
        ["L'acte d'engagement rempli et signé", "Non soumis"],
    ]
    
    # Table styling
    table = Table(dossier_elements, colWidths=[4 * inch, 2 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    # Convertir la table en un canvas platypus
    table.wrapOn(p, width, height)
    table.drawOn(p, 100, height - 350)
    
    # Page 1 fin
    p.showPage()

    # Page 2
    p.setFont("Helvetica", 12)
    p.drawString(100, height - 50, "Informations personnelles")
    p.drawString(100, height - 70, f"Lieu de naissance : {etudiant.lieu_naissance}")
    p.drawString(100, height - 90, f"Date de naissance : {etudiant.date_naissance.strftime('%d/%m/%Y')}")
    p.drawString(100, height - 110, f"Sexe : {etudiant.sexe}")
    p.drawString(100, height - 130, f"Nationalité : {etudiant.nationalite}")
    p.drawString(100, height - 150, f"Téléphone : {etudiant.telephone}")
    p.drawString(100, height - 170, f"Études secondaires : {etudiant.ecole}")
    p.drawString(100, height - 190, f"Secteur : {etudiant.option}")
    p.drawString(100, height - 210, f"Pourcentage : {etudiant.pourcentage}%")
    p.drawString(100, height - 230, f"Année d'obtention du diplôme : {etudiant.annee_obtention_diplome}")
    p.drawString(100, height - 250, f"Province de l'école : {etudiant.province_educationnelle}")
    
    # Page 2 fin
    p.showPage()

    # Page 3 - Acte d'engagement
    p.setFont("Helvetica-Bold", 14)

    p.drawString(100, height - 50, "ACTE D’ENGAGEMENT")
    p.setFont("Helvetica", 12)
    p.drawString(100, height - 70, "Je soussigné(e) :………………………………………………………………………")
    p.drawString(100, height - 90, "………………………………………………………………………………………………………………………………………")
    p.drawString(100, height - 110, "M’engage à observer scrupuleusement et sans conditions le règlement général applicable")
    p.drawString(100, height - 130, "aux étudiants de l’Université de Lubumbashi tel que prévu par les dispositions légal en la matière.")
    p.drawString(100, height - 150, "D’ores et déjà :")
    p.drawString(100, height - 170, "Je renonce à être l’auteur de tract ou document séditieux incitatif aux troubles de quelque nature que ce soit;")
    p.drawString(100, height - 190, "Je m’abstiens de contribuer à l’installation de la débauche sur le campus universitaires ;")
    p.drawString(100, height - 210, "Je renonce aux pratiques barbares frisant l’immoralité telle que la « bleusaille » ;")
    p.drawString(100, height - 230, "Je n’entreprendrai aucune action susceptible de perturber le déroulement des enseignements,")
    p.drawString(100, height - 250, "des évaluations, des séances de délibérations etc.,")
    p.drawString(100, height - 270, "Je ne constituerai pas le relais des personnes extérieures à l’Université et au pays qui seraient tentées d’entraîner les étudiants dans des aventures catastrophiques.")
    p.drawString(100, height - 290, f"Fait à Lubumbashi, le {etudiant.date_naissance.strftime('%d/%m/%Y')}")
    p.drawString(100, height - 310, f"Nom et signature : {etudiant.nom} {etudiant.post_nom} {etudiant.prenom}")

    # Page 3 fin
    p.showPage()
    p.save()

    # Retour du PDF en réponse HTTP
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="fiche_academique.pdf"'
    return response 

    """""


""""from django.shortcuts import render, redirect
from .models import Etudiant
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

def generer_pdf(request):
    etudiant_id = request.session.get('etudiant_id')
    if etudiant_id is None:
        return redirect('etudiant_form1')  # Redirigez si l'étudiant n'est pas trouvé

    etudiant = Etudiant.objects.get(id=etudiant_id)
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Page 1
    p.drawString(100, height - 50, "FICHE ACADEMIQUE 2022-2023")
    p.drawString(100, height - 70, "Premier tour")
    p.drawString(100, height - 90, "Imprimer cette page en deux exemplaires")
    p.drawString(100, height - 110, "Déposer son dossier complet à l'apparitorat central.")
    p.drawString(100, height - 130, "Voici les éléments qui constituent le dossier:")
    dossier_elements = [
        "Formulaire de préinscription + le code élève à 14 chiffres",
        "Copie du reçu de paiement de frais de préinscription",
        "Palmarès, journal (édition 2015, 2022), une copie du diplôme",
        "Copie de l'acte de naissance",
        "Original de l'attestation de bonne vie et moeurs et du civisme",
        "Original de l'attestation de résidence signée par un notable de Lubumbashi",
        "Original du rapport médical fourni par les Cliniques Universitaires de Lubumbashi",
        "Deux Photos passeport récentes (avec un fond blanc)",
        "L'acte d'engagement rempli et signé",
    ]
    for i, element in enumerate(dossier_elements):
        p.drawString(100, height - 150 - i * 20, f"- {element}")

    p.drawString(100, height - 280, "Le dossier est à déposer à l'apparitorat central (au Rez-de-Chaussée du Building Administratif UNILU, Route kasapa) au plus tard le 26 novembre.")
    p.drawString(100, height - 300, "Prendre l'autorisation de se présenter à la banque (Apparitorat central)")
    p.drawString(100, height - 320, "Payer les frais d'inscription à toutes les Agences RAWBANK (Numéro du compte : 15130-01003581548-34 USD)")
    p.drawString(100, height - 340, "Pour toute information supplémentaire, veuillez consulter notre Page Facebook Université de Lubumbashi Officiel")
    p.drawString(100, height - 360, "Tél : +243822350147 / +243990896424 / +243821222840")
    p.drawString(100, height - 380, "Email: informationetudiant@unilu.ac.cd")
    p.drawString(100, height - 400, "Identité")
    p.drawString(100, height - 420, f"Nom, postnom, prénom : {etudiant.nom} {etudiant.post_nom} {etudiant.prenom}")

    p.showPage()

    # Page 2
    p.drawString(100, height - 50, "Informations personnelles")
    p.drawString(100, height - 70, f"Lieu de naissance : {etudiant.lieu_naissance}")
    p.drawString(100, height - 90, f"Date de naissance : {etudiant.date_naissance.strftime('%d/%m/%Y')}")
    p.drawString(100, height - 110, f"Sexe : {etudiant.sexe}")
    p.drawString(100, height - 130, f"État-civil : Célibataire")
    p.drawString(100, height - 150, f"Nationalité : {etudiant.nationalite}")
    p.drawString(100, height - 170, f"Téléphone : {etudiant.telephone}")
    p.drawString(100, height - 190, f"Études secondaires : {etudiant.ecole}")
    #p.drawString(100, height - 210, f"Code élève : {etudiant.code_eleve}")
    p.drawString(100, height - 230, f"Secteur : {etudiant.option}")
    p.drawString(100, height - 250, f"Pourcentage : {etudiant.pourcentage}%")
    #p.drawString(100, height - 270, f"Établissement : {etudiant.etablissement}")
    p.drawString(100, height - 290, f"Année d'obtention du diplôme : {etudiant.annee_obtention_diplome}")
    p.drawString(100, height - 310, f"Province de l'école : {etudiant.province_educationnelle}")

    p.drawString(100, height - 350, "Choix effectués :")
    #p.drawString(100, height - 370, f"Premier choix : {etudiant.filiere_choix}")
  
    p.showPage()

    # Page 3
    p.drawString(100, height - 50, "ACTE D’ENGAGEMENT")
    p.drawString(100, height - 70, "Je soussigné")
    p.drawString(100, height - 90, "………………………………………………………………………………………………………………………………………")
    p.drawString(100, height - 110, "M’engage à observer scrupuleusement et sans conditions le règlement général applicable")
    p.drawString(100, height - 130, "aux étudiants de l’Université de Lubumbashi tel que prévu par les dispositions légal en la matière.")
    p.drawString(100, height - 150, "D’ores et déjà :")
    p.drawString(100, height - 170, "Je renonce à être l’auteur de tract ou document séditieux incitatif aux troubles de quelque nature que ce soit;")
    p.drawString(100, height - 190, "Je m’abstiens de contribuer à l’installation de la débauche sur le campus universitaires ;")
    p.drawString(100, height - 210, "Je renonce aux pratiques barbares frisant l’immoralité telle que la « bleusaille » ;")
    p.drawString(100, height - 230, "Je n’entreprendrai aucune action susceptible de perturber le déroulement des enseignements,")
    p.drawString(100, height - 250, "des évaluations, des séances de délibérations etc.,")
    p.drawString(100, height - 270, "Je ne constituerai pas le relais des personnes extérieures à l’Université et au pays qui seraient tentées d’entraîner les étudiants dans des aventures catastrophiques.")
    p.drawString(100, height - 290, f"Fait à Lubumbashi, le {etudiant.date_naissance.strftime('%d/%m/%Y')}")
    p.drawString(100, height - 310, f"Nom et signature : {etudiant.nom} {etudiant.post_nom} {etudiant.prenom}")

    p.showPage()
    p.save()

    buffer.seek(0)
    
    # Correction ici : utiliser HttpResponse sans 'as_attachment'
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="fiche_academique.pdf"'
    return response

    """""

"""def choix_form(request):
    etudiant_id = request.session.get('etudiant_id')
    etudiant = Etudiant.objects.get(id=etudiant_id)
    
    if request.method == 'POST':
        form = ChoixForm(request.POST)
        if form.is_valid():
            # Process choices and save if necessary
            # Redirect to PDF generation
            return redirect('generer_pdf')
    else:
        form = ChoixForm()

    return render(request, 'choix_filiere.html', {'form': form, 'etudiant': etudiant})

from django.http import JsonResponse
from .models import Departement, Promotion

def get_departements(request):
    faculte_id = request.GET.get('faculte_id')
    departements = Departement.objects.filter(faculte_id=faculte_id)
    departement_list = list(departements.values('id', 'nom'))
    return JsonResponse(departement_list, safe=False)

def get_promotions(request):
    departement_id = request.GET.get('departement')
    promotions = Promotion.objects.filter(departement_id=departement_id).all()
    return JsonResponse(list(promotions.values('id', 'nom')), safe=False)

# etudiant/views.py
from django.shortcuts import render, redirect
from .models import Etudiant
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO



def generer_pdf(etudiant):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Page 1
    p.drawString(100, height - 50, "FICHE ACADEMIQUE 2022-2023")
    p.drawString(100, height - 70, "Premier tour")
    p.drawString(100, height - 90, "Imprimer cette page en deux exemplaires")
    p.drawString(100, height - 110, "Déposer son dossier complet à l'apparitorat central.")
    p.drawString(100, height - 130, "Voici les éléments qui constituent le dossier:")
    dossier_elements = [
        "Formulaire de préinscription + le code élève à 14 chiffres",
        "Copie du reçu de paiement de frais de préinscription",
        "Palmarès, journal (édition 2015, 2022), une copie du diplôme",
        "Copie de l'acte de naissance",
        "Original de l'attestation de bonne vie et moeurs et du civisme",
        "Original de l'attestation de résidence signée par un notable de Lubumbashi",
        "Original du rapport médical fourni par les Cliniques Universitaires de Lubumbashi",
        "Deux Photos passeport récentes (avec un fond blanc)",
        "L'acte d'engagement rempli et signé",
    ]
    for i, element in enumerate(dossier_elements):
        p.drawString(100, height - 150 - i * 20, f"- {element}")

    p.drawString(100, height - 280, "Le dossier est à déposer à l'apparitorat central (au Rez-de-Chaussée du Building Administratif UNILU, Route kasapa) au plus tard le 26 novembre.")
    p.drawString(100, height - 300, "Prendre l'autorisation de se présenter à la banque (Apparitorat central)")
    p.drawString(100, height - 320, "Payer les frais d'inscription à toutes les Agences RAWBANK (Numéro du compte : 15130-01003581548-34 USD)")
    p.drawString(100, height - 340, "Pour toute information supplémentaire, veuillez consulter notre Page Facebook Université de Lubumbashi Officiel")
    p.drawString(100, height - 360, "Tél : +243822350147 / +243990896424 / +243821222840")
    p.drawString(100, height - 380, "Email: informationetudiant@unilu.ac.cd")
    p.drawString(100, height - 400, "Identité")
    p.drawString(100, height - 420, f"Nom, postnom, prénom : {etudiant.nom} {etudiant.post_nom} {etudiant.prenom}")
    #p.drawString(100, height - 440, f"Identifiant : {etudiant.identifiant}")

    p.showPage()

    # Page 2
    p.drawString(100, height - 50, "Informations personnelles")
    p.drawString(100, height - 70, f"Lieu de naissance : {etudiant.lieu_naissance}")
    p.drawString(100, height - 90, f"Date de naissance : {etudiant.date_naissance.strftime('%d/%m/%Y')}")
    p.drawString(100, height - 110, f"Sexe : {etudiant.sexe}")
    p.drawString(100, height - 130, f"État-civil : Célibataire")
    p.drawString(100, height - 150, f"Nationalité : {etudiant.nationalite}")
    p.drawString(100, height - 170, f"Téléphone : {etudiant.telephone}")
    p.drawString(100, height - 190, f"Études secondaires : {etudiant.etudes_secondaires}")
    p.drawString(100, height - 210, f"Code élève : {etudiant.code_eleve}")
    p.drawString(100, height - 230, f"Secteur : {etudiant.section}")
    p.drawString(100, height - 250, f"Pourcentage : {etudiant.pourcentage}%")
    p.drawString(100, height - 270, f"Établissement : {etudiant.etablissement}")
    p.drawString(100, height - 290, f"Année d'obtention du diplôme : {etudiant.annee_obtention}")
    p.drawString(100, height - 310, f"Province de l'école : {etudiant.province_ecole}")

    p.drawString(100, height - 350, "Choix effectués :")
    p.drawString(100, height - 370, f"Premier choix : {etudiant.choix_1}")
    p.drawString(100, height - 390, f"Deuxième choix : {etudiant.choix_2}")

    p.showPage()

    # Page 3
    p.drawString(100, height - 50, "ACTE D’ENGAGEMENT")
    p.drawString(100, height - 70, "Je soussigné")
    p.drawString(100, height - 90, "………………………………………………………………………………………………………………………………………")
    p.drawString(100, height - 110, "M’engage à observer scrupuleusement et sans conditions le règlement général applicable")
    p.drawString(100, height - 130, "aux étudiants de l’Université de Lubumbashi tel que prévu par les dispositions légal en la matière.")
    p.drawString(100, height - 150, "D’ores et déjà :")
    p.drawString(100, height - 170, "Je renonce à être l’auteur de tract ou document séditieux incitatif aux troubles de quelque nature que ce soit;")
    p.drawString(100, height - 190, "Je m’abstiens de contribuer à l’installation de la débauche sur le campus universitaires ;")
    p.drawString(100, height - 210, "Je renonce aux pratiques barbares frisant l’immoralité telle que la « bleusaille » ;")
    p.drawString(100, height - 230, "Je n’entreprendrai aucune action susceptible de perturber le déroulement des enseignements,")
    p.drawString(100, height - 250, "des évaluations, des séances de délibérations etc.,")
    p.drawString(100, height - 270, "Je ne constituerai pas le relais des personnes extérieures à l’Université et au pays qui seraient tentées d’entraîner les étudiants dans des aventures catastrophiques.")
    p.drawString(100, height - 290, f"Fait à Lubumbashi, le {etudiant.date_naissance.strftime('%d/%m/%Y')}")
    p.drawString(100, height - 310, f"Nom et signature : {etudiant.nom} {etudiant.post_nom} {etudiant.prenom}")

    p.showPage()
    p.save()

    buffer.seek(0)
    return HttpResponse(buffer, as_attachment=True, filename='fiche_academique.pdf')



"""

"""from django.shortcuts import render, redirect
from .forms import EtudiantForm1, ChoixForm
from .models import Etudiant

from django.shortcuts import render, redirect

from .models import Etudiant
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

def etudiant_form1(request):
    if request.method == 'POST':
        form = EtudiantForm1(request.POST)
        if form.is_valid():
            etudiant = form.save()
            request.session['etudiant_id'] = etudiant.id
            return redirect('choix_view')
    else:
        form = EtudiantForm1()
    return render(request, 'inscription.html', {'form': form})


def choix_view(request):
    if request.method == 'POST':
        form = ChoixForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('generer_pdf')  # Remplacez par votre URL de succès
    else:
        form = ChoixForm()
    
    return render(request, 'choix_filiere.html', {'form': form})"""

"""def choix_form(request):
    etudiant_id = request.session.get('etudiant_id')
    etudiant = Etudiant.objects.get(id=etudiant_id)
    
    if request.method == 'POST':
        form = ChoixForm(request.POST)
        if form.is_valid():
            # Process choices and save if necessary
            # Redirect to PDF generation
            return redirect('generer_pdf')
    else:
        form = ChoixForm()

    return render(request, 'choix_filiere.html', {'form': form, 'etudiant': etudiant})

from django.http import JsonResponse
from .models import Departement, Promotion

def get_departements(request):
    if request.method == 'GET' and request.is_ajax():
        faculte_id = request.GET.get('faculte_id')
        departements = Departement.objects.filter(faculte_id=faculte_id).values('id', 'nom')
        return JsonResponse(list(departements), safe=False)

def get_promotions(request):
    if request.method == 'GET' and request.is_ajax():
        departement_id = request.GET.get('departement_id')
        promotions = Promotion.objects.filter(departement_id=departement_id).values('id', 'nom')
        return JsonResponse(list(promotions), safe=False)


def generer_pdf(etudiant):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Page 1
    p.drawString(100, height - 50, "FICHE ACADEMIQUE 2022-2023")
    p.drawString(100, height - 70, "Premier tour")
    p.drawString(100, height - 90, "Imprimer cette page en deux exemplaires")
    p.drawString(100, height - 110, "Déposer son dossier complet à l'apparitorat central.")
    p.drawString(100, height - 130, "Voici les éléments qui constituent le dossier:")
    dossier_elements = [
        "Formulaire de préinscription + le code élève à 14 chiffres",
        "Copie du reçu de paiement de frais de préinscription",
        "Palmarès, journal (édition 2015, 2022), une copie du diplôme",
        "Copie de l'acte de naissance",
        "Original de l'attestation de bonne vie et moeurs et du civisme",
        "Original de l'attestation de résidence signée par un notable de Lubumbashi",
        "Original du rapport médical fourni par les Cliniques Universitaires de Lubumbashi",
        "Deux Photos passeport récentes (avec un fond blanc)",
        "L'acte d'engagement rempli et signé",
    ]
    for i, element in enumerate(dossier_elements):
        p.drawString(100, height - 150 - i * 20, f"- {element}")

    p.drawString(100, height - 280, "Le dossier est à déposer à l'apparitorat central (au Rez-de-Chaussée du Building Administratif UNILU, Route kasapa) au plus tard le 26 novembre.")
    p.drawString(100, height - 300, "Prendre l'autorisation de se présenter à la banque (Apparitorat central)")
    p.drawString(100, height - 320, "Payer les frais d'inscription à toutes les Agences RAWBANK (Numéro du compte : 15130-01003581548-34 USD)")
    p.drawString(100, height - 340, "Pour toute information supplémentaire, veuillez consulter notre Page Facebook Université de Lubumbashi Officiel")
    p.drawString(100, height - 360, "Tél : +243822350147 / +243990896424 / +243821222840")
    p.drawString(100, height - 380, "Email: informationetudiant@unilu.ac.cd")
    p.drawString(100, height - 400, "Identité")
    p.drawString(100, height - 420, f"Nom, postnom, prénom : {etudiant.nom} {etudiant.post_nom} {etudiant.prenom}")
    p.drawString(100, height - 440, f"Identifiant : {etudiant.identifiant}")

    p.showPage()

    # Page 2
    p.drawString(100, height - 50, "Informations personnelles")
    p.drawString(100, height - 70, f"Lieu de naissance : {etudiant.lieu_naissance}")
    p.drawString(100, height - 90, f"Date de naissance : {etudiant.date_naissance.strftime('%d/%m/%Y')}")
    p.drawString(100, height - 110, f"Sexe : {etudiant.sexe}")
    p.drawString(100, height - 130, f"État-civil : Célibataire")
    p.drawString(100, height - 150, f"Nationalité : {etudiant.nationalite}")
    p.drawString(100, height - 170, f"Téléphone : {etudiant.telephone}")
    p.drawString(100, height - 190, f"Études secondaires : {etudiant.etudes_secondaires}")
    p.drawString(100, height - 210, f"Code élève : {etudiant.code_eleve}")
    p.drawString(100, height - 230, f"Secteur : {etudiant.section}")
    p.drawString(100, height - 250, f"Pourcentage : {etudiant.pourcentage}%")
    p.drawString(100, height - 270, f"Établissement : {etudiant.etablissement}")
    p.drawString(100, height - 290, f"Année d'obtention du diplôme : {etudiant.annee_obtention}")
    p.drawString(100, height - 310, f"Province de l'école : {etudiant.province_ecole}")

    p.drawString(100, height - 350, "Choix effectués :")
    p.drawString(100, height - 370, f"Premier choix : {etudiant.choix_1}")
    p.drawString(100, height - 390, f"Deuxième choix : {etudiant.choix_2}")

    p.showPage()

    # Page 3
    p.drawString(100, height - 50, "ACTE D’ENGAGEMENT")
    p.drawString(100, height - 70, "Je soussigné")
    p.drawString(100, height - 90, "………………………………………………………………………………………………………………………………………")
    p.drawString(100, height - 110, "M’engage à observer scrupuleusement et sans conditions le règlement général applicable")
    p.drawString(100, height - 130, "aux étudiants de l’Université de Lubumbashi tel que prévu par les dispositions légal en la matière.")
    p.drawString(100, height - 150, "D’ores et déjà :")
    p.drawString(100, height - 170, "Je renonce à être l’auteur de tract ou document séditieux incitatif aux troubles de quelque nature que ce soit;")
    p.drawString(100, height - 190, "Je m’abstiens de contribuer à l’installation de la débauche sur le campus universitaires ;")
    p.drawString(100, height - 210, "Je renonce aux pratiques barbares frisant l’immoralité telle que la « bleusaille » ;")
    p.drawString(100, height - 230, "Je n’entreprendrai aucune action susceptible de perturber le déroulement des enseignements,")
    p.drawString(100, height - 250, "des évaluations, des séances de délibérations etc.,")
    p.drawString(100, height - 270, "Je ne constituerai pas le relais des personnes extérieures à l’Université et au pays qui seraient tentées d’entraîner les étudiants dans des aventures catastrophiques.")
    p.drawString(100, height - 290, f"Fait à Lubumbashi, le {etudiant.date_naissance.strftime('%d/%m/%Y')}")
    p.drawString(100, height - 310, f"Nom et signature : {etudiant.nom} {etudiant.post_nom} {etudiant.prenom}")

    p.showPage()
    p.save()

    buffer.seek(0)
    return HttpResponse(buffer, as_attachment=True, filename='fiche_academique.pdf')



from django.shortcuts import render, redirect
from .forms import EtudiantForm
from .models import Etudiant, Faculte, Departement, Promotion

def inscription_etudiant(request):
    if request.method == 'POST':
        form = EtudiantForm(request.POST, request.FILES)
        if form.is_valid():
            etudiant = form.save()  # Sauvegarder les informations de l'étudiant
            return redirect('choix_filiere', etudiant_id=etudiant.id)  # Rediriger vers le choix de filière
    else:
        form = EtudiantForm()
    
    return render(request, 'inscription.html', {'form': form})


from django.http import JsonResponse
from .models import Departement, Promotion

def get_departements(request, faculte_id):
    departements = Departement.objects.filter(faculte_id=faculte_id)
    departements_list = list(departements.values('id', 'nom'))
    return JsonResponse(departements_list, safe=False)

def get_promotions(request, departement_id):
    promotions = Promotion.objects.filter(departement_id=departement_id)
    promotions_list = list(promotions.values('id', 'nom'))
    return JsonResponse(promotions_list, safe=False)

def choix_filiere(request, etudiant_id):
    etudiant = get_object_or_404(Etudiant, id=etudiant_id)
    facultes = Faculte.objects.all()

    if request.method == 'POST':
        # Récupérer les informations soumises
        faculte_id = request.POST.get('faculte')
        departement_id = request.POST.get('departement')
        promotion_id = request.POST.get('promotion')
        
        etudiant_nom = request.POST.get('nom')  
        etudiant_prenom = request.POST.get('prenom')
        
        # Ajouter ces informations à l'étudiant
        etudiant.faculte_id = faculte_id
        etudiant.departement_id = departement_id
        etudiant.promotion_id = promotion_id
        etudiant_nom = etudiant_nom
        etudiant_prenom = etudiant_prenom
        etudiant.save()

        # Rediriger vers la génération du PDF
        return redirect('generation_pdf', etudiant_id=etudiant.id)

    return render(request, 'choix_filiere.html', {'etudiant': etudiant})




from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from .models import Etudiant

def generation_pdf(request, etudiant_id):
    etudiant = get_object_or_404(Etudiant, id=etudiant_id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="fiche_{etudiant.nom}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)

    # Page 1 : Informations du dossier
    p.drawString(3 * cm, 28 * cm, "FICHE ACADEMIQUE 2022-2023")
    p.drawString(3 * cm, 27 * cm, "Premier tour")
    p.drawString(3 * cm, 26 * cm, "Imprimer cette page en deux exemplaires")
    # Ajouter les autres informations du dossier...
    p.showPage()

    # Page 2 : Informations personnelles de l'étudiant
    p.drawString(3 * cm, 28 * cm, "Lieu de naissance : " + etudiant.lieu_naissance)
    p.drawString(3 * cm, 27 * cm, "Date de naissance : " + etudiant.date_naissance.strftime("%d/%m/%Y"))
    # Ajouter les autres informations de l'étudiant...
    p.showPage()

    # Page 3 : Acte d'engagement
    p.drawString(3 * cm, 28 * cm, "ACTE D’ENGAGEMENT")
    p.drawString(3 * cm, 27 * cm, "Je soussigné, m’engage à respecter le règlement de l'Université.")
    # Ajouter les autres éléments de l'engagement...
    p.showPage()

    p.save()
    return response"""



""""from django.shortcuts import render, redirect
from .forms import EtudiantForm
from .models import Etudiant, Faculte

def inscription_etudiant(request):
    if request.method == 'POST':
        form = EtudiantForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('choix_filiere')  # Redirection vers la page de choix de filière
    else:
        form = EtudiantForm()
    return render(request, 'inscription.html', {'form': form})

from django.http import JsonResponse
from .models import Departement, Promotion

def get_departements(request):
    faculte_id = request.GET.get('faculte_id')
    departements = Departement.objects.filter(faculte_id=faculte_id)
    departements_list = list(departements.values('id', 'nom'))
    return JsonResponse(departements_list, safe=False)

def get_promotions(request):
    departement_id = request.GET.get('departement_id')
    promotions = Promotion.objects.filter(departement_id=departement_id)
    promotions_list = list(promotions.values('id', 'nom'))
    return JsonResponse(promotions_list, safe=False)


from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from django.conf import settings

def choix_filiere(request):
    facultes = Faculte.objects.all()

    if request.method == 'POST':
        # Récupérer les informations soumises
        faculte_id = request.POST.get('faculte')
        departement_id = request.POST.get('departement')
        promotion_id = request.POST.get('promotion')
        
        etudiant_nom = request.POST.get('nom')  
        etudiant_prenom = request.POST.get('prenom')

        faculte = Faculte.objects.get(id=faculte_id)
        departement = Departement.objects.get(id=departement_id)
        promotion = Promotion.objects.get(id=promotion_id)

        # Préparation de la réponse PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="fiche_academique.pdf"'

        p = canvas.Canvas(response, pagesize=A4)
        width, height = A4

        # Chemin vers le logo (ajuste en fonction de ton projet)
        #logo_path = "https://th.bing.com/th/id/R.26d1f8eaea48615e154161622df9de9b?rik=5Mfz36h784ldcA&pid=ImgRaw&r=0"

        # Page 1 : Ajout du logo et contenu formaté
        #if logo_path:
        #    p.drawImage(ImageReader(logo_path), width/2 - 3*cm, height - 4*cm, 6*cm, 6*cm)  # Centré

        p.setFont("Helvetica-Bold", 16)
        p.drawCentredString(width / 2, height - 5 * cm, "FICHE ACADEMIQUE 2022-2023")
        p.drawCentredString(width / 2, height - 6 * cm, "Premier tour")
        p.drawCentredString(width / 2, height - 7 * cm, "Imprimer cette page en deux exemplaires")
        p.setFont("Helvetica", 12)
        p.drawString(3 * cm, height - 9 * cm, "Déposer son dossier complet à l'apparitorat central.")
        p.drawString(3 * cm, height - 10 * cm, "Voici les éléments qui constituent le dossier:")

        dossier_elements = [
            "Formulaire de préinscription + le code élève à 14 chiffres",
            "Copie du reçu de paiement de frais de préinscription",
            "Palmarès, journal (édition 2015, 2022), une copie du diplôme (des examens d'Etat)",
            "Copie de l'acte de naissance",
            "Original de l'attestation de bonne vie et mœurs et du civisme",
            "Original de l'attestation de résidence signée par un notable de Lubumbashi",
            "Original du rapport médical fourni par les Cliniques Universitaires de Lubumbashi",
            "Deux Photos passeport récentes (avec un fond blanc)",
            "L'acte d'engagement rempli et signé",
            "Le dossier est à déposer à l'apparitorat central (Rez-de-Chaussée du Building Administratif UNILU, Route Kasapa)",
            "Date limite : 26 novembre",
            "Tout retard entraînera l'annulation de l'inscription."
        ]

        y_position = height - 11 * cm
        for element in dossier_elements:
            p.drawString(3 * cm, y_position, "- " + element)
            y_position -= 0.8 * cm

        # Informations bancaires
        p.drawString(3 * cm, y_position, "Prendre l'autorisation de se présenter à la banque (Apparitorat central)")
        y_position -= 1 * cm
        p.drawString(3 * cm, y_position, "Payer les frais d'inscription à RAWBANK (Numéro du compte : 15130-01003581548-34 USD)")
        y_position -= 1 * cm
        p.drawString(3 * cm, y_position, "Pour plus d'informations, consultez la Page Facebook Université de Lubumbashi Officiel")

        # Coordonnées
        y_position -= 1.5 * cm
        p.setFont("Helvetica-Bold", 12)
        p.drawString(3 * cm, y_position, "Tél : +243822350147 / +243990896424 / +243821222840")
        y_position -= 1 * cm
        p.drawString(3 * cm, y_position, "Email: informationetudiant@unilu.ac.cd")
        y_position -= 1 * cm
        p.drawString(3 * cm, y_position, "Numéro du compte : 15130-01003581548-34 USD")

        # Identité de l'étudiant
        y_position -= 2 * cm
        p.setFont("Helvetica-Bold", 14)
        p.drawString(3 * cm, y_position, "Identité de l'étudiant")
        p.setFont("Helvetica", 12)
        y_position -= 1 * cm
        p.drawString(3 * cm, y_position, f"Nom, Postnom, Prénom : {etudiant_nom.upper()} {etudiant_prenom.upper()}")
        y_position -= 1 * cm
        p.drawString(3 * cm, y_position, "Identifiant : 20230797")

        # Fin de la première page
        p.showPage()

        # Page 2 : Informations sur le choix de filière
        p.setFont("Helvetica-Bold", 14)
        p.drawString(3 * cm, height - 3 * cm, "Choix de Filière")
        p.setFont("Helvetica", 12)
        p.drawString(3 * cm, height - 5 * cm, f"Faculté : {faculte.nom}")
        p.drawString(3 * cm, height - 6 * cm, f"Département : {departement.nom}")
        p.drawString(3 * cm, height - 7 * cm, f"Promotion : {promotion.nom}")

        p.showPage()

        # Page 3 : Déclaration et engagement
        p.setFont("Helvetica-Bold", 14)
        p.drawString(3 * cm, height - 3 * cm, "Déclaration et Engagement")
        declaration = (
            "Je soussigné(e), reconnais avoir pris connaissance des règlements de l'université et m'engage à "
            "les respecter. Je confirme que toutes les informations fournies sont exactes et complètes. Je m'engage "
            "à suivre le programme choisi et à respecter les normes académiques et disciplinaires de l'université."
        )
        p.setFont("Helvetica", 12)
        p.drawString(3 * cm, height - 5 * cm, declaration)

        # Signature
        p.drawString(3 * cm, height - 10 * cm, "Signature de l'étudiant : ___________________________")

        # Terminer le PDF
        p.save()

        return response

    return render(request, 'choix_filiere.html', {'facultes': facultes})
"""""



"""from django.shortcuts import render
from django.http import HttpResponse
from .models import Faculte, Departement, Promotion, Etudiant  # Importer le modèle Etudiant si disponible
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
def choix_filiere(request):
    facultes = Faculte.objects.all()

    if request.method == 'POST':
        # Récupérer les informations du formulaire
        faculte_id = request.POST.get('faculte')
        departement_id = request.POST.get('departement')
        promotion_id = request.POST.get('promotion')
        
        # Informations supplémentaires de l'étudiant (ajoute ce que tu veux)
        etudiant_nom = request.POST.get('nom')  # Exemple de nom d'étudiant
        etudiant_prenom = request.POST.get('prenom')

        # Récupérer les instances des choix
        faculte = Faculte.objects.get(id=faculte_id)
        departement = Departement.objects.get(id=departement_id)
        promotion = Promotion.objects.get(id=promotion_id)

        

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="inscription_etudiant.pdf"'

        # Création d'un PDF de 3 pages avec ReportLab
        p = canvas.Canvas(response, pagesize=A4)

        # Page 1 : Informations personnelles
        p.setFont("Helvetica-Bold", 14)
        p.drawString(100, 800, "Informations Personnelles de l'Étudiant")
        p.setFont("Helvetica", 12)
        p.drawString(100, 750, f"Nom : {etudiant_nom}")
        p.drawString(100, 730, f"Prénom : {etudiant_prenom}")
        # Ajouter plus d'infos personnelles ici si besoin

        # Passer à la page suivante
        p.showPage()

        # Page 2 : Choix de la filière
        p.setFont("Helvetica-Bold", 14)
        p.drawString(100, 800, "Choix de Filière")
        p.setFont("Helvetica", 12)
        p.drawString(100, 750, f"Faculté : {faculte.nom}")
        p.drawString(100, 730, f"Département : {departement.nom}")
        p.drawString(100, 710, f"Promotion : {promotion.nom}")

        # Passer à la page suivante
        p.showPage()

        # Page 3 : Déclaration et engagement
        p.setFont("Helvetica-Bold", 14)
        p.drawString(100, 800, "Déclaration et Engagement")
        p.setFont("Helvetica", 12)
        declaration = (
            "Je soussigné(e), reconnais avoir pris connaissance des règlements de l'université "
            "et m'engage à les respecter. Je confirme que toutes les informations fournies "
            "sont exactes et complètes. Je m'engage à suivre le programme choisi et à respecter "
            "les normes académiques et disciplinaires de l'université."
        )
        p.drawString(100, 750, declaration)

        # Terminer le PDF
        p.showPage()
        p.save()

        # Retourner le PDF généré
        return response

    # Si GET, afficher le formulaire pour le choix de la filière
    return render(request, 'choix_filiere.html', {'facultes': facultes})

def choix_filiere(request):
    facultes = Faculte.objects.all()
    return render(request, 'choix_filiere.html', {'facultes': facultes})


from django.http import HttpResponse
from reportlab.pdfgen import canvas
from .models import Etudiant



from django.http import HttpResponse
from reportlab.pdfgen import canvas

def generation_pdf(request):
    etudiant = Etudiant.objects.last()  # L'étudiant récemment inscrit

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{etudiant.nom}_{etudiant.prenom}.pdf"'

    p = canvas.Canvas(response)

    p.drawString(100, 800, f"Nom: {etudiant.nom}")
    p.drawString(100, 780, f"Post-nom: {etudiant.post_nom}")
    p.drawString(100, 760, f"Prénom: {etudiant.prenom}")
    # Ajoute d'autres informations à afficher dans le PDF...

    p.showPage()
    p.save()

    return response
"""""

