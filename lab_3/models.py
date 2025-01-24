from django.db import models
from django.contrib.auth.models import AbstractUser,User
from django.urls import reverse


### Clasa de utilizator


class CustomUser(AbstractUser):
    telefon = models.CharField(max_length=15, blank=True)
    data_nasterii = models.DateField(blank=True, null=True)
    adresa = models.TextField(blank=True, null=True)
    GEN_CHOICES=[
        ('masculin', 'Masculin'),
        ('feminin', 'Feminin'),
        ('nu doresc sa raspund', 'Nu doresc sa raspund')
    ]
    gen=models.CharField(max_length=30, choices=GEN_CHOICES, blank=True, null=True)
    cod_postal=models.CharField(max_length=20, blank=True, null=True)
    cod = models.CharField(max_length=100, blank=True, null=True) 
    email_confirmat = models.BooleanField(default=False)
    blocat = models.BooleanField(default=False)
    


### Clasa de comanda

from django.conf import settings

class Comanda(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Leagă comanda de utilizator
    produse = models.JSONField()  # Stocăm produsele sub formă de JSON (id + cantitate)
    total_pret= models.DecimalField(max_digits=10, decimal_places=2)
    total_cantitate = models.IntegerField()  # Totalul cantităților
    data_comanda = models.DateTimeField(auto_now_add=True)  # Data la care a fost realizată comanda

    def __str__(self):
        return f"Comanda {self.id} pentru {self.user.username} la {self.data_comanda}"  
    

# Create your models here.

class Caracteristici(models.Model):
    id_caracteristici=models.AutoField(primary_key=True)
    nume=models.CharField(max_length=50)
    descriere=models.TextField(null=True)
    def __str__(self):
        return self.nume
    
class TipMotor(models.Model):
    class TipuriMotorChoices(models.TextChoices):
        DIESEL = 'diesel', 'Diesel'
        BENZINA = 'benzina', 'Benzina'
        ELECTRIC = 'electric', 'Electric'
        HIBRID = 'hibrid', 'Hibrid'

    id_motor = models.AutoField(primary_key=True)
    tip_motor = models.CharField(max_length=20, choices=TipuriMotorChoices.choices, unique=True)

    def __str__(self):
        return self.tip_motor
    
class Categorie(models.Model):
    id_categorie=models.AutoField(primary_key=True)
    nume=models.CharField(max_length=50)
    descriere=models.TextField(null=True)
    tipuri_motor = models.ManyToManyField(TipMotor)
    def __str__(self):
        return self.nume
    def get_tipuri_motor(self):
        return ", ".join([tip.tip_motor for tip in self.tipuri_motor.all()])
        
class Dealer(models.Model):
    id_dealer=models.AutoField(primary_key=True)
    nume=models.CharField(max_length=20)
    telefon=models.CharField(max_length=10)
    email=models.EmailField()
    locatie=models.CharField()
    def __str__(self):
        return f"{self.nume} - {self.telefon}"
     
class Masina(models.Model):
    id_masina=models.AutoField(primary_key=True)
    marca=models.CharField(max_length=20)
    model=models.CharField(max_length=20)
    an_fabricatie=models.PositiveIntegerField()
    kilometraj=models.PositiveIntegerField(default=0)
    pret=models.DecimalField(max_digits=8, decimal_places=2)
    imagine=models.ImageField(upload_to='images/', max_length=300)
    dealer=models.ForeignKey(Dealer, on_delete=models.CASCADE)
    categorie=models.ForeignKey(Categorie, on_delete=models.CASCADE)
    tip_motor=models.ForeignKey(TipMotor, on_delete=models.CASCADE)
    caracteristici=models.ManyToManyField(Caracteristici)
    stoc= models.PositiveBigIntegerField(default=1)
        
    def __str__(self):
        return f"{self.marca} {self.model}"
    
    def get_absolute_url(self):
        return reverse('masina_detail', kwargs={'id': self.id_masina})
    
class Revizie(models.Model):
    id_revizie=models.AutoField(primary_key=True)
    data_revizie=models.DateField()
    nr_kilometri=models.PositiveIntegerField()
    serviciu=models.CharField(max_length=50)
    cost=models.DecimalField(max_digits=8, decimal_places=2)
    masina=models.ForeignKey(Masina, on_delete=models.CASCADE)
    def __str__(self):
        return self.serviciu

### TASK 2 LAB 7 ###

from django.conf import settings

class Vizualizare(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  
    masina = models.ForeignKey(Masina, on_delete=models.CASCADE)  
    data_vizualizare = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        return f"{self.user.username} a vizualizat {self.masina.marca} {self.masina.model}"  
    
class Promotie(models.Model):
    nume = models.CharField(max_length=100)  
    data_creare = models.DateTimeField(auto_now_add=True)  
    data_expirare = models.DateTimeField() 
    reduceri = models.PositiveIntegerField(default=10)  
    dealeri = models.ManyToManyField(Dealer)  

    def __str__(self):
        return f"{self.nume} ({self.data_expirare})"
    
###TASK 3 LAB 8 ###
from django.contrib.contenttypes.models import ContentType

class Oferta(models.Model):
    nume = models.CharField(max_length=255)
    descriere = models.TextField()

    class Meta:
        permissions = [
            ("vizualizeaza_oferta", "Poate vizualiza oferta")  
        ]

    def __str__(self):
        return self.nume
