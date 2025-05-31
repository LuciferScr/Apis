import importlib
import os
import string
from pyrogram import Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import time
import csv
from bino import get_bin_info
from datetime import datetime, timedelta
import random
import importlib.util 
import types
from pyrogram import Client, filters

api_id = 26732763
api_hash = "db528630e35298a5cefd8f51a123324b"
bot_token = "7928602739:AAFL6NBfxwDq8L3pg576bgjabdSfcfqEn2g"

archivo_csv = 'bins.csv'
chat_send = [-1001983783501] 

app = Client("NewScrapp", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

def calcular_verificador_luhn(numero):
    digitos = [int(digito) for digito in numero]
    digitos.reverse()

    suma = 0
    for i in range(len(digitos)):
        if i % 2 == 0:
            digito_doble = digitos[i] * 2
            suma += digito_doble - 9 if digito_doble > 9 else digito_doble
        else:
            suma += digitos[i]

    return (10 - (suma % 10)) % 10


def generar_tarjeta(bin_cc):
    tarjetas_generadas = []
    bin_generado = str(bin_cc).rjust(6, '0')

    resto_tarjeta = ''.join(random.choice('0123456789') for _ in range(9))

    numero_tarjeta = bin_generado + resto_tarjeta

    digito_verificacion = calcular_verificador_luhn(numero_tarjeta)

    tarjeta_formateada = f"{numero_tarjeta}{digito_verificacion}"

    fecha_expiracion = (datetime.now() + timedelta(days=random.randint(365, (2030 - datetime.now().year) * 365))).strftime("%m|%Y")

    primer_digito = str(bin_cc)[0]
    if primer_digito == '3':
        cvv = random.randint(1000, 9999)  
    else:
        cvv = random.randint(100, 999)  
        
    tarjeta_formateada += f"|{fecha_expiracion}|{cvv}"

    tarjetas_generadas.append(tarjeta_formateada)

    return tarjetas_generadas

def find_between(data: str, first: str, last: str) -> str:
    # Busca una subcadena dentro de una cadena, dados dos marcadores
    if not isinstance(data, str):
        raise TypeError("El primer argumento debe ser una cadena de texto.")
    
    try:
        start_index = data.index(first) + len(first)
        end_index = data.index(last, start_index)
        return data[start_index:end_index]
    except ValueError:
        return ''
    
def get_random_string(length):
    # Genera una cadena de texto aleatoria.
    letters = string.ascii_letters + string.digits
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


def obtener_numero_aleatorio():
    with open(archivo_csv, newline='', encoding='utf-8') as archivo:
        lector_csv = csv.reader(archivo)
        encabezados = next(lector_csv) 

        lineas_filtradas = [linea for linea in lector_csv if linea[0].startswith(('5', '6', '4'))]

        if lineas_filtradas:
            info_aleatoria = random.choice(lineas_filtradas)
            
            numero_aleatorio = dict(zip(encabezados, info_aleatoria)).get('number')
            return numero_aleatorio
        else:
            return None

def enviar_conectado():
    while True:
        
        for chat_id in chat_send:
          
                bin_cc = obtener_numero_aleatorio()
                x = get_bin_info(bin_cc)
                bank = x.get("bank_name")
                
                if bank is None or not bank.strip():
                        pass
                else:

                    tarjetas_generadas = generar_tarjeta(bin_cc)
                    for i, tarjeta in enumerate(tarjetas_generadas, start=1):
                        mes = random.randint(25, 35)

                        primeros_8 = tarjeta[:8]
                        primeros_12 = tarjeta[:12]
                        
                        mes = f"{random.randint(1, 12):02d}"  
                        ano = random.randint(2025, 2030) 

                        cvv = f"{random.randint(100, 999)}"

                        extra1 = f"{primeros_12}xxxx|{mes}|{ano}"
                        
                        digitos_aleatorios = ''.join([str(random.randint(0, 9)) for _ in range(4)])
                        extra2 = f"{primeros_8}{digitos_aleatorios}xxxx|{mes}|{ano}"

                        text = f"""
⛈ New Card!
━ • ━━━━━━━━━━━━ • ━
•Card: <code>{tarjeta}</code>
•Response: <code>Card Issuer Declined CVV!</code>
━ • ━━━━━━━━━━━━ • ━
•Info = <code>{x.get("type")}</code> <code>{x.get("vendor")}</code> <code>{x.get("level")}</code>
•Country = <code>{x.get("country")} {x.get("flag")}</code>
•Bank = <code>{x.get("bank_name")}</code> 
━ • ━━━━━━━━━━━━ • ━
<code>{extra1}</code>
<code>{extra2}</code>
━ • ━━━━━━━━━━━━ • ━"""


                    print(f"Tarjeta {i}: {tarjeta}")
                    app.send_message(chat_id, text)

  
        time.sleep(10)  

if __name__ == "__main__":
    app.start()
    print("Scrapper + Bot Iniciados con exito!")
    app.run(enviar_conectado())
