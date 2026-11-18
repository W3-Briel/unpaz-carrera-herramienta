import os
import pickle
import sqlite3
from contextlib import closing

from class_Materias import Materia


DIRECTORIO_PROYECTO = os.path.dirname(os.path.abspath(__file__))
BASE_DATOS_POR_DEFECTO = os.path.join(
    DIRECTORIO_PROYECTO, "datos_academicos.sqlite3"
)

CARRERAS_INICIALES = (
    ("LGTI", "Licenciatura en Gestión de Tecnologías de Información"),
    ("COMERCIO_ELECTRONICO", "Comercio Electrónico"),
)


class RepositorioAcademico:
    def __init__(self, ruta=BASE_DATOS_POR_DEFECTO):
        self.ruta = ruta
        self._crear_esquema()
        self._importar_planes_iniciales_si_corresponde()

    def _conectar(self):
        conexion = sqlite3.connect(self.ruta)
        conexion.row_factory = sqlite3.Row
        conexion.execute("PRAGMA foreign_keys = ON")
        return conexion

    def _crear_esquema(self):
        with closing(self._conectar()) as conexion:
            with conexion:
                conexion.executescript(
                    """
                    CREATE TABLE IF NOT EXISTS carreras (
                        id TEXT PRIMARY KEY,
                        nombre TEXT NOT NULL UNIQUE
                    );

                    CREATE TABLE IF NOT EXISTS materias (
                        carrera_id TEXT NOT NULL,
                        codigo INTEGER NOT NULL,
                        asignatura TEXT NOT NULL,
                        regimen TEXT NOT NULL,
                        horas INTEGER NOT NULL,
                        anio INTEGER NOT NULL,
                        PRIMARY KEY (carrera_id, codigo),
                        FOREIGN KEY (carrera_id) REFERENCES carreras(id)
                    );

                    CREATE TABLE IF NOT EXISTS correlativas (
                        carrera_id TEXT NOT NULL,
                        materia_codigo INTEGER NOT NULL,
                        correlativa_codigo INTEGER NOT NULL,
                        PRIMARY KEY (carrera_id, materia_codigo, correlativa_codigo),
                        FOREIGN KEY (carrera_id, materia_codigo)
                            REFERENCES materias(carrera_id, codigo),
                        FOREIGN KEY (carrera_id, correlativa_codigo)
                            REFERENCES materias(carrera_id, codigo)
                    );

                    CREATE TABLE IF NOT EXISTS alumnos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre TEXT NOT NULL,
                        carrera_id TEXT NOT NULL,
                        creado_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE (id, carrera_id),
                        FOREIGN KEY (carrera_id) REFERENCES carreras(id)
                    );

                    CREATE TABLE IF NOT EXISTS materias_aprobadas (
                        alumno_id INTEGER NOT NULL,
                        carrera_id TEXT NOT NULL,
                        materia_codigo INTEGER NOT NULL,
                        tipo_aprobacion TEXT NOT NULL
                            CHECK (tipo_aprobacion IN (
                                'Regularizada', 'Examen', 'Promocionada'
                            )),
                        nota REAL NOT NULL CHECK (nota >= 0 AND nota <= 10),
                        actualizada_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (alumno_id, materia_codigo),
                        FOREIGN KEY (alumno_id, carrera_id)
                            REFERENCES alumnos(id, carrera_id),
                        FOREIGN KEY (carrera_id, materia_codigo)
                            REFERENCES materias(carrera_id, codigo)
                    );
                    """
                )
        self._migrar_materias_aprobadas()

    def _migrar_materias_aprobadas(self):
        with closing(self._conectar()) as conexion:
            definicion = conexion.execute(
                """
                SELECT sql FROM sqlite_master
                WHERE type = 'table' AND name = 'materias_aprobadas'
                """
            ).fetchone()["sql"]
            if "Promocionada" in definicion:
                return

            with conexion:
                conexion.execute(
                    """
                    CREATE TABLE materias_aprobadas_nueva (
                        alumno_id INTEGER NOT NULL,
                        carrera_id TEXT NOT NULL,
                        materia_codigo INTEGER NOT NULL,
                        tipo_aprobacion TEXT NOT NULL
                            CHECK (tipo_aprobacion IN (
                                'Regularizada', 'Examen', 'Promocionada'
                            )),
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
                    INSERT INTO materias_aprobadas_nueva
                        (alumno_id, carrera_id, materia_codigo,
                         tipo_aprobacion, nota, actualizada_en)
                    SELECT alumno_id, carrera_id, materia_codigo,
                           tipo_aprobacion, nota, actualizada_en
                    FROM materias_aprobadas
                    """
                )
                conexion.execute("DROP TABLE materias_aprobadas")
                conexion.execute(
                    "ALTER TABLE materias_aprobadas_nueva RENAME TO materias_aprobadas"
                )

    def _importar_planes_iniciales_si_corresponde(self):
        with closing(self._conectar()) as conexion:
            existentes = conexion.execute(
                "SELECT COUNT(*) AS cantidad FROM carreras"
            ).fetchone()["cantidad"]
        if existentes:
            return

        planes = {}
        for carrera_id, nombre in CARRERAS_INICIALES:
            ruta_plan = os.path.join(DIRECTORIO_PROYECTO, "bin_Carreras", carrera_id)
            with open(ruta_plan, "rb") as archivo:
                planes[carrera_id] = (nombre, pickle.load(archivo))

        with closing(self._conectar()) as conexion:
            with conexion:
                for carrera_id, (nombre, plan) in planes.items():
                    conexion.execute(
                        "INSERT INTO carreras (id, nombre) VALUES (?, ?)",
                        (carrera_id, nombre),
                    )
                    for materia in plan:
                        conexion.execute(
                            """
                            INSERT INTO materias
                                (carrera_id, codigo, asignatura, regimen, horas, anio)
                            VALUES (?, ?, ?, ?, ?, ?)
                            """,
                            (
                                carrera_id,
                                materia.get_codigo(),
                                materia.get_asignatura(),
                                materia.get_regimen(),
                                materia.get_horas(),
                                materia.get_año(),
                            ),
                        )
                    for materia in plan:
                        for correlativa in materia.get_correlativas():
                            conexion.execute(
                                """
                                INSERT INTO correlativas
                                    (carrera_id, materia_codigo, correlativa_codigo)
                                VALUES (?, ?, ?)
                                """,
                                (
                                    carrera_id,
                                    materia.get_codigo(),
                                    int(correlativa),
                                ),
                            )

    def listar_carreras(self):
        with closing(self._conectar()) as conexion:
            filas = conexion.execute(
                "SELECT id, nombre FROM carreras ORDER BY nombre"
            ).fetchall()
        return [(fila["id"], fila["nombre"]) for fila in filas]

    def crear_alumno(self, nombre, carrera_id):
        nombre = (nombre or "").strip()
        if not nombre:
            raise ValueError("El nombre del alumno no puede estar vacío.")

        with closing(self._conectar()) as conexion:
            with conexion:
                cursor = conexion.execute(
                    "INSERT INTO alumnos (nombre, carrera_id) VALUES (?, ?)",
                    (nombre, carrera_id),
                )
                alumno_id = cursor.lastrowid
        return alumno_id

    def listar_alumnos(self):
        with closing(self._conectar()) as conexion:
            filas = conexion.execute(
                """
                SELECT alumnos.id, alumnos.nombre, carreras.id AS carrera_id,
                       carreras.nombre AS carrera_nombre
                FROM alumnos
                JOIN carreras ON carreras.id = alumnos.carrera_id
                ORDER BY alumnos.nombre, alumnos.id
                """
            ).fetchall()
        return [dict(fila) for fila in filas]

    def obtener_alumno(self, alumno_id):
        with closing(self._conectar()) as conexion:
            fila = conexion.execute(
                """
                SELECT alumnos.id, alumnos.nombre, carreras.id AS carrera_id,
                       carreras.nombre AS carrera_nombre
                FROM alumnos
                JOIN carreras ON carreras.id = alumnos.carrera_id
                WHERE alumnos.id = ?
                """,
                (alumno_id,),
            ).fetchone()
        if fila is None:
            raise ValueError("No existe el alumno seleccionado.")
        return dict(fila)

    def obtener_plan(self, carrera_id):
        with closing(self._conectar()) as conexion:
            filas = conexion.execute(
                """
                SELECT codigo, asignatura, regimen, horas, anio
                FROM materias
                WHERE carrera_id = ?
                ORDER BY anio, codigo
                """,
                (carrera_id,),
            ).fetchall()
            plan = {
                fila["codigo"]: Materia(
                    fila["codigo"],
                    fila["asignatura"],
                    fila["regimen"],
                    fila["horas"],
                    [],
                    fila["anio"],
                )
                for fila in filas
            }
            relaciones = conexion.execute(
                """
                SELECT materia_codigo, correlativa_codigo
                FROM correlativas
                WHERE carrera_id = ?
                ORDER BY materia_codigo, correlativa_codigo
                """,
                (carrera_id,),
            ).fetchall()

        for relacion in relaciones:
            plan[relacion["materia_codigo"]].correlativas.append(
                relacion["correlativa_codigo"]
            )
        return list(plan.values())

    def guardar_materias_aprobadas(self, alumno_id, materias_aprobadas):
        alumno = self.obtener_alumno(alumno_id)
        codigos_plan = {
            materia.get_codigo()
            for materia in self.obtener_plan(alumno["carrera_id"])
        }
        guardadas = 0

        with closing(self._conectar()) as conexion:
            with conexion:
                for materia in materias_aprobadas:
                    if materia.codigo not in codigos_plan:
                        raise ValueError(
                            "La materia {} no pertenece a la carrera del alumno.".format(
                                materia.codigo
                            )
                        )
                    tipo = materia.tipo_aprobacion.strip().lower()
                    if tipo.startswith("regulariz"):
                        tipo_guardado = "Regularizada"
                        nota_minima = 6
                    elif tipo.startswith("examen"):
                        tipo_guardado = "Examen"
                        nota_minima = 4
                    elif tipo.startswith("promocion"):
                        tipo_guardado = "Promocionada"
                        nota_minima = 0
                    else:
                        raise ValueError(
                            "Tipo de aprobación no admitido para la materia {}.".format(
                                materia.codigo
                            )
                        )
                    if materia.nota < nota_minima:
                        raise ValueError(
                            "La nota de la materia {} no alcanza el mínimo para {}.".format(
                                materia.codigo, tipo_guardado
                            )
                        )

                    conexion.execute(
                        """
                        INSERT INTO materias_aprobadas
                            (alumno_id, carrera_id, materia_codigo,
                             tipo_aprobacion, nota)
                        VALUES (?, ?, ?, ?, ?)
                        ON CONFLICT (alumno_id, materia_codigo) DO UPDATE SET
                            tipo_aprobacion = excluded.tipo_aprobacion,
                            nota = excluded.nota,
                            actualizada_en = CURRENT_TIMESTAMP
                        """,
                        (
                            alumno_id,
                            alumno["carrera_id"],
                            materia.codigo,
                            tipo_guardado,
                            materia.nota,
                        ),
                    )
                    guardadas += 1
        return guardadas

    def listar_materias_aprobadas(self, alumno_id):
        with closing(self._conectar()) as conexion:
            filas = conexion.execute(
                """
                SELECT materias_aprobadas.materia_codigo AS codigo,
                       materias.asignatura, materias_aprobadas.tipo_aprobacion,
                       materias_aprobadas.nota
                FROM materias_aprobadas
                JOIN materias
                  ON materias.carrera_id = materias_aprobadas.carrera_id
                 AND materias.codigo = materias_aprobadas.materia_codigo
                WHERE materias_aprobadas.alumno_id = ?
                ORDER BY materias.codigo
                """,
                (alumno_id,),
            ).fetchall()
        return [dict(fila) for fila in filas]

    def codigos_materias_aprobadas(self, alumno_id):
        return [
            fila["codigo"]
            for fila in self.listar_materias_aprobadas(alumno_id)
        ]
