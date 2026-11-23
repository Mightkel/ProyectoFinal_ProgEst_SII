# Ritmo

Ritmo es un reproductor web para organizar música, armar una playlist y descubrir
artistas relacionados. Es el proyecto final de Programación Estructurada y está
hecho con Python y Flask.

## Problema y objetivo

Una colección de canciones necesita algo más que una carpeta: buscar títulos,
cambiar el orden de reproducción y recordar lo que se escuchó. El objetivo de
Ritmo es reunir esas tareas en una aplicación local y aplicar estructuras de datos
dinámicas para resolverlas. Está dirigido a personas que quieren organizar y
reproducir su propia colección de música.

## Integrantes

| Integrante | GitHub |
| --- | --- |
| Maykel Cruz | [Mightkel](https://github.com/Mightkel) / [MaykelCruz](https://github.com/MaykelCruz) |
| Humberto René Ruiz Rodríguez | [ur1ii](https://github.com/ur1ii) |
| José Alfredo Baca Moreno | [JaBaca67](https://github.com/JaBaca67) |
| Justin | [justin1021208](https://github.com/justin1021208) |

## Funciones principales

- Agregar y eliminar canciones de la biblioteca.
- Buscar por título, artista o género.
- Agregar canciones a la playlist, moverlas o dejarlas a continuación de la actual.
- Avanzar, retroceder, mezclar y repetir la playlist.
- Volver a una canción usando el historial de reproducción.
- Conectar artistas con un peso de afinidad y consultar recomendaciones.
- Ver las estructuras en la sección **Bajo el capó**.
- Animar burbuja, selección, inserción y Quicksort; comparar sus operaciones y
  aplicar el orden a la playlist.
- Guardar los cambios en archivos JSON.

## Requisitos e instalación

Se necesita Python 3.10 o superior y pip. Las pruebas se ejecutaron con Python 3.13.
La única dependencia directa es Flask; se instala desde `requirements.txt`.

Clonar el repositorio y entrar a la carpeta:

```bash
git clone https://github.com/Mightkel/ProyectoFinal_ProgEst_SII.git
cd ProyectoFinal_ProgEst_SII
```

En Windows, desde PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

En Linux o macOS:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python app.py
```

Abrir <http://127.0.0.1:5000>. Desde la presentación, pulsar **Abrir Ritmo**.
Para detener el servidor, presionar `Ctrl+C` en la terminal.

El servidor de `app.py` usa el modo de desarrollo de Flask y está pensado para
ejecutarse localmente.

## Primera ejecución y archivos de audio

La biblioteca comienza vacía. En **Biblioteca**, desplegar **Añadir una canción** y
completar título, artista, género y duración. La duración puede escribirse como
`3:45` o como `225` segundos.

Se puede adjuntar un archivo desde la biblioteca. Se admiten audios `.mp3`, `.ogg`,
`.wav` y `.m4a`, y portadas `.jpg`, `.jpeg`, `.png` y `.webp`. La reproducción de
cada formato depende del navegador.

También se pueden copiar archivos a `musica/` y `portadas/`, usando como nombre
el ID de la canción, su título o `artista - título`. Al adjuntar desde la interfaz,
las carpetas se crean automáticamente y el archivo se guarda con el ID.

Sin archivo de audio, la aplicación muestra un modo simulado: el tiempo y la
playlist avanzan, pero no se escucha sonido.

## Estructuras de datos

| Estructura | Archivo | Datos y uso |
| --- | --- | --- |
| Lista de diccionarios | `modulos/biblioteca.py` | Cada canción contiene ID, título, artista, género y duración. Permite altas, bajas y filtros. |
| Lista doblemente enlazada | `modulos/playlist.py` | Cada nodo guarda un ID y referencias al anterior y al siguiente. Permite navegar y reordenar la playlist. |
| Árbol binario de búsqueda | `modulos/indice.py` | Guarda títulos normalizados, sus IDs e hijos izquierdo y derecho. Se usa para búsquedas por prefijo y recorridos alfabéticos. |
| Pila | `modulos/historial.py` | Guarda IDs de reproducciones; `append` agrega al tope y `pop` permite volver. Conserva hasta 50 entradas. |
| Grafo no dirigido con pesos | `modulos/grafo.py` | Un diccionario de adyacencia conecta artistas con afinidades del 1 al 10. Se usa para recomendaciones y recorridos BFS. |

Las estructuras crecen según los datos ingresados. En la playlist, cambiar los
enlaces evita desplazar todas las canciones; localizar un nodo por ID sí requiere
recorrerla. La pila permite recuperar lo último escuchado en orden LIFO. El árbol
evita revisar todos los títulos en cada búsqueda cuando mantiene una altura baja;
se construye inicialmente balanceado, pero no se rebalancea tras cada inserción.
El grafo representa relaciones entre artistas sin imponer un orden lineal.

El camino calculado por BFS es el de menos saltos, no el de menor peso. Los pesos
se usan como afinidad para las recomendaciones.

## Demostración rápida

1. Crear tres canciones: A, B y C, con duraciones diferentes.
2. Agregarlas a la playlist en ese orden y reproducir A.
3. Elegir **Reproducir a continuación** en C. La playlist pasa de A, B, C a A, C, B.
4. Avanzar a C y usar **Volver a la canción anterior** para regresar a A.
5. Abrir **Bajo el capó** para mostrar la lista enlazada, el árbol y la pila.
6. En **Ordenación**, seleccionar la playlist y ordenar por duración. La animación
   muestra comparaciones e intercambios; **Aplicar a mi playlist** guarda el orden
   y conserva la canción actual.

Para ver recomendaciones, agregar canciones de distintos artistas y conectar
esos artistas desde **Mapa de artistas**.

## Guardado

La carpeta `datos/` se crea al guardar el primer cambio y contiene:

- `canciones.json`: biblioteca.
- `playlist.json`: orden de los IDs, canción actual y repetición.
- `historial.json`: pila de reproducciones.
- `grafo.json`: artistas, conexiones y pesos.

Al iniciar, se reconstruyen el árbol de búsqueda y la lista enlazada. Los datos,
audios y portadas de cada instalación se mantienen fuera del repositorio.

## Pruebas

Con el entorno instalado, ejecutar:

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
```

En Linux o macOS, reemplazar el ejecutable por `.venv/bin/python`.
Las pruebas comprueban los cuatro algoritmos, la reproducción de sus pasos,
las rutas de ordenación, el guardado de la playlist y la actualización del
historial al eliminar canciones. Usan una carpeta temporal para no cambiar los
datos locales.

## Repositorio y colaboración

La versión integrada está en `main`. Las ramas de trabajo del equipo y sus commits
permiten consultar los cambios de cada integrante.

- [Repositorio](https://github.com/Mightkel/ProyectoFinal_ProgEst_SII)
- [Historial de main](https://github.com/Mightkel/ProyectoFinal_ProgEst_SII/commits/main/)
- [Ramas del equipo](https://github.com/Mightkel/ProyectoFinal_ProgEst_SII/branches)

Cada integrante debe trabajar con su cuenta y registrar sus cambios con mensajes
que expliquen el aporte realizado.
