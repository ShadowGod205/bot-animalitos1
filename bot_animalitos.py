import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import threading

# --- CONFIGURACIÓN ---
TOKEN = "8543705872:AAH97lAXGm7siInXCXPXITRXvm7saTDEMGo"
CHAT_ID = "8516718046"

# Configuración detallada por sorteo
CONFIG_SORTEOS = {
    "La Granjita 🐾": {
        "url": "https://lagranjita.com/",
        "inicio": 8, "fin": 19, "minuto_inicio": 0
    },
    "Lotto Activo 🎰": {
        "url": "https://www.lottoactivo.com/resultados/animalitos/",
        "inicio": 8, "fin": 19, "minuto_inicio": 0
    },
    "Guacharo Activo 🦅": {
        "url": "https://loteriadehoy.com/animalito/guacharoactivo/resultados/",
        "inicio": 8, "fin": 19, "minuto_inicio": 0
    },
    "Lotto Rey 👑": {
        "url": "https://loteriadehoy.com/animalito/lottorey/resultados/",
        "inicio": 8, "fin": 19, "minuto_inicio": 30 # Empieza 8:30, termina 7:30 (19:30)
    }
}

historial = {nombre: None for nombre in CONFIG_SORTEOS}

def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mensaje, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=payload, timeout=10)
    except:
        pass

def obtener_animalito(nombre, url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')

        if "lagranjita" in url:
            elemento = soup.select_one('.container-animalito-nombre, .animal-name')
        else:
            elementos = soup.find_all(['h3', 'strong', 'b'])
            elemento = next((e for e in elementos if 1 < len(e.text.strip()) < 15 and "PUBLICIDAD" not in e.text.upper()), None)
        
        return elemento.get_text(strip=True).upper() if elemento else None
    except:
        return None

def monitorear_con_horario(nombre, config):
    print(f"✅ Hilo iniciado para {nombre}")
    
    while True:
        ahora = datetime.now()
        hora = ahora.hour
        minuto = ahora.minute
        
        # Validación de horario (8:00 AM a 7:00 PM o 8:30 AM a 7:30 PM)
        esta_en_horario = False
        
        if nombre == "Lotto Rey 👑":
            # Especial para Lotto Rey: 8:30 AM a 7:30 PM (19:30)
            if (hora == 8 and minuto >= 30) or (8 < hora < 19) or (hora == 19 and minuto <= 30):
                esta_en_horario = True
        else:
            # Estándar: 8:00 AM a 7:00 PM (19:00)
            if 8 <= hora <= 19:
                esta_en_horario = True

        if esta_en_horario:
            # Si estamos en los primeros 10 minutos de la hora (donde sale el resultado)
            # Para Lotto Rey, se considera el desfase de 30 min.
            minuto_objetivo = config["minuto_inicio"]
            
            # Revisar intensamente si estamos cerca del minuto del sorteo
            animal_actual = obtener_animalito(nombre, config["url"])
            
            if animal_actual and animal_actual != historial[nombre]:
                mensaje = (
                    f"🎯 *RESULTADO OFICIAL* 🎯\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"🏢 *Lotería:* {nombre}\n"
                    f"🐾 *Animal:* {animal_actual}\n"
                    f"🕒 *Hora:* {ahora.strftime('%I:%M %p')}\n"
                    f"━━━━━━━━━━━━━━━━━━"
                )
                enviar_telegram(mensaje)
                historial[nombre] = animal_actual
                print(f"[{ahora.strftime('%H:%M')}] {nombre} -> {animal_actual}")
                
                # Después de encontrarlo, descansa 15 minutos para no repetir
                time.sleep(900)
            else:
                # Si no ha salido, revisar cada 45 segundos
                time.sleep(45)
        else:
            # Si está fuera de horario, avisar una vez y dormir hasta que falte poco para las 8am
            print(f"💤 {nombre} fuera de horario. Durmiendo...")
            time.sleep(600) # Revisa cada 10 min si ya amaneció

# --- LANZAMIENTO ---
print(f"🚀 Bot Profesional @ResultadosVIPbot iniciado")
enviar_telegram("🕒 *Sistema de Horarios Activado*\n\n✅ 8:00 AM - 7:00 PM (Sorteos Estándar)\n✅ 8:30 AM - 7:30 PM (Lotto Rey)")

for nombre, config in CONFIG_SORTEOS.items():
    t = threading.Thread(target=monitorear_con_horario, args=(nombre, config))
    t.daemon = True
    t.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Bot apagado.")
