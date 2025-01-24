from django.shortcuts import render, redirect
from django.http import HttpResponse

from .forms import ContactForm, MasinaForm, FiltruMasinaForm, PromotieForm
from django.core.paginator import Paginator
from .models import Masina, Dealer, Categorie, TipMotor, CustomUser, Vizualizare, Promotie, Oferta, Comanda
from django.contrib.auth import authenticate
from lab_3.forms import CustomUserCreationForm, PromotieForm
from django.contrib.auth import login
import json, os, time
from lab_3.utils import preprocesare_mesaj, calculeaza_varsta
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages

   
### Inregistrare ###

### TASK 1 LAB 7 ###
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user= form.save(commit=False)
            user.cod=str(uuid.uuid4())
            user.save()
            trimite_email_confirmare(user)
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'lab_3/inregistrare.html', {'form': form})

### Autentificare + TASK 3 LAB 7 + TASK 4 LAB 7  ###

from .forms import CustomAuthenticationForm
from django.core.mail import mail_admins
from django.utils import timezone
from datetime import timedelta
from datetime import datetime

def custom_login_view(request):
    if request.method == 'POST':
        logger.debug("S-a inițiat o cerere de logare.") #DEBUG
        form = CustomAuthenticationForm(data=request.POST, request=request)
        try:
            # Verif daca username-ul este 'admin' si daca s-a gresit parola
            username = request.POST.get('username')
            if username == 'admin' and not form.is_valid():
                ip_address = request.META.get('REMOTE_ADDR')
                logger.critical("Admin încearcă să se logheze fără parolă validă.") #CRITICAL

                # Trimitem email daca username-ul este 'admin' si parola e gresita
                subject = 'Cineva încearcă să ne preia site-ul'
                message = f'Au fost încercări de logare eșuate pentru adminul {username} din IP-ul {ip_address}.'
                html_message = f'<h1 style="color:red;">Cineva încearcă să ne preia site-ul</h1><p>Au fost încercări de logare eșuate pentru adminul <strong>{username}</strong> din IP-ul <strong>{ip_address}</strong>.</p>'
                mail_admins(subject, message, html_message=html_message, fail_silently=False)

            # Verif daca logarea e valida
            if form.is_valid():
                user = form.get_user()
                
                 # Verif daca utilizatorul este blocat
                if user.blocat:
                    logger.warning(f"Utilizatorul {user.username} este blocat și a încercat să se logheze.")  # WARNING
                    messages.error(request, "Contul tău a fost blocat. Nu te poți autentifica.")
                    return redirect('login')  

                if not user.email_confirmat:
                    logger.warning(f"Utilizatorul {user.username} nu și-a confirmat email-ul.") #WARNING
                    messages.error(request, "Trebuie să confirmați e-mailul înainte de a vă autentifica.")
                    return redirect('login')

                request.session['failed_logins'] = []
                login(request, user)

                request.session['username'] = user.username
                request.session['email'] = user.email
                request.session['telefon'] = user.telefon or "Nu a fost specificat"
                request.session['data_nasterii'] = user.data_nasterii.strftime('%Y-%m-%d') if user.data_nasterii else "Nu a fost specificata"
                request.session['gen'] = user.gen or "Nu a fost specificat"
                request.session['adresa'] = user.adresa or "Nu este specificata"
                request.session['cod_postal'] = user.cod_postal or "Nu este specificat"

                if not form.cleaned_data.get('ramane_logat'):
                    request.session.set_expiry(0)
                else:
                    request.session.set_expiry(24 * 60 * 60)  # o zi în secunde
                    
                logger.info(f"Autentificare completă pentru {user.username}.") #INFO
                return redirect('profil')

            else:
                ip_address = request.META.get('REMOTE_ADDR')
                failed_logins = request.session.get('failed_logins', [])

                # Ad incercarea curenta
                failed_logins.append(timezone.now().strftime('%Y-%m-%d %H:%M:%S')) 

                # Alegem incercarile vechi de 2 minute
                failed_logins = [attempt for attempt in failed_logins if timezone.now() - timezone.make_aware(datetime.strptime(attempt, '%Y-%m-%d %H:%M:%S')) < timedelta(minutes=2)]

                # Daca sunt 3 incercari esuate in 2 minute, trimitem email
                if len(failed_logins) >= 3:
                    logger.error("Trei încercări de logare eșuate consecutive detectate.")  # ERROR
                    subject = 'Logări suspecte'
                    message = f'Au fost 3 încercări de logare eșuate pentru utilizatorul {username} din IP-ul {ip_address}.'
                    html_message = f'<h1 style="color:red;">Logări suspecte</h1><p>Au fost 3 încercări de logare eșuate pentru utilizatorul <strong>{username}</strong> din IP-ul <strong>{ip_address}</strong>.</p>'
                    mail_admins(subject, message, html_message=html_message, fail_silently=False)

                    request.session['failed_logins'] = []

                else:
                    request.session['failed_logins'] = failed_logins

                messages.error(request, "Login eșuat! Încearcă din nou.")
                return redirect('login')  # Redirectionam utilizatorul inapoi la pagina de login

        except Exception as e:
            logger.error(f"Eroare la logare: {str(e)}")
            subject = 'Eroare la logare'
            message = f'A apărut o eroare neașteptată în procesul de logare: {str(e)}'
            html_message = f'<h1 style="color:red;">Eroare la logare</h1><p>A apărut o eroare neașteptată: <strong>{str(e)}</strong></p>'
            mail_admins(subject, message, html_message=html_message, fail_silently=False)

            messages.error(request, "A apărut o eroare. Încercați mai târziu.") #EROARE
            return redirect('login') 

    else:
        form = CustomAuthenticationForm()

    return render(request, 'lab_3/login.html', {'form': form})
        
