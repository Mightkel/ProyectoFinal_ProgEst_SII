#Medición a posteriori del ordenamiento burbuja de Ritmo.
#Ejecutar desde la raíz del repositorio:  python analisis/medir_burbuja.py
#Opcional: python analisis/medir_burbuja.py 250 500 1000   (otros tamaños)
#Genera analisis/resultados_<version de Python>.csv con la mediana de 5 listas.
#Necesita unos 3 GB de RAM libres para verificar las listas de 3000 elementos.
import csv
import gc
import os
import platform
import random
import statistics
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modulos import ordenacion

TAMANOS = [250, 500, 1000, 1500, 2000, 2500, 3000]
LISTAS_POR_CASO = 5
TIEMPO_MINIMO = 0.2      # segundos acumulados por lista
VALOR_MAXIMO = 1_000_000


def burbuja_sin_pasos(claves):
    #Mismos ciclos que ordenacion._burbuja, sin guardar los pasos de la animación.
    orden = list(range(len(claves)))
    comparaciones = intercambios = 0
    for fin in range(len(orden) - 1, 0, -1):
        cambio = False
        for i in range(fin):
            comparaciones += 1
            if claves[orden[i]] > claves[orden[i + 1]]:
                orden[i], orden[i + 1] = orden[i + 1], orden[i]
                intercambios += 1
                cambio = True
        if not cambio:
            break
    return orden, comparaciones, intercambios


def generar(distribucion, n, semilla):
    azar = random.Random(semilla)
    #Valores distintos: así la lista inversa da exactamente n(n-1)/2 intercambios.
    datos = azar.sample(range(VALOR_MAXIMO), n)
    if distribucion == "ordenada":
        datos.sort()
    elif distribucion == "inversa":
        datos.sort(reverse=True)
    return datos


def comprobar(claves):
    #La versión medida debe hacer lo mismo que ordenacion.ordenar() de Ritmo.
    orden, comp, inter = burbuja_sin_pasos(claves)
    ritmo = ordenacion.ordenar(claves, "burbuja")
    assert orden == ritmo["orden"], "orden distinto"
    assert comp == ritmo["comparaciones"], "comparaciones distintas"
    assert inter == ritmo["intercambios"], "intercambios distintos"
    del ritmo
    gc.collect()    #la lista de pasos de Ritmo puede ocupar ~2 GB con n = 3000


def medir(claves):
    #Repite el ordenamiento hasta sumar TIEMPO_MINIMO y devuelve ms por ejecución.
    repeticiones = 0
    inicio = time.perf_counter()
    while True:
        burbuja_sin_pasos(claves)
        repeticiones += 1
        transcurrido = time.perf_counter() - inicio
        if transcurrido >= TIEMPO_MINIMO:
            return transcurrido / repeticiones * 1000


def main():
    tamanos = [int(x) for x in sys.argv[1:]] or TAMANOS
    version = platform.python_version()
    print(f"Python {version} | {platform.processor() or platform.machine()} | {platform.system()} {platform.release()}")
    filas = []
    for distribucion, caso in (("ordenada", "mejor"), ("aleatoria", "promedio"), ("inversa", "peor")):
        for n in tamanos:
            tiempos, comps, inters = [], [], []
            for semilla in range(LISTAS_POR_CASO):
                claves = generar(distribucion, n, semilla)
                if semilla == 0:
                    comprobar(claves)    #una verificación por caso y tamaño
                tiempos.append(medir(claves))
                _, comp, inter = burbuja_sin_pasos(claves)
                comps.append(comp)
                inters.append(inter)
            fila = {"caso": caso, "distribucion": distribucion, "n": n,
                    "mediana_ms": round(statistics.median(tiempos), 4),
                    "comparaciones_prom": statistics.mean(comps),
                    "intercambios_prom": statistics.mean(inters)}
            filas.append(fila)
            print(f"{caso:9} n={n:5}  {fila['mediana_ms']:10.4f} ms  "
                  f"comp={fila['comparaciones_prom']:.0f}  inter={fila['intercambios_prom']:.0f}")
    salida = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"resultados_{version}.csv")
    with open(salida, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=list(filas[0]))
        escritor.writeheader()
        escritor.writerows(filas)
    print("Resultados guardados en", salida)


if __name__ == "__main__":
    main()
