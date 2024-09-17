from django.urls import path
from . import views

urlpatterns = [
    path('', views.etudiant_form1, name='etudiant_form1'),
    path('filiere_choix/', views.filiere_choix, name='filiere_choix'),
    path('get-departements/',views.get_departements, name='get_departements'),
    path('get-promotions/',views.get_promotions, name='get_promotions'),
    #path('confirmation/',views.confirmation, name='confirmation'),
    path('generer_pdf/',views.generer_pdf, name='generer_pdf'),
    path('felicitation/', views.felicitation, name='felicitation'),

]
