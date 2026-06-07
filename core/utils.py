import os
import cloudinary.uploader

def guardar_archivo_sistema(archivo, carpeta_destino):
    if os.getenv('ENVIRONMENT') == 'production':
        try:
            resultado = cloudinary.uploader.upload(archivo, folder=carpeta_destino, resource_type='auto')
            return resultado['secure_url']
        except Exception:
            return archivo
    else:
        return archivo