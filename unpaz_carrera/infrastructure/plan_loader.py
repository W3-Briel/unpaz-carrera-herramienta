import json
from dataclasses import dataclass
from pathlib import Path

from unpaz_carrera.domain.materia import Materia
from unpaz_carrera.domain.scoring import calcular_importancias_globales


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PLANS_DIRECTORY = PROJECT_ROOT / "data" / "planes"


@dataclass(frozen=True)
class PlanCarrera:
    identificador: str
    nombre: str
    materias: tuple


def cargar_planes(directorio=DEFAULT_PLANS_DIRECTORY):
    rutas = sorted(Path(directorio).glob("*.json"))
    if not rutas:
        raise ValueError("No hay archivos JSON de planes en {}.".format(directorio))

    planes = []
    ids = set()
    for ruta in rutas:
        try:
            with ruta.open(encoding="utf-8") as archivo:
                datos = json.load(archivo)
        except (OSError, json.JSONDecodeError) as error:
            raise ValueError("No se pudo leer el plan {}: {}".format(ruta, error))

        if not isinstance(datos, dict):
            raise ValueError("El plan {} debe contener un objeto JSON.".format(ruta))
        identificador = datos.get("id")
        nombre = datos.get("nombre")
        registros = datos.get("materias")
        if not isinstance(identificador, str) or not identificador.strip():
            raise ValueError("Falta un id de carrera válido en {}.".format(ruta))
        if identificador in ids:
            raise ValueError("Id de carrera duplicado: {}.".format(identificador))
        if not isinstance(nombre, str) or not nombre.strip():
            raise ValueError("Falta un nombre de carrera válido en {}.".format(ruta))
        if not isinstance(registros, list):
            raise ValueError("El campo materias debe ser una lista en {}.".format(ruta))

        materias = tuple(_cargar_materia(registro, ruta) for registro in registros)
        calcular_importancias_globales(materias)
        ids.add(identificador)
        planes.append(PlanCarrera(identificador, nombre, materias))

    return tuple(planes)


def _cargar_materia(registro, ruta):
    if not isinstance(registro, dict):
        raise ValueError("Materia inválida en {}.".format(ruta))
    try:
        codigo = _entero_positivo(registro["codigo"], "codigo")
        nombre = registro["asignatura"]
        regimen = registro["regimen"]
        horas = _entero_positivo(registro["horas"], "horas")
        anio = _entero_positivo(registro["anio"], "anio")
        correlativas = registro["correlativas"]
    except KeyError as error:
        raise ValueError(
            "Falta el campo {} en una materia de {}.".format(error.args[0], ruta)
        )

    if not isinstance(nombre, str) or not nombre.strip():
        raise ValueError("La materia {} tiene un nombre inválido.".format(codigo))
    if not isinstance(regimen, str) or not regimen.strip():
        raise ValueError("La materia {} tiene un régimen inválido.".format(codigo))
    if not isinstance(correlativas, list):
        raise ValueError("Las correlativas de {} deben ser una lista.".format(codigo))

    return Materia(codigo, nombre, regimen, horas, correlativas, anio)


def _entero_positivo(valor, campo):
    if isinstance(valor, bool) or not isinstance(valor, int) or valor <= 0:
        raise ValueError("{} debe ser un entero positivo.".format(campo))
    return valor