### Logout ###

from django.contrib.auth import logout

def logout_view(request):
    if request.user.has_perm('lab_3.vizualizeaza_oferta'):
        content_type = ContentType.objects.get_for_model(Oferta)
        permission = Permission.objects.get(codename='vizualizeaza_oferta', content_type=content_type)
        request.user.user_permissions.remove(permission) 
    logout(request)
    messages.info(request, "Te-ai delogat cu succes!")
    return redirect('login')

### Schimbare Parola ###

def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, request.user)
            logger.info(f"Utilizatorul {request.user.username} a schimbat parola cu succes.")
            messages.success(request, 'Parola a fost actualizata')
            return redirect('profil')
        else:
            logger.warning(f"Utilizatorul {request.user.username} a încercat să schimbe parola, dar parolele nu coincid.")
            messages.error(request, 'Exista erori.')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'lab_3/schimba_parola.html', {'form': form})

# Create your views here.

def index(request):
    context = {
        'can_add_masina': request.user.has_perm('lab_3.add_masina'),
    }
    return render(request, 'lab_3/index.html', context)

### Task 2 PROIECT 5 ###

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid(): 
            form_data = form.cleaned_data

            if 'confirmare_email' in form_data:
                del form_data['confirmare_email']

            form_data['mesaj'] = preprocesare_mesaj(form_data['mesaj'])

            varsta = calculeaza_varsta(form_data['data_nasterii'])
            form_data['varsta'] = varsta  
            del form_data['data_nasterii']  

            json_data = json.dumps(form_data)

            timestamp = int(time.time())  
            file_name = f"mesaj_{timestamp}.json"
            file_path = os.path.join('mesaje', file_name)

            os.makedirs('mesaje', exist_ok=True)

           
            with open(file_path, 'w', encoding='utf-8') as json_file:
                json_file.write(json_data)
            return redirect('succes')  
    else:
        form = ContactForm()

    return render(request, 'lab_3/contact.html', {'form': form})

def mesaj_trimis_view(request):
    return render(request, 'lab_3/mesaj_trimis.html')

def profile_view(request):
    if not request.user.is_authenticated:
        return redirect('login')  

    username = request.user.username
    email = request.session.get('email', 'N/A')
    telefon = request.session.get('telefon', 'N/A')
    data_nasterii = request.session.get('data_nasterii', 'N/A')
    gen = request.session.get('gen', 'N/A')
    adresa = request.session.get('adresa', 'N/A')
    cod_postal = request.session.get('cod_postal', 'N/A')

    return render(request, 'lab_3/profil.html', {
        'username': username,
        'email': email,
        'telefon': telefon,
        'data_nasterii': data_nasterii,
        'gen': gen,
        'adresa': adresa,
        'cod_postal': cod_postal,    
    })

