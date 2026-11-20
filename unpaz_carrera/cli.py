import argparse
import sqlite3

from unpaz_carrera.application.academic_service import (
    obtener_recomendaciones,
    preparar_importacion_materias,
)
from unpaz_carrera.domain.materia import Materia
from unpaz_carrera.domain.scoring import calcular_importancias_globales
from unpaz_carrera.infrastructure.repository import RepositorioAcademico
from unpaz_carrera.infrastructure.siu_guarani import abrir_plan_estudio_siu


def seleccionar_registro(registros, etiqueta):
    if not registros:
        print("No hay {} cargados.".format(etiqueta))
        return None

    for indice, registro in enumerate(registros):
        print(" {}: {}".format(indice, registro["descripcion"]))

    try:
        indice = int(input("Selecciona {}: ".format(etiqueta)))
    except ValueError:
        print("Ingresa un número de la lista.")
        return None

    if indice < 0 or indice >= len(registros):
        print("El número no corresponde a una opción.")
        return None
    return registros[indice]["valor"]


def seleccionar_alumno(repositorio):
    alumnos = repositorio.listar_alumnos()
    opciones = [
        {
            "descripcion": "{} | {}".format(
                alumno["nombre"], alumno["carrera_nombre"]
            ),
            "valor": alumno,
        }
        for alumno in alumnos
    ]
    return seleccionar_registro(opciones, "alumno")


def seleccionar_carrera(repositorio):
    carreras = repositorio.listar_carreras()
    opciones = [
        {"descripcion": nombre, "valor": carrera_id}
        for carrera_id, nombre in carreras
    ]
    return seleccionar_registro(opciones, "carrera")


def cargar_alumno(repositorio):
    nombre = input("Nombre del alumno: ").strip()
    carrera_id = seleccionar_carrera(repositorio)
    if carrera_id is None:
        return
    alumno_id = repositorio.crear_alumno(nombre, carrera_id)
    print("Alumno guardado con ID {}.".format(alumno_id))


def formatear_materia_aprobada(materia_siu, materia_plan):
    if materia_plan is None:
        materia_plan = Materia(
            materia_siu.codigo,
            materia_siu.nombre or "Materia sin nombre detectado",
            "",
            0,
            [],
            1,
        )
    return "{} | {} | nota {}".format(
        materia_plan,
        materia_siu.tipo_aprobacion,
        materia_siu.nota,
    )


def cargar_materias_aprobadas(repositorio):
    alumno = seleccionar_alumno(repositorio)
    if alumno is None:
        return

    importacion = preparar_importacion_materias(
        repositorio,
        alumno["id"],
        abrir_plan_estudio_siu(),
    )
    analisis = importacion.analisis
    print(
        "\nLectura del SIU: {} filas; {} con código; {} con tipo reconocido; "
        "{} con nota; {} materias aprobadas distintas.".format(
            analisis.filas_analizadas,
            analisis.filas_con_codigo,
            analisis.filas_con_tipo,
            analisis.filas_con_nota,
            len(analisis.materias_aprobadas),
        )
    )
    if analisis.descartadas:
        print("Muestra de filas descartadas:")
        for descartada in analisis.descartadas[:5]:
            print(
                "  [{}] {}".format(
                    descartada.motivo,
                    " | ".join(descartada.celdas),
                )
            )

    if not analisis.materias_aprobadas:
        print(
            "No se detectaron materias aprobadas: Promocionada, "
            "Regularizada con nota >= 6 o Examen con nota >= 4."
        )
        return

    plan = repositorio.obtener_plan(alumno["carrera_id"])
    calcular_importancias_globales(plan)
    materias_por_codigo = {materia.get_codigo(): materia for materia in plan}

    print(
        "\nMaterias aprobadas detectadas para {} ({}):".format(
            alumno["nombre"], alumno["carrera_nombre"]
        )
    )
    for materia in importacion.coincidentes + importacion.sin_coincidencia:
        print(
            "  {}".format(
                formatear_materia_aprobada(
                    materia, materias_por_codigo.get(materia.codigo)
                )
            )
        )

    if importacion.sin_coincidencia:
        print(
            "\nSe omitirán {} materias cuyo código no pertenece al plan seleccionado.".format(
                len(importacion.sin_coincidencia)
            )
        )
    if not importacion.coincidentes:
        print("No hay materias coincidentes para guardar.")
        return

    respuesta = input(
        "\nGuardar/actualizar {} materias aprobadas? [s/N]: ".format(
            len(importacion.coincidentes)
        )
    ).strip().lower()
    if respuesta not in ("s", "si", "sí"):
        print("Importación cancelada; no se guardaron cambios.")
        return

    cantidad = repositorio.guardar_materias_aprobadas(
        alumno["id"], importacion.coincidentes
    )
    print("{} materias aprobadas guardadas.".format(cantidad))


def mostrar_recomendaciones(repositorio):
    alumno = seleccionar_alumno(repositorio)
    if alumno is None:
        return

    recomendaciones = obtener_recomendaciones(repositorio, alumno["id"])
    codigos_aprobados = repositorio.codigos_materias_aprobadas(alumno["id"])
    print(
        "\nRecomendaciones para {} | {} | materias aprobadas: {}".format(
            alumno["nombre"],
            alumno["carrera_nombre"],
            len(codigos_aprobados),
        )
    )
    if not recomendaciones:
        print("No hay materias disponibles según las correlativas del plan.")
        return

    for recomendacion in recomendaciones:
        print(
            "{} | puntaje {:.2f}".format(
                recomendacion.materia,
                recomendacion.puntaje,
            )
        )
        for contribucion in recomendacion.contribuciones:
            estado = (
                "desbloqueo inmediato"
                if contribucion.materias_faltantes == 0
                else "MateriasFaltantes: {}".format(
                    contribucion.materias_faltantes
                )
            )
            print(
                "  {} | {} | importancia global {} | aporte {:.2f}".format(
                    estado,
                    contribucion.materia.get_asignatura(),
                    contribucion.importancia_global,
                    contribucion.puntos,
                )
            )


def main(argv=None):
    parser = argparse.ArgumentParser(prog="unpaz-carrera")
    parser.add_argument(
        "comando",
        nargs="?",
        choices=("sincronizar-planes",),
        help="actualiza los planes de JSON en SQLite sin borrar alumnos ni historial",
    )
    argumentos = parser.parse_args(argv)
    repositorio = RepositorioAcademico()

    if argumentos.comando == "sincronizar-planes":
        print(
            "{} planes sincronizados.".format(
                repositorio.sincronizar_planes()
            )
        )
        return

    while True:
        print(
            "\nMenu:\n"
            " 0: cargar alumno\n"
            " 1: cargar materias aprobadas desde SIU\n"
            " 2: recomendacion de materias\n"
            " 3: salir"
        )
        opcion = input("Opcion: ").strip()
        try:
            if opcion == "0":
                cargar_alumno(repositorio)
            elif opcion == "1":
                cargar_materias_aprobadas(repositorio)
            elif opcion == "2":
                mostrar_recomendaciones(repositorio)
            elif opcion == "3":
                break
            else:
                print("Opcion no reconocida.")
        except (RuntimeError, ValueError, sqlite3.Error) as error:
            print("No se pudo completar la operacion: {}".format(error))
