import sqlite3

from class_Materias import Materia
from repositorio import RepositorioAcademico
from scoring import (
    calcular_importancias_globales,
    puntuar_materias_cursables,
)
from siu_guarani import abrir_plan_estudio_siu, analizar_materias_aprobadas


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
        {
            "descripcion": nombre,
            "valor": carrera_id,
        }
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
            0,
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

    tablas = abrir_plan_estudio_siu()
    analisis = analizar_materias_aprobadas(tablas)
    materias_siu = analisis.materias_aprobadas
    print(
        "\nLectura del SIU: {} filas; {} con código; {} con tipo reconocido; "
        "{} con nota; {} materias aprobadas distintas.".format(
            analisis.filas_analizadas,
            analisis.filas_con_codigo,
            analisis.filas_con_tipo,
            analisis.filas_con_nota,
            len(materias_siu),
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

    if not materias_siu:
        print(
            "No se detectaron materias aprobadas: Promocionada, "
            "Regularizada con nota >= 6 o Examen con nota >= 4."
        )
        return

    plan = repositorio.obtener_plan(alumno["carrera_id"])
    calcular_importancias_globales(plan)
    materias_por_codigo = {
        materia.get_codigo(): materia for materia in plan
    }

    aprobadas_por_codigo = {}
    for materia in materias_siu:
        aprobadas_por_codigo[materia.codigo] = materia

    coincidentes = []
    sin_coincidencia = []
    print(
        "\nMaterias aprobadas detectadas para {} ({}):".format(
            alumno["nombre"], alumno["carrera_nombre"]
        )
    )
    for materia_siu in sorted(aprobadas_por_codigo.values(), key=lambda item: item.codigo):
        materia_plan = materias_por_codigo.get(materia_siu.codigo)
        print("  {}".format(formatear_materia_aprobada(materia_siu, materia_plan)))
        if materia_plan is None:
            sin_coincidencia.append(materia_siu)
        else:
            coincidentes.append(materia_siu)

    if sin_coincidencia:
        print(
            "\nSe omitirán {} materias cuyo código no pertenece al plan seleccionado.".format(
                len(sin_coincidencia)
            )
        )
    if not coincidentes:
        print("No hay materias coincidentes para guardar.")
        return

    respuesta = input(
        "\nGuardar/actualizar {} materias aprobadas? [s/N]: ".format(
            len(coincidentes)
        )
    ).strip().lower()
    if respuesta not in ("s", "si", "sí"):
        print("Importación cancelada; no se guardaron cambios.")
        return

    cantidad = repositorio.guardar_materias_aprobadas(
        alumno["id"], coincidentes
    )
    print("{} materias aprobadas guardadas.".format(cantidad))


def mostrar_recomendaciones(repositorio):
    alumno = seleccionar_alumno(repositorio)
    if alumno is None:
        return

    plan = repositorio.obtener_plan(alumno["carrera_id"])
    codigos_aprobados = repositorio.codigos_materias_aprobadas(alumno["id"])
    recomendaciones = puntuar_materias_cursables(plan, codigos_aprobados)

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


def main():
    repositorio = RepositorioAcademico()
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


if __name__ == "__main__":
    main()
