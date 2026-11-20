from dataclasses import dataclass

from unpaz_carrera.domain.scoring import puntuar_materias_cursables
from unpaz_carrera.infrastructure.siu_guarani import (
    AnalisisSiu,
    analizar_materias_aprobadas,
)


@dataclass(frozen=True)
class ImportacionMaterias:
    analisis: AnalisisSiu
    coincidentes: tuple
    sin_coincidencia: tuple


def preparar_importacion_materias(repositorio, alumno_id, tablas):
    alumno = repositorio.obtener_alumno(alumno_id)
    analisis = analizar_materias_aprobadas(tablas)
    plan_por_codigo = {
        materia.get_codigo(): materia
        for materia in repositorio.obtener_plan(alumno["carrera_id"])
    }

    materias_por_codigo = {
        materia.codigo: materia for materia in analisis.materias_aprobadas
    }
    coincidentes = []
    sin_coincidencia = []
    for materia in sorted(materias_por_codigo.values(), key=lambda item: item.codigo):
        if materia.codigo in plan_por_codigo:
            coincidentes.append(materia)
        else:
            sin_coincidencia.append(materia)

    return ImportacionMaterias(
        analisis,
        tuple(coincidentes),
        tuple(sin_coincidencia),
    )


def obtener_recomendaciones(repositorio, alumno_id):
    alumno = repositorio.obtener_alumno(alumno_id)
    plan = repositorio.obtener_plan(alumno["carrera_id"])
    aprobadas = repositorio.codigos_materias_aprobadas(alumno_id)
    return puntuar_materias_cursables(plan, aprobadas)
