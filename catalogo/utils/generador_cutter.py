import json
import os
import bisect
import unicodedata

class CutterSanbornGenerator:
    def __init__(self):
        ruta_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_json = os.path.join(ruta_actual, 'cutter_sanborn.json')

        with open(ruta_json, 'r', encoding='utf-8') as file:
            datos_crudos = json.load(file)

            # Voltea el orden del Json
            datos_preparados = [(item[1].lower(), item[0]) for item in datos_crudos]

            datos_ordenados = sorted(datos_preparados, key=lambda x: x[0])

            self.claves = [item[0] for item in datos_ordenados] # Letras
            self.valores = [item[1] for item in datos_ordenados] # Números

    def _normalizar_texto(self, texto):
        texto = texto.lower().strip()
        texto = ''.join(c for c in unicodedata.normalize('NFD', texto)
                        if unicodedata.category(c) != 'Mn')
        return texto
    
    def generar_codigo(self, apellido_autor, titulo=""):
        if not apellido_autor:
            return ""
        apellido_normalizado = self._normalizar_texto(apellido_autor)
        apellido_clave = apellido_normalizado.split()[0]

        # Búsqueda Binaria
        posicion = bisect.bisect_right(self.claves, apellido_clave) - 1
        if posicion < 0:
            numero_cutter = "100"
        else:
            numero_cutter = self.valores[posicion]
        if apellido_clave.startswith('sc'):
            letra_inicial = apellido_clave[:3].capitalize()
       # elif apellido_clave[0] in 'aeious':
            #letra_inicial = apellido_clave[:2].capitalize() if len(apellido_clave) > 1 else apellido_clave.capitalize()
        else:
            letra_inicial = apellido_clave[0].upper()
        
        libristica = ""
        if titulo:
            titulo_normalizado = self._normalizar_texto(titulo)
            libristica = titulo_normalizado[0].lower()

        # Armar y Retornar el código
        return f"{letra_inicial}{numero_cutter}{libristica}"

generador = CutterSanbornGenerator()