import random
import unittest

from modulos import ordenacion


class PruebasOrdenacion(unittest.TestCase):
    def test_resultado_y_animacion(self):
        azar = random.Random(23)
        casos = [[], [7], [1, 2, 3], [3, 2, 1], [4, 4, 4],
                 [3, 1, 3, 2, 1], ["zeta", "alfa", "beta"],
                 [("pop", "zeta"), ("pop", "alfa"), ("rock", "beta")]]
        casos += [[azar.randrange(10) for _ in range(n)] for n in range(2, 31)]
        for info in ordenacion.info_algoritmos():
            for descendente in (False, True):
                for claves in casos:
                    with self.subTest(algoritmo=info["clave"], descendente=descendente, claves=claves):
                        originales = list(claves)
                        r = ordenacion.ordenar(claves, info["clave"], descendente)
                        self.assertEqual(claves, originales)
                        self.assertEqual([claves[k] for k in r["orden"]],
                                         sorted(claves, reverse=descendente))
                        if info["estable"]:
                            self.assertEqual(r["orden"], sorted(range(len(claves)),
                                             key=lambda k: claves[k], reverse=descendente))
                        #Reproduce lo que hace el navegador, incluyendo las posiciones definitivas.
                        orden = list(range(len(claves)))
                        fijas = {}
                        comparaciones = intercambios = 0
                        for paso in r["pasos"]:
                            i = paso["i"]
                            self.assertTrue(0 <= i < len(orden))
                            if paso["tipo"] in ("comparar", "intercambiar"):
                                j = paso["j"]
                                self.assertTrue(0 <= j < len(orden))
                            if paso["tipo"] == "comparar":
                                comparaciones += 1
                            elif paso["tipo"] == "intercambiar":
                                orden[i], orden[j] = orden[j], orden[i]
                                intercambios += 1
                            elif paso["tipo"] == "fijar":
                                fijas[i] = orden[i]
                            else:
                                self.assertEqual(paso["tipo"], "pivote")
                            for posicion, elemento in fijas.items():
                                self.assertEqual(orden[posicion], elemento)
                        self.assertEqual(orden, r["orden"])
                        self.assertEqual(len(fijas), len(claves))
                        self.assertEqual(comparaciones, r["comparaciones"])
                        self.assertEqual(intercambios, r["intercambios"])

    def test_claves_y_etiquetas(self):
        cancion = {"titulo": "Árbol", "artista": "Érika", "genero": "Pop", "duracion": 225}
        self.assertEqual(ordenacion.clave_cancion(cancion, "titulo"), "arbol")
        self.assertEqual(ordenacion.clave_cancion(cancion, "artista"), ("erika", "arbol"))
        self.assertEqual(ordenacion.clave_cancion(cancion, "genero"), ("pop", "arbol"))
        self.assertEqual(ordenacion.clave_cancion(cancion, "duracion"), 225)
        self.assertEqual(ordenacion.texto_corto(cancion, "duracion"), "3:45")
        self.assertEqual(ordenacion.texto_corto(cancion, "titulo"), "Árbol")
        cancion["titulo"] = "Un título demasiado largo para una burbuja"
        self.assertEqual(len(ordenacion.texto_corto(cancion, "titulo")), 16)

    def test_algoritmo_desconocido(self):
        self.assertIsNone(ordenacion.ordenar([3, 1, 2], "desconocido"))


if __name__ == "__main__":
    unittest.main()