### TASK3 PROIECT LAB 5  +++ TASK 2 LAB 8###
def creare_masina(request):
    if not request.user.is_authenticated:
        return redirect('login')  

    if not request.user.has_perm('lab_3.add_masina'): 
        return HttpResponseForbidden(
            render(request, 'lab_3/403.html', {
                'titlu': 'Eroare adaugare produse',
                'mesaj_personalizat': 'Nu ai permisiunea de a adăuga mașini.'
            })
        )
    
    if request.method == 'POST':
        form = MasinaForm(request.POST)
        if form.is_valid():
            masina = form.save(commit=False)  
            masina.save()  
            return redirect('listare_masini')  
    else:
        form = MasinaForm()

    return render(request, 'lab_3/creare_masina.html', {'form': form})

################################################

### TASK 2 LAB 4 ###
def listing(request):
    lista_masini= Masina.objects.all()
    paginator = Paginator(lista_masini,6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "lab_3/list.html", {"page_obj": page_obj})

### TASK 2 LAB 4 ###
def masina_list(request):
    masini = Masina.objects.all()  

    marca = request.GET.get('marca')
    if marca:
        masini = masini.filter(marca__icontains=marca)

    model = request.GET.get('model')
    if model:
        masini = masini.filter(model__icontains=model)

    an_fabricatie = request.GET.get('an_fabricatie')
    if an_fabricatie:
        masini = masini.filter(an_fabricatie=an_fabricatie)

    min_kilometraj = request.GET.get('min_kilometraj')
    max_kilometraj = request.GET.get('max_kilometraj')
    if min_kilometraj:
        masini = masini.filter(kilometraj__gte=min_kilometraj)
    if max_kilometraj:
        masini = masini.filter(kilometraj__lte=max_kilometraj)

    min_pret = request.GET.get('min_pret')
    max_pret = request.GET.get('max_pret')
    if min_pret:
        masini = masini.filter(pret__gte=min_pret)
    if max_pret:
        masini = masini.filter(pret__lte=max_pret)

    dealer = request.GET.get('dealer')
    if dealer:
        masini = masini.filter(dealer__nume__icontains=dealer)

    categorie = request.GET.get('categorie')
    if categorie:
        masini = masini.filter(categorie__nume__icontains=categorie)

    tip_motor = request.GET.get('tip_motor')
    if tip_motor:
        masini = masini.filter(tip_motor__tip_motor=tip_motor)

    marci = Masina.objects.values_list('marca', flat=True).distinct()
    categorii = Categorie.objects.all()
    dealeri = Dealer.objects.all()
    tipuri_motor = TipMotor.objects.all()

    return render(request, 'lab_3/masina_list.html', {
        'masini': masini,
        'marci': marci,
        'categorii': categorii,
        'dealeri': dealeri,
        'tipuri_motor': tipuri_motor,
    })
 
#######################################################
    
### TASK 1 PROIECT Lab 5
def masina_filter(request):

    form = FiltruMasinaForm(request.GET)

    masini = Masina.objects.all()  

    if form.is_valid():
        if form.cleaned_data['marca']:
            masini= masini.filter(marca__icontains=form.cleaned_data['marca'])
        if form.cleaned_data['model']:
            masini= masini.filter(model__icontains=form.cleaned_data['model'])
        if form.cleaned_data['an_fabricatie']:
            masini= masini.filter(an_fabricatie=form.cleaned_data['an_fabricatie'])
        if form.cleaned_data['min_kilometraj']:
            masini= masini.filter(kilometraj__gte=form.cleaned_data['min_kilometraj'])
        if form.cleaned_data['max_kilometraj']:
            masini= masini.filter(kilometraj__lte=form.cleaned_data['max_kilometraj'])
        if form.cleaned_data['min_pret']:
            masini= masini.filter(pret__gte=form.cleaned_data['min_pret'])
        if form.cleaned_data['max_pret']:
            masini= masini.filter(pret__lte=form.cleaned_data['max_pret'])
        if form.cleaned_data['dealer']:
            masini= masini.filter(dealer=form.cleaned_data['dealer'])
        if form.cleaned_data['categorie']:
            masini= masini.filter(categorie=form.cleaned_data['categorie'])
        if form.cleaned_data['tip_motor']:
            masini= masini.filter(tip_motor=form.cleaned_data['tip_motor'])

    return render(request, 'lab_3/masina_filter.html', {'form': form, 'masini': masini})

#########################################################

### LAB 7 TASK 1 ###

from django.core.mail import send_mail
import uuid
from django.template.loader import render_to_string
from django.conf import settings

