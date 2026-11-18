import re
import time
from dataclasses import dataclass


LOGIN_URL = "https://estudiantes.unpaz.edu.ar/autogestion/"
PLAN_URL = "https://estudiantes.unpaz.edu.ar/autogestion/plan_estudio"

ESTADOS_APROBADOS = (
    "aprobada",
    "aprobado",
    "promocionada",
    "promocionado",
)


@dataclass(frozen=True)
class TablaSiu:
    encabezados: tuple
    filas: tuple


@dataclass(frozen=True)
class MateriaAprobadaSiu:
    codigo: int
    nombre: str
    tipo_aprobacion: str
    nota: float


def _crear_driver():
    try:
        from selenium import webdriver
        from selenium.webdriver.edge.options import Options as EdgeOptions

        options = EdgeOptions()
        options.add_argument("--start-maximized")
        return webdriver.Edge(options=options)
    except Exception as edge_error:
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options as ChromeOptions

            options = ChromeOptions()
            options.add_argument("--start-maximized")
            return webdriver.Chrome(options=options)
        except Exception as chrome_error:
            raise RuntimeError(
                "No se pudo iniciar Microsoft Edge ni Google Chrome. "
                "Instala uno de los dos navegadores. "
                "Edge: {}; Chrome: {}".format(edge_error, chrome_error)
            )


def abrir_plan_estudio_siu(timeout_segundos=300):
    try:
        from selenium.webdriver.support.ui import WebDriverWait
    except ImportError:
        raise RuntimeError(
            "Falta Selenium. Instala las dependencias con "
            "`python -m pip install -r requirements.txt`."
        )

    driver = _crear_driver()
    try:
        driver.get(LOGIN_URL)
        input(
            "\nInicia sesión manualmente en el navegador. "
            "Cuando estés autenticado, presiona Enter aquí..."
        )

        driver.get(PLAN_URL)
        WebDriverWait(driver, 30).until(
            lambda navegador: navegador.execute_script(
                "return document.readyState"
            ) == "complete"
        )

        tablas = _extraer_tablas_html(driver)
        if not tablas:
            raise RuntimeError(
                "No se encontraron tablas en la página de plan de estudio."
            )
        return tablas
    except RuntimeError:
        raise
    except Exception as error:
        raise RuntimeError(
            "No se pudo navegar a la página del plan de estudio: {}".format(error)
        )
    finally:
        driver.quit()


def _normalizar_celda(texto):
    return " ".join((texto or "").split())


def _extraer_tablas_html(driver):
    try:
        from selenium.webdriver.common.by import By

        elementos = driver.find_elements(By.CSS_SELECTOR, "table")
    except Exception:
        return []

    tablas = []
    for elemento in elementos:
        encabezados = tuple(
            _normalizar_celda(celda.text)
            for celda in elemento.find_elements(By.CSS_SELECTOR, "thead tr th")
        )
        if not encabezados:
            encabezados = tuple(
                _normalizar_celda(celda.text)
                for celda in elemento.find_elements(By.CSS_SELECTOR, "tr:first-child th, tr:first-child td")
            )

        filas = []
        filas_html = elemento.find_elements(By.CSS_SELECTOR, "tbody tr")
        if not filas_html:
            filas_html = elemento.find_elements(By.CSS_SELECTOR, "tr")

        for fila in filas_html:
            celdas = tuple(
                _normalizar_celda(celda.text)
                for celda in fila.find_elements(By.CSS_SELECTOR, "th, td")
            )
            if celdas and any(celdas):
                filas.append(celdas)

        if filas:
            tablas.append(TablaSiu(encabezados, tuple(filas)))
    return tablas


def extraer_materias_aprobadas(tablas):
    materias = []

    for tabla in tablas:
        encabezados = tuple(encabezado.lower() for encabezado in tabla.encabezados)
        indices = {
            "codigo": _buscar_indice(encabezados, ("codigo", "código", "cod")),
            "materia": _buscar_indice(encabezados, ("materia", "asignatura", "actividad")),
            "estado": _buscar_indice(encabezados, ("estado", "condicion", "condición")),
            "nota": _buscar_indice(encabezados, ("nota", "calificacion", "calificación", "resultado")),
            "tipo": _buscar_indice(encabezados, ("tipo", "instancia", "modalidad", "acta")),
        }

        for fila in tabla.filas:
            texto = " | ".join(fila).lower()

            codigo = None
            if indices["codigo"] is not None and indices["codigo"] < len(fila):
                codigo = _buscar_codigo((fila[indices["codigo"]],), permitir_codigo_corto=True)
            if codigo is None:
                codigo = _buscar_codigo(fila)
            if codigo is None:
                continue

            nombre = _buscar_nombre(fila, indices)
            estado = _buscar_estado(fila, indices)
            tipo = _buscar_tipo(fila, indices)
            nota = _buscar_nota(fila, indices)

            if materia_aprobada(tipo, estado, texto, nota):
                materias.append(
                    MateriaAprobadaSiu(
                        codigo=codigo,
                        nombre=nombre,
                        tipo_aprobacion=tipo or estado,
                        nota=nota,
                    )
                )

    return sorted(set(materias), key=lambda materia: materia.codigo)


def _buscar_indice(encabezados, candidatos):
    for indice, encabezado in enumerate(encabezados):
        if any(candidato in encabezado for candidato in candidatos):
            return indice
    return None


def _buscar_codigo(partes, permitir_codigo_corto=False):
    for parte in partes:
        coincidencias = re.findall(r"\b\d{2,6}\b", parte)
        if coincidencias:
            codigo = int(coincidencias[0])
            if permitir_codigo_corto or codigo >= 100:
                return codigo
    return None


def _buscar_nombre(fila, indices):
    indice = indices["materia"]
    if indice is not None and indice < len(fila):
        return fila[indice]
    for celda in fila:
        if _buscar_codigo((celda,)) is None and celda:
            return celda
    return ""


def _buscar_estado(fila, indices):
    indice = indices["estado"]
    if indice is not None and indice < len(fila):
        return fila[indice]
    for celda in fila:
        texto = celda.lower()
        if any(estado in texto for estado in ESTADOS_APROBADOS):
            return celda
    return ""


def _buscar_tipo(fila, indices):
    indice = indices["tipo"]
    if indice is not None and indice < len(fila):
        return fila[indice]

    texto = " ".join(fila).lower()
    if "regulariz" in texto:
        return "Regularizada"
    if "examen" in texto:
        return "Examen"
    if "promocion" in texto:
        return "Promocionada"
    return ""


def _buscar_nota(fila, indices):
    indice = indices["nota"]
    if indice is not None and indice < len(fila):
        coincidencia = re.search(r"(\d+(?:[.,]\d+)?)", fila[indice].replace(",", "."))
        if coincidencia:
            return float(coincidencia.group(1))

    for celda in fila:
        coincidencia = re.search(r"\b([1-9]|10)(?:[.,]0)?\b", celda.replace(",", "."))
        if coincidencia:
            return float(coincidencia.group(1))
    return None


def materia_aprobada(tipo, estado, texto, nota):
    tipo_texto = "{} {}".format(tipo or "", estado or "").lower()
    tipo_texto = "{} {}".format(tipo_texto, texto)

    if nota is None:
        return False

    if "regulariz" in tipo_texto:
        return nota >= 6
    if "examen" in tipo_texto:
        return nota >= 4

    if "promocion" in tipo_texto:
        return nota >= 4
    if any(estado_aprobado in tipo_texto for estado_aprobado in ESTADOS_APROBADOS):
        return nota >= 4
    return False
