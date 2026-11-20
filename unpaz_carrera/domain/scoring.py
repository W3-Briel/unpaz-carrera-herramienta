from dataclasses import dataclass
import math


@dataclass(frozen=True)
class ImportanciaGlobal:
    directas: int
    indirectas: int
    total: int


@dataclass(frozen=True)
class ContribucionPuntaje:
    materia: object
    materias_faltantes: int
    importancia_global: int
    puntos: float


@dataclass(frozen=True)
class PuntajeRecomendacion:
    materia: object
    puntaje: float
    desbloqueos_inmediatos: tuple
    dependientes_directos_pendientes: tuple
    dependientes_indirectos_pendientes: tuple
    contribuciones: tuple


def _codigo_entero(codigo, contexto):
    try:
        return int(codigo)
    except (TypeError, ValueError):
        raise ValueError("Código de materia inválido en {}: {!r}".format(contexto, codigo))


def _construir_grafo(plan):
    if not plan:
        raise ValueError("El plan de estudios está vacío.")

    materias = {}
    correlativas = {}

    for materia in plan:
        codigo = _codigo_entero(materia.get_codigo(), "el plan")
        if codigo in materias:
            raise ValueError("Código de materia duplicado en el plan: {}".format(codigo))

        materias[codigo] = materia
        correlativas[codigo] = {
            _codigo_entero(correlativa, "las correlativas de {}".format(codigo))
            for correlativa in (materia.get_correlativas() or [])
        }

    for codigo, requisitos in correlativas.items():
        if codigo in requisitos:
            raise ValueError("La materia {} no puede ser correlativa de sí misma.".format(codigo))
        faltantes = requisitos - materias.keys()
        if faltantes:
            raise ValueError(
                "La materia {} tiene correlativas inexistentes: {}.".format(
                    codigo, sorted(faltantes)
                )
            )

    dependientes = {codigo: set() for codigo in materias}
    for codigo, requisitos in correlativas.items():
        for requisito in requisitos:
            dependientes[requisito].add(codigo)

    descendientes = {}
    visitando = set()

    def obtener_descendientes(codigo):
        if codigo in descendientes:
            return descendientes[codigo]
        if codigo in visitando:
            raise ValueError("El plan tiene un ciclo de correlativas que incluye {}.".format(codigo))

        visitando.add(codigo)
        resultado = set()
        for dependiente in dependientes[codigo]:
            resultado.add(dependiente)
            resultado.update(obtener_descendientes(dependiente))
        visitando.remove(codigo)
        descendientes[codigo] = resultado
        return resultado

    for codigo in materias:
        obtener_descendientes(codigo)

    return materias, correlativas, dependientes, descendientes


def _calcular_importancias(materias, dependientes, descendientes):
    importancias = {}
    for codigo, materia in materias.items():
        directas = len(dependientes[codigo])
        indirectas = len(descendientes[codigo] - dependientes[codigo])
        importancia = ImportanciaGlobal(directas, indirectas, directas + indirectas)
        materia.set_importancias_globales(directas, indirectas)
        importancias[codigo] = importancia
    return importancias


def calcular_importancias_globales(plan):
    materias, _, dependientes, descendientes = _construir_grafo(plan)
    return _calcular_importancias(materias, dependientes, descendientes)


def _normalizar_aprobadas(codigos):
    resultado = set()
    for codigo in codigos:
        if isinstance(codigo, str) and not codigo.strip():
            continue
        resultado.add(_codigo_entero(codigo, "el historial del alumno"))
    return resultado


def _calcular_materias_faltantes(materias, correlativas, aprobadas, candidata):
    completadas = set(aprobadas)
    completadas.add(candidata)
    pendientes = set(materias) - completadas
    materias_faltantes = {}
    cantidad = 0

    # Se asume que el alumno completa todas las materias habilitadas en el mismo nivel de MateriasFaltantes.
    while pendientes:
        disponibles = {
            codigo for codigo in pendientes
            if correlativas[codigo].issubset(completadas)
        }
        if not disponibles:
            raise ValueError("No se pudieron resolver las correlativas restantes del plan.")

        for codigo in disponibles:
            materias_faltantes[codigo] = cantidad
        completadas.update(disponibles)
        pendientes.difference_update(disponibles)
        cantidad += 1

    return materias_faltantes


def puntuar_materias_cursables(plan, codigos_aprobados, alpha=1.0, decay=0.5):
    try:
        alpha = float(alpha)
        decay = float(decay)
    except (TypeError, ValueError):
        raise ValueError("alpha y decay deben ser numéricos.")

    if not math.isfinite(alpha) or alpha < 0:
        raise ValueError("alpha debe ser un número finito mayor o igual a cero.")
    if not math.isfinite(decay) or decay < 0 or decay > 1:
        raise ValueError("decay debe estar entre cero y uno.")

    materias, correlativas, dependientes, descendientes = _construir_grafo(plan)
    importancias = _calcular_importancias(materias, dependientes, descendientes)
    aprobadas = _normalizar_aprobadas(codigos_aprobados)

    fuera_del_plan = aprobadas - materias.keys()
    if fuera_del_plan:
        raise ValueError(
            "El historial contiene códigos que no están en el plan: {}.".format(
                sorted(fuera_del_plan)
            )
        )

    maxima_importancia = max((item.total for item in importancias.values()), default=0)
    recomendaciones = []

    for codigo, materia in materias.items():
        if codigo in aprobadas or not correlativas[codigo].issubset(aprobadas):
            continue

        materias_faltantes = _calcular_materias_faltantes(materias, correlativas, aprobadas, codigo)
        pendientes_dependientes = descendientes[codigo] - aprobadas
        directos_pendientes = dependientes[codigo] & pendientes_dependientes
        indirectos_pendientes = pendientes_dependientes - dependientes[codigo]
        inmediatos = {
            dependiente for dependiente in directos_pendientes
            if (correlativas[dependiente] - {codigo}).issubset(aprobadas)
        }

        contribuciones = []
        for dependiente in pendientes_dependientes:
            importancia_global = importancias[dependiente].total
            importancia_normalizada = (
                importancia_global / maxima_importancia if maxima_importancia else 0
            )
            puntos = (decay ** materias_faltantes[dependiente]) * (
                1 + alpha * importancia_normalizada
            )
            contribuciones.append(
                ContribucionPuntaje(
                    materias[dependiente],
                    materias_faltantes[dependiente],
                    importancia_global,
                    puntos,
                )
            )

        contribuciones.sort(
            key=lambda item: (
                item.materias_faltantes,
                item.materia.get_año(),
                item.materia.get_codigo(),
            )
        )
        recomendaciones.append(
            PuntajeRecomendacion(
                materia=materia,
                puntaje=sum(item.puntos for item in contribuciones),
                desbloqueos_inmediatos=tuple(
                    materias[codigo_inmediato]
                    for codigo_inmediato in sorted(inmediatos)
                ),
                dependientes_directos_pendientes=tuple(
                    materias[codigo_directo]
                    for codigo_directo in sorted(directos_pendientes)
                ),
                dependientes_indirectos_pendientes=tuple(
                    materias[codigo_indirecto]
                    for codigo_indirecto in sorted(indirectos_pendientes)
                ),
                contribuciones=tuple(contribuciones),
            )
        )

    recomendaciones.sort(key=lambda item: item.puntaje, reverse=True)
    return recomendaciones