def trimite_email_confirmare(user):
    url_imagine = f"http://localhost:8000/static/images/image_transparent-Photoroom.png"
    # Linkul de confirmare
    link_confirmare = f"http://localhost:8000/lab_3/confirmare_succes/{user.cod}/"
    html_message = render_to_string('lab_3/email_template.html', {
        'user': user,
        'link_confirmare': link_confirmare,
        'url_imagine': url_imagine,
    })
    # Trimitem e-mailul
    send_mail(
        subject="Confirmare e-mail",
        message="Te rugăm să confirmi adresa ta de e-mail.",  
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
    )
    
def confirma_mail(request, cod):

    user = CustomUser.objects.filter(cod=cod).first()  

    if not user:  
        messages.error(request, "Codul de confirmare este invalid.")

    if user.email_confirmat:
        messages.info(request, "E-mailul a fost deja confirmat.")
    else:
        user.email_confirmat = True  
        user.cod = None  
        user.save()
        messages.success(request, "E-mailul tău a fost confirmat cu succes!")

    return render(request, 'lab_3/confirmare_succes.html', {'user': user})

### TASK 2 LAB 7 ###

from django.db.models import Count
from django.core.mail import EmailMessage
from django.core.mail import send_mass_mail

def promotii_view(request):
    if request.method == 'POST':
        form = PromotieForm(request.POST)

        if form.is_valid():
            promotie = form.save()
            K = 3  

            emailuri = []  

            for dealer in promotie.dealeri.all():
                utilizatori = (
                    Vizualizare.objects.filter(masina__dealer=dealer)
                    .values('user')
                    .annotate(count=Count('user'))
                    .filter(count__gte=K)
                )

                for utilizator in utilizatori:
                    user_id = utilizator['user']
                    vizualizare = Vizualizare.objects.filter(user_id=user_id).first()

                    user_email = vizualizare.user.email
                    user = vizualizare.user

                    if dealer.nume == 'BestCars':
                        subject = f"Promoție specială la {dealer.nume}!"
                        body = render_to_string('lab_3/email_template_promo1.html', {
                            'nume_promo': promotie.nume,
                            'dealer': dealer.nume,
                            'reduceri': promotie.reduceri,
                            'data_expirare': promotie.data_expirare,
                            'user': user,
                        })
                    else:
                        subject = f"Ofertă exclusivă de la {dealer.nume}!"
                        body = render_to_string('lab_3/email_template_promo2.html', {
                            'nume_promo': promotie.nume,
                            'dealer': dealer.nume,
                            'reduceri': promotie.reduceri,
                            'data_expirare': promotie.data_expirare,
                            'user': user,
                        })

                    emailuri.append((subject, body, settings.DEFAULT_FROM_EMAIL, [user_email]))

            send_mass_mail(emailuri, fail_silently=False)

            messages.success(request, "Promoția a fost adăugată și emailurile au fost trimise!")
            return redirect('promotii')

    else:
        form = PromotieForm()
    promotii = Promotie.objects.filter(data_expirare__gte=timezone.now())
    return render(request, 'lab_3/promotii.html', {'form': form, 'promotii': promotii})

### TASK 4 LAB 7 ###

import logging

logger = logging.getLogger('django')

### TASK 1 LAB 8 ###

from django.http import HttpResponse, HttpResponseForbidden

def afisare_pagina2(request):
    if not request.user.has_perm('lab_3.vizualizare_pagina'):
        # Generează pagina de eroare 403
        pagina_eroare = render(request, 'lab_3/403.html', {
            'titlu': 'Acces interzis',
            'mesaj_personalizat': 'Nu aveți permisiunea de a vizualiza această pagină.'
        })
        # Returnează un răspuns 403 cu pagina generată
        return HttpResponseForbidden(pagina_eroare)
    
    # Dacă utilizatorul are permisiunea necesară
    return HttpResponse("Ok, bine, tu ai voie.")

### TASK 3 LAB 8 ###

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

@login_required
def adauga_permisiune_oferta(request):
    content_type = ContentType.objects.get_for_model(Oferta)
    perm = Permission.objects.get(codename='vizualizeaza_oferta', content_type=content_type)

    request.user.user_permissions.add(perm)
    messages.success(request, "Ai primit permisiunea de a vizualiza oferta.") #SUCCES
    
    return redirect('oferta')  


