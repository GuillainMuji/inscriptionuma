from django import forms
from .models import Etudiant, Faculte, Departement, Promotion, Choix_filiere
from django.core.exceptions import ValidationError

class EtudiantForm1(forms.ModelForm):
    class Meta:
        model = Etudiant
        fields = [
            'nom', 'post_nom', 'prenom', 'sexe', 'etat_civil', 'pourcentage',
            'province_educationnelle', 'ecole', 'annee_obtention_diplome', 'option',
            'lieu_naissance', 'date_naissance', 'nationalite', 'province_origine',
            'territoire_district', 'secteur', 'adresse_mail', 'telephone', 'adresse_complet'
        ]
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        nom = cleaned_data.get('nom')
        post_nom = cleaned_data.get('post_nom')
        prenom = cleaned_data.get('prenom')
        province_origine = cleaned_data.get('province_origine')
        sexe = cleaned_data.get('sexe')
        annee_obtention_diplome = cleaned_data.get('annee_obtention_diplome')
        

        # Vérifie si un utilisateur avec le même nom, post_nom et prénom existe déjà
        if Etudiant.objects.filter(nom=nom, post_nom=post_nom, prenom=prenom, province_origine=province_origine, sexe = sexe, annee_obtention_diplome=annee_obtention_diplome).exists():
            raise ValidationError("Un etudiant avec les mêmes identifiants existe déjà, veuillez bien verifiér les informations .")
        return cleaned_data

class ChoixFiliereForm(forms.ModelForm):
    class Meta:
        model = Choix_filiere
        fields = ['faculte', 'departement', 'promotion']
        widgets = {
            'faculte': forms.Select(attrs={'id': 'faculte'}),
            'departement': forms.Select(attrs={'id': 'departement'}),
            'promotion': forms.Select(attrs={'id': 'promotion'}),
        }
