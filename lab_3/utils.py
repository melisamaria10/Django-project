import re
from datetime import datetime

def preprocesare_mesaj(mesaj):
    mesaj = mesaj.replace("\n", " ")  
    mesaj = re.sub(r'\s+', ' ', mesaj).strip()
    return mesaj

def calculeaza_varsta(data_nasterii):
    today = datetime.today()
    ani = today.year - data_nasterii.year
    luni = today.month - data_nasterii.month
    
    if luni < 0:
        ani -= 1
        luni += 12
    
    return f"{ani} ani si {luni} luni"
