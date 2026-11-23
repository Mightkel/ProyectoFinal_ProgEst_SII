#Ordenación paso a paso. Se mueven índices para conservar los datos originales.
from modulos.biblioteca import formatear_duracion, normalizar


def info_algoritmos():
    return [
        {"clave": "burbuja", "nombre": "Burbuja",
         "descripcion": "Compara vecinos y los intercambia. En cada pasada, el mayor queda al final.",
         "mejor": "O(n)", "promedio": "O(n²)", "peor": "O(n²)", "estable": True},
        {"clave": "seleccion", "nombre": "Selección",
         "descripcion": "Busca el menor de los elementos pendientes y lo coloca en la siguiente posición.",
         "mejor": "O(n²)", "promedio": "O(n²)", "peor": "O(n²)", "estable": False},
        {"clave": "insercion", "nombre": "Inserción",
         "descripcion": "Inserta cada elemento en el lugar que le corresponde dentro de la parte ordenada.",
         "mejor": "O(n)", "promedio": "O(n²)", "peor": "O(n²)", "estable": True},
        {"clave": "rapida", "nombre": "Quicksort",
         "descripcion": "Elige el último elemento como pivote, separa los menores y ordena ambos lados.",
         "mejor": "O(n log n)", "promedio": "O(n log n)", "peor": "O(n²)", "estable": False},
    ]


def clave_cancion(cancion, campo):
    if campo == "duracion":
        return cancion["duracion"]
    if campo == "titulo":
        return normalizar(cancion["titulo"])
    return normalizar(cancion[campo]), normalizar(cancion["titulo"])


def texto_corto(cancion, campo):
    if campo == "duracion":
        return formatear_duracion(cancion["duracion"])
    texto = cancion[campo]
    return texto if len(texto) <= 16 else texto[:15] + "…"


def _comparar(claves, orden, pasos, i, j, descendente):
    #True si el elemento de i debe ir después del de j.
    pasos.append({"tipo": "comparar", "i": i, "j": j})
    a, b = claves[orden[i]], claves[orden[j]]
    return a < b if descendente else a > b


def _intercambiar(orden, pasos, i, j):
    if i != j:
        orden[i], orden[j] = orden[j], orden[i]
        pasos.append({"tipo": "intercambiar", "i": i, "j": j})


def _fijar(pasos, i):
    pasos.append({"tipo": "fijar", "i": i})


def _burbuja(claves, orden, pasos, descendente):
    for fin in range(len(orden) - 1, 0, -1):
        cambio = False
        for i in range(fin):
            if _comparar(claves, orden, pasos, i, i + 1, descendente):
                _intercambiar(orden, pasos, i, i + 1)
                cambio = True
        _fijar(pasos, fin)
        if not cambio:
            for i in range(fin):
                _fijar(pasos, i)
            return
    if orden:
        _fijar(pasos, 0)


def _seleccion(claves, orden, pasos, descendente):
    for i in range(len(orden)):
        menor = i
        for j in range(i + 1, len(orden)):
            if _comparar(claves, orden, pasos, menor, j, descendente):
                menor = j
        _intercambiar(orden, pasos, i, menor)
        _fijar(pasos, i)


def _insercion(claves, orden, pasos, descendente):
    for i in range(1, len(orden)):
        j = i
        while j > 0:
            if not _comparar(claves, orden, pasos, j - 1, j, descendente):
                break
            _intercambiar(orden, pasos, j - 1, j)
            j -= 1
    #El prefijo está ordenado en cada vuelta, pero sus posiciones aún pueden cambiar.
    for i in range(len(orden)):
        _fijar(pasos, i)


def _rapida(claves, orden, pasos, descendente, inicio, fin):
    if inicio > fin:
        return
    if inicio == fin:
        _fijar(pasos, inicio)
        return
    pasos.append({"tipo": "pivote", "i": fin})
    posicion = inicio
    for j in range(inicio, fin):
        if not _comparar(claves, orden, pasos, j, fin, descendente):
            _intercambiar(orden, pasos, posicion, j)
            posicion += 1
    _intercambiar(orden, pasos, posicion, fin)
    _fijar(pasos, posicion)
    _rapida(claves, orden, pasos, descendente, inicio, posicion - 1)
    _rapida(claves, orden, pasos, descendente, posicion + 1, fin)


def ordenar(claves, algoritmo="burbuja", descendente=False):
    if algoritmo not in ("burbuja", "seleccion", "insercion", "rapida"):
        return None
    orden = list(range(len(claves)))
    pasos = []
    if algoritmo == "burbuja":
        _burbuja(claves, orden, pasos, descendente)
    elif algoritmo == "seleccion":
        _seleccion(claves, orden, pasos, descendente)
    elif algoritmo == "insercion":
        _insercion(claves, orden, pasos, descendente)
    else:
        _rapida(claves, orden, pasos, descendente, 0, len(orden) - 1)
    return {
        "orden": orden,
        "pasos": pasos,
        "comparaciones": sum(p["tipo"] == "comparar" for p in pasos),
        "intercambios": sum(p["tipo"] == "intercambiar" for p in pasos),
    }
