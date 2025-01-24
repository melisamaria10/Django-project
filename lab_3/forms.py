from django import forms
import re
from django.core.exceptions import ValidationError
from datetime import date
from lab_3.models import Masina, Dealer, TipMotor, Categorie, Promotie

##Task 2 PROIECT Lab 5##
TIP_MESAJ_CHOICES = [
    ('reclamatie', 'Reclamatie'),
    ('intrebare', 'Intrebare'),
    ('review', 'Review'),
    ('cerere', 'Cerere'),
    ('programare', 'Programare'),
]

def validare_text(text):
    if not text:
        return
    if not text[0].isupper():
        raise ValidationError("Textul trebuie sa inceapă cu litera mare.")
    if not re.match(r'^[A-Za-z\s]+$', text):
        raise ValidationError("Textul poate contine doar litere și spatii.")
    
def validare_varsta(data_nasterii):
    today = date.today()
    age = today.year - data_nasterii.year - ((today.month, today.day) < (data_nasterii.month, data_nasterii.day))
    if age < 18:
        raise ValidationError("Trebuie sa aveti minim 18 ani pentru a trimite un mesaj.")
    
def validare_numar_cuvinte(val):
    words = val.split()
    if len(words) < 5 or len(words) > 100:
        raise ValidationError("Mesajul trebuie sa contina intre 5 si 100 de cuvinte.")
    
def validare_linkuri(val):
    if "http://" in val or "https://" in val:
        raise ValidationError("Mesajul nu poate contine linkuri.")
    
def validare_semnatura(val, nume):
    words = val.split()
    if words and words[-1].lower() != nume.lower():
        raise ValidationError(f"Mesajul trebuie sa se semneze cu numele dvs. '{nume}'.")
    
def validare_nume_si_subiect(val):
    validare_text(val)

class ContactForm(forms.Form):
    nume = forms.CharField(max_length=10, label='Nume', required=True, validators=[validare_nume_si_subiect])
    prenume = forms.CharField(label='Prenume', validators=[validare_nume_si_subiect], required=False)
    data_nasterii=forms.DateField(label='Data nasterii',widget=forms.DateInput(attrs={'type': 'date'}))
    email = forms.EmailField(label='Email', required=True)
    confirmare_email=forms.EmailField(label='Confirmare email', required=True)
    tip_mesaj=forms.ChoiceField(choices=TIP_MESAJ_CHOICES, label='Tip mesaj')
    subiect= forms.CharField(required=True, label='Subiect', validators=[validare_nume_si_subiect])
    minim_zile_asteptare=forms.IntegerField(label='Minim zile asteptare', min_value=1)
    mesaj = forms.CharField(widget=forms.Textarea, label='Mesaj', required=True, validators=[validare_numar_cuvinte,validare_linkuri])
    
    def clean(self):
        cleaned_data = super().clean()
        email = self.cleaned_data.get("email")
        confirm_email = self.cleaned_data.get("confirmare_email")
        if email and confirm_email and (email != confirm_email):
            raise forms.ValidationError("Adresele de email nu coincid.")
        
        return cleaned_data
        
    def clean_data_nasterii(self):
        data_nasterii = self.cleaned_data['data_nasterii']
        validare_varsta(data_nasterii)
        return data_nasterii
    
    def clean_mesaj(self):
        mesaj = self.cleaned_data['mesaj']
        nume = self.cleaned_data.get("nume")
        if nume:
            validare_semnatura(mesaj, nume)
        else:
            raise forms.ValidationError("Trebuie sa introduceti numele.")
        return mesaj

    
#####################################################

