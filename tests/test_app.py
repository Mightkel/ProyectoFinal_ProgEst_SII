import tempfile
import unittest
from unittest.mock import patch

import app as proyecto


class PruebasAplicacion(unittest.TestCase):
    def setUp(self):
        carpeta = tempfile.TemporaryDirectory(prefix="ritmo_pruebas_")
        self.addCleanup(carpeta.cleanup)
        self.addCleanup(proyecto.cargar_estado)
        datos = patch.object(proyecto.almacenamiento, "CARPETA_DATOS", carpeta.name)
        datos.start()
        self.addCleanup(datos.stop)
        testing = patch.dict(proyecto.app.config, TESTING=True)
        testing.start()
        self.addCleanup(testing.stop)
        proyecto.cargar_estado()
        self.cliente = proyecto.app.test_client()

    def agregar_canciones(self):
        for titulo, artista, genero, duracion in [
                ("Zeta", "Banda C", "Rock", "3:00"),
                ("Árbol", "Banda B", "Pop", "2:00"),
                ("Beta", "Banda A", "Jazz", "4:00")]:
            r = self.cliente.post("/api/canciones", json={
                "titulo": titulo, "artista": artista, "genero": genero, "duracion": duracion})
            self.assertEqual(r.status_code, 200)

    def test_algoritmos_y_ordenacion_numerica(self):
        r = self.cliente.get("/api/ordenacion/algoritmos")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.json["algoritmos"]), 4)
        for info in r.json["algoritmos"]:
            for descendente in (False, True):
                numeros = [3, 1, 2, 1]
                r = self.cliente.post("/api/ordenar", json={
                    "fuente": "numeros", "numeros": numeros,
                    "algoritmo": info["clave"], "descendente": descendente})
                self.assertEqual(r.status_code, 200)
                self.assertEqual([numeros[k] for k in r.json["orden"]],
                                 sorted(numeros, reverse=descendente))

    def test_ordenacion_por_campos_y_aplicacion_a_playlist(self):
        self.agregar_canciones()
        for i in [1, 2, 3]:
            self.cliente.post("/api/playlist/agregar", json={"id": i})
        self.cliente.post("/api/reproducir", json={"id": 2})
        for campo, esperado in [("titulo", [2, 3, 1]), ("artista", [3, 2, 1]),
                                ("genero", [3, 2, 1]), ("duracion", [2, 1, 3])]:
            for fuente in ("canciones", "playlist"):
                r = self.cliente.post("/api/ordenar", json={"fuente": fuente, "campo": campo})
                self.assertEqual(r.status_code, 200)
                self.assertEqual([r.json["elementos"][k]["id"] for k in r.json["orden"]], esperado)
        r = self.cliente.post("/api/playlist/ordenar", json={
            "campo": "duracion", "algoritmo": "rapida", "descendente": True})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json["ids"], [3, 1, 2])
        proyecto.cargar_estado()
        estado = self.cliente.get("/api/estado").json
        self.assertEqual(estado["playlist"]["ids"], [3, 1, 2])
        self.assertEqual(estado["playlist"]["actual"], 2)

    def test_comparar_algoritmos(self):
        r = self.cliente.post("/api/ordenar/comparar", json={
            "fuente": "numeros", "numeros": [3, 1, 2]})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json["n"], 3)
        self.assertEqual(len(r.json["resultados"]), 4)
        self.assertTrue(all(f["comparaciones"] > 0 for f in r.json["resultados"]))

    def test_validacion_ordenacion(self):
        for numeros in ([], [1], [True, 2], [0, 2], [1000, 2], ["a", 2], list(range(1, 32))):
            r = self.cliente.post("/api/ordenar", json={"fuente": "numeros", "numeros": numeros})
            self.assertEqual(r.status_code, 400)
        for datos in ({"fuente": "inexistente"}, {"campo": "inexistente"},
                      {"fuente": "numeros", "numeros": [2, 1], "algoritmo": "inexistente"}):
            self.assertEqual(self.cliente.post("/api/ordenar", json=datos).status_code, 400)

    def test_eliminar_actual_actualiza_historial_y_persistencia(self):
        self.agregar_canciones()
        for i in [1, 2, 3]:
            self.cliente.post("/api/playlist/agregar", json={"id": i})
        self.cliente.post("/api/reproducir", json={"id": 1})
        r = self.cliente.delete("/api/canciones/1")
        self.assertEqual(r.status_code, 200)
        proyecto.cargar_estado()
        estado = self.cliente.get("/api/estado").json
        self.assertEqual(estado["playlist"]["ids"], [2, 3])
        self.assertEqual(estado["playlist"]["actual"], 2)
        self.assertEqual(estado["historial"], [2])
        self.assertEqual(self.cliente.get("/api/buscar?q=Zeta").json["resultados"], [])

    def test_eliminar_actual_en_medio_o_al_final(self):
        self.agregar_canciones()
        for i in [1, 2, 3]:
            self.cliente.post("/api/playlist/agregar", json={"id": i})
        self.cliente.post("/api/reproducir", json={"id": 1})
        self.cliente.post("/api/reproducir", json={"id": 2})
        self.cliente.delete("/api/canciones/2")
        estado = self.cliente.get("/api/estado").json
        self.assertEqual(estado["playlist"]["actual"], 3)
        self.assertEqual(estado["historial"], [3, 1])
        #Volver debe recuperar A, sin referencias a la canción B eliminada.
        self.assertEqual(self.cliente.post("/api/volver").status_code, 200)
        self.assertEqual(self.cliente.get("/api/estado").json["playlist"]["actual"], 1)
        self.cliente.post("/api/reproducir", json={"id": 3})
        self.cliente.delete("/api/canciones/3")
        estado = self.cliente.get("/api/estado").json
        self.assertEqual(estado["playlist"]["actual"], 1)
        self.assertEqual(estado["historial"], [1])

    def test_eliminar_no_actual_y_ultima_cancion(self):
        self.agregar_canciones()
        for i in [1, 2]:
            self.cliente.post("/api/playlist/agregar", json={"id": i})
        self.cliente.post("/api/reproducir", json={"id": 1})
        self.cliente.post("/api/reproducir", json={"id": 2})
        self.cliente.delete("/api/canciones/1")
        estado = self.cliente.get("/api/estado").json
        self.assertEqual(estado["playlist"]["actual"], 2)
        self.assertEqual(estado["historial"], [2])
        self.cliente.delete("/api/canciones/2")
        estado = self.cliente.get("/api/estado").json
        self.assertIsNone(estado["playlist"]["actual"])
        self.assertEqual(estado["playlist"]["ids"], [])
        self.assertEqual(estado["historial"], [])
        self.assertEqual(self.cliente.post("/api/volver").status_code, 400)


if __name__ == "__main__":
    unittest.main()
