import unittest

from siu_guarani import (
    TablaSiu,
    extraer_materias_aprobadas,
)


class ExtraccionSiuTests(unittest.TestCase):
    def test_detecta_estado_y_codigo_desde_encabezados(self):
        tablas = (
            TablaSiu(
                ("Código", "Materia", "Estado", "Nota"),
                (
                    ("6001", "Análisis Matemático I", "Aprobada", "8"),
                    ("6002", "Arquitectura de Computadoras I", "Pendiente", "3"),
                ),
            ),
        )

        materias = extraer_materias_aprobadas(tablas)

        self.assertEqual(
            materias,
            [materias[0]],
        )
        self.assertEqual(materias[0].codigo, 6001)
        self.assertEqual(materias[0].nombre, "Análisis Matemático I")
        self.assertEqual(materias[0].nota, 8)

    def test_no_confunde_codigo_con_numero_de_fila(self):
        tablas = (
            TablaSiu(
                ("Nº", "Actividad", "Condición"),
                (("1", "Introducción a la Programación", "Promocionado"),),
            ),
        )

        materias = extraer_materias_aprobadas(tablas)

        self.assertEqual(materias, [])

    def test_admite_nombres_completos(self):
        tablas = (
            TablaSiu(
                ("Materia", "Código", "Estado", "Nota"),
                (("Inglés I", "6010", "Promocionada", "8"),),
            ),
        )

        materias = extraer_materias_aprobadas(tablas)

        self.assertEqual(materias[0].codigo, 6010)
        self.assertEqual(materias[0].nombre, "Inglés I")
        self.assertEqual(materias[0].tipo_aprobacion, "Promocionada")
        self.assertEqual(materias[0].nota, 8)

    def test_regularizada_requiere_nota_seis_o_mas(self):
        tablas = (
            TablaSiu(
                ("Código", "Materia", "Tipo", "Nota"),
                (
                    ("6001", "Análisis Matemático I", "Regularizada", "6"),
                    ("6002", "Arquitectura de Computadoras I", "Regularizada", "5"),
                ),
            ),
        )

        materias = extraer_materias_aprobadas(tablas)

        self.assertEqual([materia.codigo for materia in materias], [6001])

    def test_examen_requiere_nota_cuatro_o_mas(self):
        tablas = (
            TablaSiu(
                ("Código", "Materia", "Tipo", "Nota"),
                (
                    ("6001", "Análisis Matemático I", "Examen", "4"),
                    ("6002", "Arquitectura de Computadoras I", "Examen", "3"),
                ),
            ),
        )

        materias = extraer_materias_aprobadas(tablas)

        self.assertEqual([materia.codigo for materia in materias], [6001])


if __name__ == "__main__":
    unittest.main()
