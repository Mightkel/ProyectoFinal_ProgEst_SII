#Reproductor de música — servidor Flask.

import os
from flask import Flask, jsonify, render_template, request, send_from_directory
from modulos import almacenamiento, biblioteca, grafo, historial, indice, ordenacion, playlist

app = Flask(__name__)

RAIZ = os.path.dirname(os.path.abspath(__file__))
CARPETA_AUDIO = os.path.join(RAIZ, "musica")
CARPETA_PORTADAS = os.path.join(RAIZ, "portadas")
EXT_AUDIO = (".mp3", ".ogg", ".wav", ".m4a")
EXT_IMAGEN = (".jpg", ".jpeg", ".png", ".webp")


def buscar_archivo(carpeta, extensiones, cancion):
    """Nombre del archivo de esa carpeta que corresponde a la canción, o None."""
    if not os.path.isdir(carpeta):
        return None
    claves = {biblioteca.normalizar(cancion["titulo"]),
              biblioteca.normalizar(f'{cancion["artista"]} - {cancion["titulo"]}'),
              str(cancion["id"])}
    for nombre in sorted(os.listdir(carpeta)):
        base, extension = os.path.splitext(nombre)
        if extension.lower() in extensiones and biblioteca.normalizar(base) in claves:
            return nombre
    return None


def con_archivos(cancion):
    """Copia de la canción con las marcas 'audio' y 'portada' (no se guardan en el JSON)."""
    return {**cancion,
            "audio": buscar_archivo(CARPETA_AUDIO, EXT_AUDIO, cancion) is not None,
            "portada": buscar_archivo(CARPETA_PORTADAS, EXT_IMAGEN, cancion) is not None}


def guardar_archivo(carpeta, extensiones, id_cancion):
    """Guarda el archivo recibido como <id>.<ext>, reemplazando el anterior. Devuelve (ok, mensaje)."""
    archivo = request.files.get("archivo")
    if archivo is None or not archivo.filename:
        return False, "No se recibió ningún archivo"
    extension = os.path.splitext(archivo.filename)[1].lower()
    if extension not in extensiones:
        return False, "Formato no admitido. Usa " + ", ".join(e[1:] for e in extensiones)
    os.makedirs(carpeta, exist_ok=True)
    for nombre in os.listdir(carpeta):
        if os.path.splitext(nombre)[0] == str(id_cancion):
            os.remove(os.path.join(carpeta, nombre))
    archivo.save(os.path.join(carpeta, f"{id_cancion}{extension}"))
    return True, ""


# Todo el estado del programa vive en este diccionario (no hay objetos propios).
estado = {}


# ---------------------------------------------------------------- carga y guardado
def cargar_estado():
    canciones = almacenamiento.cargar("canciones.json", [])
    mapa = almacenamiento.cargar("grafo.json", {})
    datos_lista = almacenamiento.cargar("playlist.json", {"ids": [], "actual": None, "circular": False})
    pila = almacenamiento.cargar("historial.json", [])

    validos = {c["id"] for c in canciones}
    ids = [i for i in datos_lista["ids"] if i in validos]
    actual = datos_lista["actual"] if datos_lista["actual"] in validos else None

    grafo.sincronizar(mapa, canciones)
    estado["canciones"] = canciones
    estado["arbol"] = indice.construir(canciones)          # el índice no se guarda: se reconstruye
    estado["mapa"] = mapa
    estado["lista"] = playlist.desde_lista(ids, actual)    # igual: la cadena se reconstruye desde ids
    estado["circular"] = bool(datos_lista["circular"])
    estado["pila"] = [i for i in pila if i in validos]


def guardar_todo():
    almacenamiento.guardar("canciones.json", estado["canciones"])
    almacenamiento.guardar("grafo.json", estado["mapa"])
    almacenamiento.guardar("playlist.json", {
        "ids": playlist.a_lista(estado["lista"]),
        "actual": playlist.id_actual(estado["lista"]),
        "circular": estado["circular"],
    })
    almacenamiento.guardar("historial.json", estado["pila"])

cargar_estado()

if __name__ == "__main__":
    app.run(debug=True)