def oferta(request):
    if not request.user.is_authenticated:
        return HttpResponseForbidden(render(request, 'lab_3/403.html', {
            'titlu': 'Eroare afisare oferta',
            'mesaj_personalizat': 'Nu ai voie să vizualizezi oferta.'
        }).content)
    else:
        if request.user.has_perm('lab_3.vizualizeaza_oferta'):
            return render(request, 'lab_3/oferta.html') 
        else:
            return HttpResponseForbidden(render(request, 'lab_3/403.html', {
                'titlu': 'Eroare afisare oferta',
                'mesaj_personalizat': 'Nu ai voie să vizualizezi oferta.'
            }).content)

### TASK 2 LAB 9 SITEMAP ###
def masina_detail(request, id):
    masina = Masina.objects.get(id_masina=id)
    return render(request, 'lab_3/masina.html', {'masina': masina})

from django.http import JsonResponse

def masina_detail_json(request,id):
    masina = Masina.objects.get(id_masina=id)
    
    data = {
        "id": masina.id_masina,
        "marca": masina.marca,
        "model": masina.model,
        "pret": masina.pret,
        "imagine": masina.imagine.url if masina.imagine else "",  
    }
    return JsonResponse(data)


### TASK 2 LAB 10 ###

def cos_virtual(request):
    return render(request, 'lab_3/cosVirtual.html')

###TASK 1 LAB 11 ###

from reportlab.pdfgen import canvas

def fisier_pdf(c):
    user = c.user
    produse = c.produse
    total_pret= c.total_pret
    total_cantitate = c.total_cantitate
    data_comenzii = c.data_comanda

    # Crearea numelui fișierului PDF cu timestamp
    timestamp = int(datetime.timestamp(data_comenzii))
    file_name = f"factura-{timestamp}.pdf"

    # Crearea folderului pentru facturi dacă nu există
    user_folder = os.path.join(settings.MEDIA_ROOT, 'temporar-facturi', user.username)
    os.makedirs(user_folder, exist_ok=True)  # Crează subfolderul utilizatorului, dacă nu există

    # Calea completă către fișierul PDF
    file_path = os.path.join(user_folder, file_name)

    # Crearea fișierului PDF
    p = canvas.Canvas(file_path)
    p.setFont=("Arial", 14)

    # Adăugarea informațiilor în PDF
    p.drawString(10, 800, f"Factura pentru comanda realizată pe {data_comenzii.strftime('%d/%m/%Y %H:%M:%S')}")
    p.drawString(10, 780, f"Nume Utilizator: {user.username}")
    p.drawString(10, 760, f"Email: {user.email}")
    p.drawString(10, 740, f"Total Produse: {total_cantitate}")
    p.drawString(10, 720, f"Total Preț: {total_pret} Euro")

    y_position = 700
    p.drawString(10, y_position, "Produse achiziționate:")
    y_position -= 20

    for produs in produse:
        p.drawString(10, y_position, f"Produs: {produs['nume']} - Cantitate: {produs['cantitate']} - Preț: {produs['pret']} Euro")
        y_position -= 20

    # Adăugarea link-urilor către produsele achiziționate
    for produs in produse:
        link = f"http://localhost:8000/lab_3/masina/{produs['id']}"
        p.drawString(10, y_position, f"Link produs: {link}")
        y_position -= 20

    # Salvarea fișierului PDF
    p.save()

    return file_path
    
def trimite_mail_pdf(user_email, file_path):
    email=EmailMessage(
        subject='Factura pentru comanda ta',
        body='Factura atasata apentru comanda ta. Iti multumim pentru cumparaturi!',
        to=[user_email],
    )
    email.attach_file(file_path)
    email.send()

def procesare_date(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Trebuie să fii autentificat pentru a plasa o comandă.'})
    
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        produse_in_cos = data['produse']  # Produsele din coș
        total_pret = data['total_pret']
        total_cantitate = data['total_cantitate']
        
        # Salvăm comanda în baza de date
        comanda = Comanda.objects.create(
            user=request.user,
            produse=produse_in_cos,
            total_pret=total_pret,
            total_cantitate=total_cantitate,
        )

        # Generăm factura
        file_path = fisier_pdf(comanda)

        # Trimitem factura pe e-mail
        trimite_mail_pdf(request.user.email, file_path)

        # Golește coșul virtual
        request.session['cos_virtual'] = []

        # Returnează un răspuns de succes
        return JsonResponse({'status': 'success', 'message': 'Comanda a fost procesată cu succes! Factura a fost trimisă prin e-mail.'})
    return JsonResponse({'status': 'error', 'message': 'Metodă invalidă.'})
        
    
    
