import schedule, os
import time, django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apl_web.settings')
django.setup()

from lab_3 import tasks


    
def run_scheduler():
    schedule.every(5).minutes.do(tasks.sterge_utilizatori_neconfirmati)  # taskul de ștergere la fiecare 2 minute
    schedule.every().thursday.at("21:15").do(tasks.trimite_newsletter)  # taskul de trimis newsletter la ora 9:00, în fiecare luni
    schedule.every(2).minutes.do(tasks.stergere_sesiuni_expirate)
    schedule.every().thursday.at("21:23").do(tasks.verifica_stoc_masini)
    while True:
        schedule.run_pending()
        time.sleep(1)  # Verifică la fiecare secundă dacă există taskuri programate
        
if __name__ == "__main__":
    try:
        run_scheduler()
    except KeyboardInterrupt:
        print("Scheduler oprit manual.")
        sys.exit()

