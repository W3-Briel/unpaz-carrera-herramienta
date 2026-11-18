import unittest

from Bexport_Bimport import Import
from class_Materias import Materia
from scoring import (
    calcular_importancias_globales,
    puntuar_materias_cursables,
)


def crear_materia(codigo, correlativas=None):
    return Materia(
        codigo,
        "Materia {}".format(codigo),
        "Cuatrimestral",
        4,
        correlativas or [],
        1,
    )


class ImportanciasGlobalesTests(unittest.TestCase):
    def test_cuenta_descendientes_unicos_por_dependencias_directas_e_indirectas(self):
        plan = [
            crear_materia(1),
            crear_materia(2, [1]),
            crear_materia(3, [1]),
            crear_materia(4, [2, 3]),
            crear_materia(5, [4]),
        ]

        metricas = calcular_importancias_globales(plan)

        self.assertEqual(metricas[1].directas, 2)
        self.assertEqual(metricas[1].indirectas, 2)
        self.assertEqual(metricas[1].total, 4)
        self.assertEqual(plan[0].get_importancia_total(), 4)

    def test_rechaza_correlativa_inexistente_y_ciclos(self):
        with self.assertRaisesRegex(ValueError, "inexistentes"):
            calcular_importancias_globales([crear_materia(1, [9])])

        with self.assertRaisesRegex(ValueError, "ciclo"):
            calcular_importancias_globales(
                [crear_materia(1, [2]), crear_materia(2, [1])]
            )

    def test_calcula_impacto_para_planes_serializados_existentes(self):
        plan = Import("LGTI").get_load()

        metricas = calcular_importancias_globales(plan)

        self.assertEqual(len(plan), 43)
        self.assertEqual(metricas[6003].directas, 3)
        self.assertEqual(metricas[6003].indirectas, 10)
        self.assertEqual(metricas[6003].total, 13)

    def test_acepta_el_plan_serializado_de_comercio_electronico(self):
        plan = Import("COMERCIO_ELECTRONICO").get_load()

        metricas = calcular_importancias_globales(plan)

        self.assertEqual(len(plan), 23)
        self.assertEqual(len(metricas), 23)


class PuntajesRecomendacionTests(unittest.TestCase):
    def setUp(self):
        self.plan = [
            crear_materia(1),
            crear_materia(2, [1]),
            crear_materia(3, [2]),
            crear_materia(4, [3]),
            crear_materia(5, [1, 6]),
            crear_materia(6),
        ]

    def test_calcula_desbloqueos_inmediatos_y_dependencias_futuras(self):
        recomendaciones = puntuar_materias_cursables(self.plan, [])
        recomendacion = next(
            item for item in recomendaciones if item.materia.get_codigo() == 1
        )

        self.assertEqual(
            [item.materia.get_codigo() for item in recomendaciones],
            [1, 6],
        )
        self.assertEqual(
            [materia.get_codigo() for materia in recomendacion.desbloqueos_inmediatos],
            [2],
        )
        self.assertEqual(
            [materia.get_codigo() for materia in recomendacion.dependientes_directos_pendientes],
            [2, 5],
        )
        self.assertEqual(
            [materia.get_codigo() for materia in recomendacion.dependientes_indirectos_pendientes],
            [3, 4],
        )
        self.assertEqual(
            {item.materia.get_codigo(): item.materias_faltantes for item in recomendacion.contribuciones},
            {2: 0, 3: 1, 4: 2, 5: 1},
        )
        self.assertAlmostEqual(recomendacion.puntaje, 2.875)

    def test_no_recomienda_materias_aprobadas_y_recalcula_el_impacto_pendiente(self):
        recomendaciones = puntuar_materias_cursables(self.plan, [1, 2, 3])

        codigos = [item.materia.get_codigo() for item in recomendaciones]
        self.assertNotIn(1, codigos)
        self.assertNotIn(2, codigos)
        self.assertNotIn(3, codigos)
        self.assertEqual(recomendaciones[0].materia.get_codigo(), 6)
        self.assertEqual(
            [materia.get_codigo() for materia in recomendaciones[0].desbloqueos_inmediatos],
            [5],
        )

    def test_rechaza_historial_con_codigos_ajenos_al_plan(self):
        with self.assertRaisesRegex(ValueError, "no están en el plan"):
            puntuar_materias_cursables(self.plan, [99])

    def test_rechaza_parametros_fuera_de_rango(self):
        with self.assertRaisesRegex(ValueError, "alpha"):
            puntuar_materias_cursables(self.plan, [], alpha=-1)
        with self.assertRaisesRegex(ValueError, "decay"):
            puntuar_materias_cursables(self.plan, [], decay=1.1)
        with self.assertRaisesRegex(ValueError, "numéricos"):
            puntuar_materias_cursables(self.plan, [], alpha="alto")


if __name__ == "__main__":
    unittest.main()
