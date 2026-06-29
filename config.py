import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-12345')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///peluquria.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de WhatsApp
    WHATSAPP_NUMBER = os.getenv('WHATSAPP_NUMBER', '8095555555')
    
    # Horarios disponibles
    HORARIOS = ['7:30', '8:00', '8:30', '9:00', '9:30', '10:00', '10:30']
    
    # Servicios y precios
    SERVICIOS = {
        'ceja': {'nombre': 'Solo sacarse la ceja', 'precio': 100},
        'afeitarse': {'nombre': 'Afeitarse', 'precio': 300},
        'recortarse': {'nombre': 'Recortarse', 'precio': 300},
        'recortarse_afeitarse': {'nombre': 'Recortarse y afeitarse', 'precio': 400},
        'cerquillo': {'nombre': 'El cerquillo', 'precio': 200}
    }