### TASK 3 LAB 5 ###
class MasinaForm(forms.ModelForm):
    stoc_suplimentar = forms.IntegerField(
        required=False,
        label="Stoc Suplimentar",
        help_text="Introduceți cantitatea suplimentară de mașini care urmează să fie adăugată în stoc.",
        min_value=0
    )
    
    kilometraj_mediu = forms.IntegerField(
        required=True,
        label="Kilometraj Mediu pe An (km)",
        help_text="Introduceți kilometrajul mediu estimat pe an (de ex. 10000)."
    )

    class Meta:
        model = Masina
        fields = ['marca', 'model', 'an_fabricatie', 'pret', 'dealer', 'categorie', 'tip_motor', 'caracteristici']
        labels = {
            'marca': 'Marca mașinii',
            'model': 'Modelul mașinii',
            'an_fabricatie': 'Anul fabricației',
            'pret': 'Prețul mașinii',
            'dealer': 'Dealer',
            'categorie': 'Categorie',
            'tip_motor': 'Tipul motorului',
            'caracteristici': 'Caracteristici',
        }
        help_texts = {
            'marca': 'Introduceți marca mașinii (ex: BMW, Audi).',
            'model': 'Introduceți modelul mașinii (ex: X5, A3).',
            'pret' : 'Introduceți prețul mașinii (în euro).',
        }

    # Validari pentru campuri individuale
    def clean_pret(self):
        pret = self.cleaned_data.get('pret')
        if pret <= 0:
            raise forms.ValidationError("Prețul trebuie să fie mai mare decât 0.")
        return pret
    
    def clean_an_fabricatie(self):
        an_fabricatie = self.cleaned_data.get('an_fabricatie')
        if an_fabricatie and an_fabricatie > date.today().year:
            raise forms.ValidationError("Anul de fabricație nu poate fi în viitor.")
        return an_fabricatie
    
    def clean_kilometraj_mediu(self):
        kilometraj_mediu = self.cleaned_data.get('kilometraj_mediu')
        if kilometraj_mediu < 0:
            raise forms.ValidationError("Kilometrajul mediu pe an nu poate fi negativ.")
        return kilometraj_mediu


    # Validare care implica mai multe câmpuri
    def clean(self):
        cleaned_data = super().clean()
        an_fabricatie = cleaned_data.get('an_fabricatie')
        kilometraj_mediu = cleaned_data.get('kilometraj_mediu')

        if an_fabricatie and kilometraj_mediu:
            varsta = date.today().year - an_fabricatie
            kilometraj_estimat = varsta * kilometraj_mediu
            
            if kilometraj_estimat > 500000:
                raise forms.ValidationError("Kilometrajul total estimat nu poate depăși 500.000 km.")
        return cleaned_data
    
    def save(self, commit=False):
        masina = super().save(commit=False)

        stoc_suplimentar = self.cleaned_data.get('stoc_suplimentar', 0)
        masina.stoc += stoc_suplimentar
        
        an_fabricatie = self.cleaned_data.get('an_fabricatie')
        kilometraj_mediu = self.cleaned_data.get('kilometraj_mediu', 0)

        if an_fabricatie and kilometraj_mediu:
            varsta = date.today().year - an_fabricatie
            kilometraj_estimat = varsta * kilometraj_mediu
            masina.kilometraj = kilometraj_estimat
        
        if commit:
            masina.save()  
        return masina
    
#####################################################
     
