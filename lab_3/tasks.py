
import django
import os
from lab_3.models import Masina, CustomUser
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apl_web.settings')
django.setup()

from django.utils import timezone


def sterge_utilizatori_neconfirmati():
    utilizatori = CustomUser.objects.filter(email_confirmat=False)
    count, _ = utilizatori.delete()
    print(f'{count} utilizatori neconfirmați au fost șterși.')
    
def trimite_newsletter():
    X = 60  # minute
    utilizatori = CustomUser.objects.filter(date_joined__lte=timezone.now() - timedelta(minutes=X))
    for user in utilizatori:
        send_mail(
            subject='Newsletter - Ofertă Specială!',
            message='Salut! Nu rata oferta noastră specială...',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        print(f"Newsletter trimis către {user.email}")
        
### TASK 3 LAB 9 ###


# Task 1: Curățare a sesiunilor expirate (la fiecare 60 de minute)
def stergere_sesiuni_expirate():
    M=8640
    limita= timezone.now()- timedelta(minutes=M)
    print(timezone.now())
    utilizatori_inactivi = CustomUser.objects.filter(last_login__lte=limita)
    count = utilizatori_inactivi.update(is_active=False)
    print(f'{count} utilizatori au fost marcați ca inactivi pentru inactivitate mai mare de {M} minute.')
    
# Task 2: Verificare stoc mașini (dacă stocul scade sub 2, trimite un e-mail administratorului)
def verifica_stoc_masini():
    prag_stoc = 2  
    masini_scazute = Masina.objects.filter(stoc__lt=prag_stoc)
    if masini_scazute.exists():
        admin_emails = [email for _, email in settings.ADMINS]
        for masina in masini_scazute:
            send_mail(
                subject='Atenție: Stoc scăzut de mașini!',
                message=f"Stocul pentru mașina {masina.marca} {masina.model} a scăzut sub {prag_stoc} unități. Vă rugăm să actualizați stocul.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=admin_emails,  
                fail_silently=False,
            )
            print(f"Notificare trimisă pentru mașina {masina.marca} {masina.model}.")
