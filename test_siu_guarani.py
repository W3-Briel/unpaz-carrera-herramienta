import unittest

from siu_guarani import (
    TablaSiu,
    analizar_materias_aprobadas,
    extraer_materias_aprobadas,
)


class ExtraccionSiuTests(unittest.TestCase):
    def test_detecta_estado_y_codigo_desde_encabezados(self):
        tablas = (
            TablaSiu(
                ("Código", "Materia", "Tipo", "Nota"),
                (
                    ("6001", "Análisis Matemático I", "Regularizada", "8"),
                    ("6002", "Arquitectura de Computadoras I", "Regularizada", "5"),
                ),
            ),
        )

        materias = extraer_materias_aprobadas(tablas)

        self.assertEqual(len(materias), 1)
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
                ("Materia", "Código", "Tipo", "Nota"),
                (("Inglés I", "6010", "Examen", "8"),),
            ),
        )

        materias = extraer_materias_aprobadas(tablas)

        self.assertEqual(materias[0].codigo, 6010)
        self.assertEqual(materias[0].nombre, "Inglés I")
        self.assertEqual(materias[0].tipo_aprobacion, "Examen")
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

    def test_prefiere_examen_si_hay_varios_resultados_aprobados(self):
        tablas = (
            TablaSiu(
                ("Código", "Materia", "Tipo", "Nota"),
                (
                    ("6001", "Análisis Matemático I", "Regularizada", "8"),
                    ("6001", "Análisis Matemático I", "Examen", "4"),
                ),
            ),
        )

        materias = extraer_materias_aprobadas(tablas)

        self.assertEqual(len(materias), 1)
        self.assertEqual(materias[0].tipo_aprobacion, "Examen")
        self.assertEqual(materias[0].nota, 4)

    def test_informa_cuales_campos_no_pudo_leer_y_no_toma_otros_numeros_como_nota(self):
        tablas = (
            TablaSiu(
                ("Código", "Materia", "Tipo", "Comisión", "Año"),
                (
                    ("6001", "Análisis Matemático I", "Regularizada", "8", "2024"),
                    ("6002", "Arquitectura de Computadoras I", "Examen", "4", "2024"),
                ),
            ),
        )

        analisis = analizar_materias_aprobadas(tablas)

        self.assertEqual(analisis.filas_analizadas, 2)
        self.assertEqual(analisis.filas_con_codigo, 2)
        self.assertEqual(analisis.filas_con_tipo, 2)
        self.assertEqual(analisis.filas_con_nota, 0)
        self.assertEqual(analisis.materias_aprobadas, ())
        self.assertEqual(
            [fila.motivo for fila in analisis.descartadas],
            ["no se identificó una nota", "no se identificó una nota"],
        )

    def test_interpreta_el_formato_real_de_la_tabla_del_plan_siu(self):
        tablas = (
            TablaSiu(
                (
                    "Actividad",
                    "Tipo",
                    "Año",
                    "Período",
                    "Nota",
                    "Origen",
                    "Créditos",
                    "Puntaje",
                    "Correlativas",
                ),
                (
                    (
                        "Análisis Matemático I (6001)",
                        "Materia",
                        "1",
                        "Cuatrimestral",
                        "9 (Promocionado)",
                        "Promoción",
                        "",
                        "",
                        "",
                    ),
                    (
                        "Ingeniería de Software I (6014)",
                        "Materia",
                        "2",
                        "Cuatrimestral",
                        "6 (Aprobado)",
                        "Examen",
                        "",
                        "",
                        "",
                    ),
                    (
                        "Álgebra y Geometría Analítica (6007)",
                        "Materia",
                        "1",
                        "Cuatrimestral",
                        "7",
                        "Regularización",
                        "",
                        "",
                        "",
                    ),
                    (
                        "Examen desaprobado (6015)",
                        "Materia",
                        "2",
                        "Cuatrimestral",
                        "3 (Desaprobado)",
                        "Examen",
                        "",
                        "",
                        "",
                    ),
                ),
            ),
        )

        analisis = analizar_materias_aprobadas(tablas)

        self.assertEqual(
            [
                (materia.codigo, materia.tipo_aprobacion, materia.nota)
                for materia in analisis.materias_aprobadas
            ],
            [
                (6001, "Promocionada", 9),
                (6007, "Regularizada", 7),
                (6014, "Examen", 6),
            ],
        )
        self.assertEqual(analisis.filas_con_nota, 4)


if __name__ == "__main__":
    unittest.main()
