import os
import json
import sqlite3
import shutil
import tempfile
import unittest
from contextlib import closing

from unpaz_carrera.domain.scoring import puntuar_materias_cursables
from unpaz_carrera.infrastructure.siu_guarani import MateriaAprobadaSiu
from unpaz_carrera.infrastructure.repository import RepositorioAcademico
from unpaz_carrera.infrastructure.plan_loader import DEFAULT_PLANS_DIRECTORY


class RepositorioAcademicoTests(unittest.TestCase):
    def setUp(self):
        self.directorio = tempfile.TemporaryDirectory()
        ruta = os.path.join(self.directorio.name, "prueba.sqlite3")
        self.repositorio = RepositorioAcademico(ruta)

    def tearDown(self):
        self.directorio.cleanup()

    def test_importa_planes_y_persisten_alumnos_e_historial(self):
        carreras = self.repositorio.listar_carreras()
        self.assertEqual(len(carreras), 2)

        alumno_id = self.repositorio.crear_alumno("Ada", "LGTI")
        materia = MateriaAprobadaSiu(
            6001, "Análisis Matemático I", "Regularizada", 7
        )
        self.assertEqual(
            self.repositorio.guardar_materias_aprobadas(alumno_id, [materia]),
            1,
        )

        nuevo_repositorio = RepositorioAcademico(self.repositorio.ruta)
        alumno = nuevo_repositorio.obtener_alumno(alumno_id)
        aprobadas = nuevo_repositorio.listar_materias_aprobadas(alumno_id)

        self.assertEqual(alumno["nombre"], "Ada")
        self.assertEqual(alumno["carrera_id"], "LGTI")
        self.assertEqual(aprobadas[0]["codigo"], 6001)
        self.assertEqual(aprobadas[0]["tipo_aprobacion"], "Regularizada")
        self.assertEqual(aprobadas[0]["nota"], 7)

    def test_scoring_usa_materias_guardadas_en_sqlite(self):
        alumno_id = self.repositorio.crear_alumno("Grace", "LGTI")
        self.repositorio.guardar_materias_aprobadas(
            alumno_id,
            [MateriaAprobadaSiu(6001, "Análisis Matemático I", "Examen", 4)],
        )

        recomendaciones = puntuar_materias_cursables(
            self.repositorio.obtener_plan("LGTI"),
            self.repositorio.codigos_materias_aprobadas(alumno_id),
        )

        codigos_recomendados = {
            recomendacion.materia.get_codigo()
            for recomendacion in recomendaciones
        }
        self.assertNotIn(6001, codigos_recomendados)
        self.assertIn(6006, codigos_recomendados)

    def test_no_guarda_materia_de_otra_carrera(self):
        alumno_id = self.repositorio.crear_alumno("Lin", "COMERCIO_ELECTRONICO")

        with self.assertRaisesRegex(ValueError, "no pertenece"):
            self.repositorio.guardar_materias_aprobadas(
                alumno_id,
                [MateriaAprobadaSiu(6001, "Análisis Matemático I", "Examen", 5)],
            )

        self.assertEqual(
            self.repositorio.listar_materias_aprobadas(alumno_id),
            [],
        )

    def test_no_guarda_nota_menor_al_minimo(self):
        alumno_id = self.repositorio.crear_alumno("Lin", "LGTI")

        with self.assertRaisesRegex(ValueError, "no alcanza el mínimo"):
            self.repositorio.guardar_materias_aprobadas(
                alumno_id,
                [MateriaAprobadaSiu(6001, "Análisis Matemático I", "Examen", 3)],
            )

        self.assertEqual(
            self.repositorio.listar_materias_aprobadas(alumno_id),
            [],
        )

    def test_migra_el_esquema_anterior_preservando_datos(self):
        alumno_id = self.repositorio.crear_alumno("Ada", "LGTI")
        self.repositorio.guardar_materias_aprobadas(
            alumno_id,
            [MateriaAprobadaSiu(6001, "Análisis Matemático I", "Examen", 6)],
        )

        with closing(sqlite3.connect(self.repositorio.ruta)) as conexion:
            with conexion:
                conexion.execute("PRAGMA foreign_keys = OFF")
                conexion.execute(
                    """
                    CREATE TABLE materias_aprobadas_vieja (
                        alumno_id INTEGER NOT NULL,
                        carrera_id TEXT NOT NULL,
                        materia_codigo INTEGER NOT NULL,
                        tipo_aprobacion TEXT NOT NULL
                            CHECK (tipo_aprobacion IN ('Regularizada', 'Examen')),
                        nota REAL NOT NULL CHECK (nota >= 0 AND nota <= 10),
                        actualizada_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (alumno_id, materia_codigo),
                        FOREIGN KEY (alumno_id, carrera_id)
                            REFERENCES alumnos(id, carrera_id),
                        FOREIGN KEY (carrera_id, materia_codigo)
                            REFERENCES materias(carrera_id, codigo)
                    )
                    """
                )
                conexion.execute(
                    """
                    INSERT INTO materias_aprobadas_vieja
                    SELECT * FROM materias_aprobadas
                    """
                )
                conexion.execute("DROP TABLE materias_aprobadas")
                conexion.execute(
                    "ALTER TABLE materias_aprobadas_vieja RENAME TO materias_aprobadas"
                )

        repositorio_migrado = RepositorioAcademico(self.repositorio.ruta)
        aprobadas_anteriores = repositorio_migrado.listar_materias_aprobadas(
            alumno_id
        )
        self.assertEqual(len(aprobadas_anteriores), 1)
        self.assertEqual(aprobadas_anteriores[0]["nota"], 6)

        repositorio_migrado.guardar_materias_aprobadas(
            alumno_id,
            [MateriaAprobadaSiu(6002, "Arquitectura de Computadoras I", "Promocionada", 9)],
        )
        self.assertEqual(
            repositorio_migrado.listar_materias_aprobadas(alumno_id)[1][
                "tipo_aprobacion"
            ],
            "Promocionada",
        )

    def test_sincroniza_cambios_del_plan_en_sqlite_y_preserva_historial(self):
        planes_dir = os.path.join(self.directorio.name, "planes")
        os.makedirs(planes_dir)
        for nombre_archivo in ("lgti.json", "comercio_electronico.json"):
            shutil.copyfile(
                os.path.join(DEFAULT_PLANS_DIRECTORY, nombre_archivo),
                os.path.join(planes_dir, nombre_archivo),
            )

        ruta_db = os.path.join(self.directorio.name, "sincronizacion.sqlite3")
        repositorio = RepositorioAcademico(ruta_db, planes_dir)
        alumno_id = repositorio.crear_alumno("Ada", "LGTI")
        repositorio.guardar_materias_aprobadas(
            alumno_id,
            [MateriaAprobadaSiu(6001, "Análisis Matemático I", "Examen", 6)],
        )

        ruta_plan = os.path.join(planes_dir, "lgti.json")
        with open(ruta_plan, encoding="utf-8") as archivo:
            plan = json.load(archivo)
        plan["materias"][0]["asignatura"] = "Análisis Matemático I actualizado"
        with open(ruta_plan, "w", encoding="utf-8") as archivo:
            json.dump(plan, archivo, ensure_ascii=False)

        self.assertEqual(repositorio.sincronizar_planes(), 2)
        materia = next(
            materia
            for materia in repositorio.obtener_plan("LGTI")
            if materia.get_codigo() == 6001
        )
        aprobadas = repositorio.listar_materias_aprobadas(alumno_id)

        self.assertEqual(materia.get_asignatura(), "Análisis Matemático I actualizado")
        self.assertEqual(len(aprobadas), 1)
        self.assertEqual(aprobadas[0]["codigo"], 6001)

    def test_no_quita_del_plan_una_materia_con_historial_aprobado(self):
        planes_dir = os.path.join(self.directorio.name, "planes_con_historial")
        os.makedirs(planes_dir)
        for nombre_archivo in ("lgti.json", "comercio_electronico.json"):
            shutil.copyfile(
                os.path.join(DEFAULT_PLANS_DIRECTORY, nombre_archivo),
                os.path.join(planes_dir, nombre_archivo),
            )

        ruta_db = os.path.join(self.directorio.name, "historial.sqlite3")
        repositorio = RepositorioAcademico(ruta_db, planes_dir)
        alumno_id = repositorio.crear_alumno("Ada", "LGTI")
        repositorio.guardar_materias_aprobadas(
            alumno_id,
            [MateriaAprobadaSiu(6001, "Análisis Matemático I", "Examen", 6)],
        )

        ruta_plan = os.path.join(planes_dir, "lgti.json")
        with open(ruta_plan, encoding="utf-8") as archivo:
            plan = json.load(archivo)
        plan["materias"] = [
            materia for materia in plan["materias"] if materia["codigo"] != 6001
        ]
        for materia in plan["materias"]:
            materia["correlativas"] = [
                codigo for codigo in materia["correlativas"] if codigo != 6001
            ]
        with open(ruta_plan, "w", encoding="utf-8") as archivo:
            json.dump(plan, archivo, ensure_ascii=False)

        with self.assertRaisesRegex(ValueError, "historial aprobado"):
            repositorio.sincronizar_planes()

        self.assertEqual(
            repositorio.codigos_materias_aprobadas(alumno_id),
            [6001],
        )
        self.assertIn(
            6001,
            {
                materia.get_codigo()
                for materia in repositorio.obtener_plan("LGTI")
            },
        )


if __name__ == "__main__":
    unittest.main()
