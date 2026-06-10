import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from catalogo.models import Libro
from .models import HistorialBusqueda

def obtener_recomendaciones(usuario):
    # 1. Obtener todos los libros (Optimizado)
    qs = Libro.objects.all().prefetch_related('autores', 'generos')
    if not qs.exists(): return []
    
    data = []
    for x in qs:
        # Unimos autores y géneros en strings legibles
        nombres_autores = " ".join([a.nombre_completo for a in x.autores.all()])
        nombres_generos = " ".join([g.nombre for g in x.generos.all()])
        
        # Sopa de palabras clave
        contenido = f"{x.titulo} {nombres_autores} {nombres_generos} {x.cutter} {x.descripcion}"
        
        data.append({
            'id': x.id, 
            'content': contenido
        })

    df = pd.DataFrame(data)
    
    spanish_stop_words = [
        'de', 'la', 'que', 'el', 'en', 'y', 'a', 'los', 'del', 'se', 'las', 'por', 'un', 'para', 
        'con', 'no', 'una', 'su', 'al', 'lo', 'como', 'más', 'pero', 'sus', 'le', 'ya', 'o', 
        'este', 'sí', 'porque', 'esta', 'entre', 'cuando', 'muy', 'sin', 'sobre', 'también', 
        'me', 'hasta', 'hay', 'donde', 'quien', 'desde', 'todo', 'nos', 'durante', 'todos', 
        'uno', 'les', 'ni', 'contra', 'otros', 'ese', 'eso', 'ante', 'ellos', 'e', 'esto', 
        'mí', 'antes', 'algunos', 'qué', 'unos', 'yo', 'otro', 'otras', 'otra', 'él', 'tanto', 
        'esa', 'estos', 'mucho', 'quienes', 'nada', 'muchos', 'cual', 'poco', 'ella', 'estar', 
        'estas', 'algunas', 'algo', 'nosotros', 'mi', 'mis', 'tú', 'te', 'ti', 'tu', 'tus', 
        'ellas', 'nosotras', 'vosotros', 'vosotras', 'os', 'mío', 'mía', 'míos', 'mías', 
        'tuyo', 'tuya', 'tuyos', 'tuyas', 'suyo', 'suya', 'suyos', 'suyas', 'nuestro', 
        'nuestra', 'nuestros', 'nuestras', 'vuestro', 'vuestra', 'vuestros', 'vuestras', 
        'esos', 'esas', 'estoy', 'estás', 'está', 'estamos', 'estáis', 'están', 'esté', 
        'estés', 'estemos', 'estéis', 'estén', 'estaré', 'estarás', 'estará', 'estaremos', 
        'estaréis', 'estarán', 'estaría', 'estarías', 'estaríamos', 'estaríais', 'estarían', 
        'estaba', 'estabas', 'estábamos', 'estabais', 'estaban', 'estuve', 'estuviste', 
        'estuvo', 'estuvimos', 'estuvisteis', 'estuvieron', 'hubiera', 'hubieras', 'hubiéramos', 
        'hubierais', 'hubieran', 'hubiese', 'hubieses', 'hubiésemos', 'hubieseis', 'hubiesen', 
        'habiendo', 'estado', 'estada', 'estados', 'estadas', 'estad'
    ]


    tfidf = TfidfVectorizer(stop_words=spanish_stop_words)
    
    # 2. Matriz Matemática
    tfidf_matrix = tfidf.fit_transform(df['content'])
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    
    # 3. Obtener perfil del usuario
    indices_recomendados = []
    ultimo_interes = HistorialBusqueda.objects.filter(usuario=usuario).order_by('-fecha').first()
    
    if ultimo_interes:
        term = ultimo_interes.termino_busqueda
        
        # Buscamos coincidencias
        matches = df[df['content'].str.contains(term, case=False, na=False)]
        
        if not matches.empty:
            idx = matches.index[0]
            sim_scores = list(enumerate(cosine_sim[idx]))
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            indices_recomendados = [i[0] for i in sim_scores[1:6]]
    
    # 4. Fallback
    if not indices_recomendados:
        return Libro.objects.all().order_by('-fecha_creacion')[:5]
        
    ids = df.iloc[indices_recomendados]['id'].tolist()
    return Libro.objects.filter(id__in=ids)