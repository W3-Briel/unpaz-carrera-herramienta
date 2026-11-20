import sqlite3
from contextlib import closing
from pathlib import Path

from unpaz_carrera.domain.materia import Materia
from unpaz_carrera.infrastructure.plan_loader import (
    DEFAULT_PLANS_DIRECTORY,
    PROJECT_ROOT,
    cargar_planes,
)


BASE_DATOS_POR_DEFECTO = PROJECT_ROOT / "datos_academicos.sqlite3"


class RepositorioAcademico:
    def __init__(
        self, ruta=BASE_DATOS_POR_DEFECTO, directorio_planes=DEFAULT_PLANS_DIRECTORY
    ):
        self.ruta = ruta
        self.directorio_planes = Path(directorio_planes)
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

        self.sincronizar_planes()

    def sincronizar_planes(self):
        planes = cargar_planes(self.directorio_planes)
        with closing(self._conectar()) as conexion:
            with conexion:
                for plan in planes:
                    self._sincronizar_plan(conexion, plan)
        return len(planes)

    @staticmethod
    def _sincronizar_plan(conexion, plan):
        carrera_id = plan.identificador
        codigos_nuevos = {materia.get_codigo() for materia in plan.materias}
        codigos_actuales = {
            fila["codigo"]
            for fila in conexion.execute(
                "SELECT codigo FROM materias WHERE carrera_id = ?",
                (carrera_id,),
            )
        }
        codigos_eliminados = codigos_actuales - codigos_nuevos
        if codigos_eliminados:
            placeholders = ",".join("?" for _ in codigos_eliminados)
            aprobadas = conexion.execute(
                """
                SELECT materia_codigo FROM materias_aprobadas
                WHERE carrera_id = ? AND materia_codigo IN ({})
                """.format(placeholders),
                (carrera_id, *sorted(codigos_eliminados)),
            ).fetchall()
            if aprobadas:
                codigos_con_historial = sorted(
                    {fila["materia_codigo"] for fila in aprobadas}
                )
                raise ValueError(
                    "No se pueden quitar materias con historial aprobado: {}.".format(
                        codigos_con_historial
                    )
                )

        conexion.execute(
            """
            INSERT INTO carreras (id, nombre) VALUES (?, ?)
            ON CONFLICT (id) DO UPDATE SET nombre = excluded.nombre
            """,
            (carrera_id, plan.nombre),
        )
        conexion.execute("DELETE FROM correlativas WHERE carrera_id = ?", (carrera_id,))
        if codigos_eliminados:
            placeholders = ",".join("?" for _ in codigos_eliminados)
            conexion.execute(
                "DELETE FROM materias WHERE carrera_id = ? AND codigo IN ({})".format(
                    placeholders
                ),
                (carrera_id, *sorted(codigos_eliminados)),
            )

        for materia in plan.materias:
            conexion.execute(
                """
                INSERT INTO materias
                    (carrera_id, codigo, asignatura, regimen, horas, anio)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT (carrera_id, codigo) DO UPDATE SET
                    asignatura = excluded.asignatura,
                    regimen = excluded.regimen,
                    horas = excluded.horas,
                    anio = excluded.anio
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
        for materia in plan.materias:
            for correlativa in materia.get_correlativas():
                conexion.execute(
                    """
                    INSERT INTO correlativas
                        (carrera_id, materia_codigo, correlativa_codigo)
                    VALUES (?, ?, ?)
                    """,
                    (carrera_id, materia.get_codigo(), correlativa),
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
