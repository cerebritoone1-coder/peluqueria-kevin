import webbrowser
import urllib.parse
import os
def enviar_whatsapp(mensaje):
    numero = os.getenv('WHATSAPP_NUMBER', '8096192002')
    mensaje_codificado = urllib.parse.quote(mensaje)
    url = f'https://wa.me/1{numero}?text={mensaje_codificado}'
    webbrowser.open(url)
    return url
