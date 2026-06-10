import os
import cloudinary.uploader
from supabase import create_client, Client

# CONFIGURACION DE SUPABASE
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase_client = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)

def guardar_archivo_sistema(archivo, carpeta_destino):
    if not archivo:
        return None
    if os.getenv('ENVIRONMENT') != 'production':
        return archivo
    
    nombre_archivo = archivo.name.lower()
    extensiones_imagen = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
    es_imagen = any(nombre_archivo.endswith(ext) for ext in extensiones_imagen)

    try:
        # CASO A: Es una imagen --> se procesa con Cloudinary
        if es_imagen:
            resultado = cloudinary.uploader.upload(
                archivo, 
                folder=carpeta_destino,
                resource_type='image'
            )
            return resultado['secure_url']
        # Caso B: Es un documento --> se procesa con Supabase
        else:
            if not supabase_client:
                print("Error: Supabase no está configurado en las variables de entorno")
                return archivo
            
            bucket_name = "repositorio"
            nombre_limpio = archivo.name.replace(" ", "_")
            ruta_en_supabase = f"{carpeta_destino}/{nombre_limpio}"
            archivo.seek(0)
            archivo_bytes = archivo.read()

            content_type = "application/pdf" if nombre_limpio.endswith('.pdf') else "application/octet-stream"

            supabase_client.storage.from_(bucket_name).upload(
                path=ruta_en_supabase,
                file=archivo_bytes,
                file_options={"x-upsert": "true", "content-type": content_type}
            )

            url_publica = supabase_client.storage.from_(bucket_name).get_public_url(ruta_en_supabase)
            return url_publica
    except Exception as e:
        print(f"Error critico en guardar_archivo_SISTEMA: {str(e)}")
        return archivo