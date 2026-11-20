import unittest

from unpaz_carrera.infrastructure.plan_loader import cargar_planes


class CargaPlanesTests(unittest.TestCase):
    def test_carga_planes_fuente_y_valida_correlativas(self):
        planes = {plan.identificador: plan for plan in cargar_planes()}

        self.assertEqual(set(planes), {"LGTI", "COMERCIO_ELECTRONICO"})
        self.assertEqual(len(planes["LGTI"].materias), 43)
        self.assertEqual(len(planes["COMERCIO_ELECTRONICO"].materias), 23)

        algebra = next(
            materia for materia in planes["LGTI"].materias
            if materia.get_codigo() == 6007
        )
        self.assertEqual(algebra.get_regimen(), "Cuatrimestral")
        self.assertEqual(algebra.get_correlativas(), [6001])


if __name__ == "__main__":
    unittest.main()
