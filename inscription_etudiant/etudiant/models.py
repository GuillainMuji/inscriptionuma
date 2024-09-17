from django.db import models

class Etudiant(models.Model):
    PROVINCES = [
    ('KINSHASA', 'Kinshasa'),
    ('BAS_UELE', 'Bas-Uele'),
    ('HAUT_UELE', 'Haut-Uele'),
    ('ITURI', 'Ituri'),
    ('NORD_KIVU', 'Nord-Kivu'),
    ('SUD_KIVU', 'Sud-Kivu'),
    ('MANIEMA', 'Maniema'),
    ('HAUT_LOMAMI', 'Haut-Lomami'),
    ('TANGANYIKA', 'Tanganyika'),
    ('LOMAMI', 'Lomami'),
    ('KASAI', 'Kasaï'),
    ('KASAI_CENTRAL', 'Kasaï-Central'),
    ('KASAI_ORIENTAL', 'Kasaï-Oriental'),
    ('HAUT_KATANGA', 'Haut-Katanga'),
    ('LUALABA', 'Lualaba'),
    ('EQUATEUR', 'Équateur'),
    ('SUD_UBANGI', 'Sud-Ubangi'),
    ('NORD_UBANGI', 'Nord-Ubangi'),
    ('MONGALA', 'Mongala'),
    ('TSHOPO', 'Tshopo'),
    ('TSHUAPA', 'Tshuapa'),
    ('MAI_NDOMBE', 'Mai-Ndombe'),
    ('KWILU', 'Kwilu'),
    ('KWANGO', 'Kwango'),
    ('KINSHASA', 'Kinshasa'),
    ]

    # Liste des états civils
    ETAT_CIVIL = [
    ('CELIBATAIRE', 'Célibataire'),
    ('MARIE', 'Marié(e)'),
    ]
    # Informations scolaires
    province_educationnelle = models.CharField(max_length=255)
    ecole = models.CharField(max_length=255)
    annee_obtention_diplome = models.IntegerField()
    option = models.CharField(max_length=255, blank=True, null=True)

    # Informations personnelles
    nom = models.CharField(max_length=255)
    post_nom = models.CharField(max_length=255)
    prenom = models.CharField(max_length=255)
    sexe = models.CharField(max_length=10, choices=[('M', 'Masculin'), ('F', 'Féminin')])
    etat_civil = models.CharField(max_length=50, choices= ETAT_CIVIL)
    pourcentage = models.CharField(max_length=10)

    # Photo d'identité
    #photo_passeport = models.ImageField(upload_to='photos/')

    # Deuxième étape
    lieu_naissance = models.CharField(max_length=255)
    date_naissance = models.DateField()
    nationalite = models.CharField(max_length=255)
    province_origine = models.CharField(max_length=255,choices=PROVINCES)
    territoire_district = models.CharField(max_length=255)
    secteur = models.CharField(max_length=255)
    adresse_mail = models.EmailField()
    telephone = models.CharField(max_length=15)
    adresse_complet = models.TextField()

    def __str__(self):
        return f"{self.nom} {self.post_nom} {self.prenom}"



class Faculte(models.Model):
    nom = models.CharField(max_length=255)

    def __str__(self):
        return self.nom

class Departement(models.Model):
    faculte = models.ForeignKey(Faculte, on_delete=models.CASCADE)
    nom = models.CharField(max_length=255)
    

    def __str__(self):
        return self.nom

class Promotion(models.Model):
    departement = models.ForeignKey(Departement, on_delete=models.CASCADE)
    nom = models.CharField(max_length=255, default='S1')
    

    def __str__(self):
        return self.nom

class Choix_filiere(models.Model):
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE)  # Nouvelle relation avec Etudiant
    faculte = models.ForeignKey(Faculte, on_delete=models.CASCADE)
    departement = models.ForeignKey(Departement, on_delete=models.CASCADE)
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.faculte} {self.departement} {self.promotion}"