##TASK1 PROIECT Lab5
class FiltruMasinaForm(forms.Form):
    marca = forms.CharField(required=False, label='Marca',widget=forms.TextInput(attrs={'placeholder': 'Ex: BMW'}))
    model = forms.CharField(required=False, label='Model', widget=forms.TextInput(attrs={'placeholder': 'Ex: X5'}))
    an_fabricatie = forms.IntegerField(required=False, label='An fabricatie', widget=forms.NumberInput(attrs={'placeholder': 'Ex: 2020'}))
    min_kilometraj = forms.IntegerField(required=False, label='Kilometraj minim', widget=forms.NumberInput(attrs={'placeholder': 'Ex: 5000'}))
    max_kilometraj = forms.IntegerField(required=False, label='Kilometraj maxim', widget=forms.NumberInput(attrs={'placeholder': 'Ex: 200000'}))
    min_pret = forms.DecimalField(required=False, label='Pret minim', widget=forms.NumberInput(attrs={'placeholder': 'Ex: 5000'}))
    max_pret = forms.DecimalField(required=False, label='Pret maxim', widget=forms.NumberInput(attrs={'placeholder': 'Ex: 30000'}))
    dealer = forms.ModelChoiceField(queryset=Dealer.objects.all(), required=False, label='Dealer', empty_label='Alege un dealer', widget=forms.Select())
    categorie = forms.ModelChoiceField(queryset=Categorie.objects.all(), required=False, label='Categorie', empty_label='Alege o categorie', widget=forms.Select())
    tip_motor = forms.ModelChoiceField(queryset=TipMotor.objects.all(), required=False, label='Tip motor', empty_label='Alege tipul motorului', widget=forms.Select())
    
####################################################

### Formular de inregistrare customizat

from lab_3.models import CustomUser
from django.contrib.auth.forms import UserCreationForm

class CustomUserCreationForm(UserCreationForm):
    telefon = forms.CharField(required=True)
    data_nasterii = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}))
    adresa = forms.CharField(widget=forms.Textarea, required=False)
    gen = forms.ChoiceField(choices=CustomUser.GEN_CHOICES, required=True)
    cod_postal = forms.CharField(max_length=20, required=False)
    class Meta:
        model = CustomUser
        fields = ("username","first_name", "last_name","email", "telefon","data_nasterii","gen","adresa", "cod_postal", "password1", "password2")
    
    def clean_telefon(self):
        telefon=self.cleaned_data.get("telefon")
        if not telefon.isdigit():
            raise ValidationError("Numarul de telefon trebuie sa contina doar cifre.")
        if len(telefon) !=10 :
            raise ValidationError("Numarul de telefon trebuie sa aiba 10 cifre.")
        return telefon
    
    def clean_data_nasterii(self):
        data_nasterii=self.cleaned_data.get("data_nasterii")
        if data_nasterii>=date.today():
            raise ValidationError("Data nasterii nu poate fi in viitor")
        return data_nasterii
    
    def clean_adresa(self):
        adresa=self.cleaned_data.get("adresa")
        if adresa:
            nr_cuv=len(adresa.split())
            if nr_cuv < 6:
                raise ValidationError("Adresa trebuie sa contina minim 6 cuvinte")
        return adresa
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.telefon = self.cleaned_data["telefon"]
        user.data_nasterii = self.cleaned_data["data_nasterii"]
        user.adresa = self.cleaned_data["adresa"]
        user.gen = self.cleaned_data["gen"]
        user.cod_postal = self.cleaned_data["cod_postal"]
        if commit:
            user.save()
        return user
    
###Formular de autentificare customizat

from django import forms
from django.contrib.auth.forms import AuthenticationForm

class CustomAuthenticationForm(AuthenticationForm):
    ramane_logat = forms.BooleanField(
        required=False,
        initial=False,
        label='Ramaneti logat'
    )

    def clean(self):        
        cleaned_data = super().clean()
        ramane_logat = self.cleaned_data.get('ramane_logat')
        return cleaned_data

### TASK 2 LAB 7 ###

class PromotieForm(forms.ModelForm):
    data_expirare = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}) 
    )
    dealeri = forms.ModelMultipleChoiceField(
        queryset=Dealer.objects.filter(nume__in=['AutoDealer', 'BestCars']),
        widget=forms.CheckboxSelectMultiple(),
        label="Selectați Dealeri",
        initial=Dealer.objects.filter(nume__in=['AutoDealer', 'BestCars']),
    )
    class Meta:
        model = Promotie
        fields = ['nume', 'data_expirare', 'reduceri', 'dealeri']
        widgets = {
            'dealeri': forms.CheckboxSelectMultiple, 
        }