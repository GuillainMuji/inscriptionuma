from django.contrib import admin

from .models import Faculte, Departement, Promotion, Choix_filiere, Etudiant


class AdminFaculte(admin.ModelAdmin):
    list_display = ('nom',)

class AdminDepartement(admin.ModelAdmin):
    list_display = ('nom', 'faculte')

class AdminPromotion(admin.ModelAdmin):
    list_display = ('nom', 'departement')

class AdminFiliere(admin.ModelAdmin):
    list_display = ('etudiant', 'faculte', 'departement', 'promotion')

class AdminEtudiant(admin.ModelAdmin):
    list_display = ('nom', 'post_nom', 'prenom', 'sexe', 'province_origine', 'territoire_district', 'adresse_mail', 'telephone')


admin.site.register(Faculte,AdminFaculte)
admin.site.register(Departement, AdminDepartement)
admin.site.register(Promotion,AdminPromotion)
admin.site.register(Choix_filiere, AdminFiliere)
admin.site.register(Etudiant, AdminEtudiant)
