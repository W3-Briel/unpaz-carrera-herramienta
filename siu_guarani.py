import re
import unicodedata
from dataclasses import dataclass


LOGIN_URL = "https://estudiantes.unpaz.edu.ar/autogestion/"
PLAN_URL = "https://estudiantes.unpaz.edu.ar/autogestion/plan_estudio"

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


@dataclass(frozen=True)
class FilaSiuDescartada:
    motivo: str
    celdas: tuple


@dataclass(frozen=True)
class AnalisisSiu:
    materias_aprobadas: tuple
    filas_analizadas: int
    filas_con_codigo: int
    filas_con_tipo: int
    filas_con_nota: int
    descartadas: tuple


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
        WebDriverWait(driver, timeout_segundos).until(
            lambda navegador: navegador.execute_script(
                "return document.readyState"
            ) == "complete"
        )
        if "/plan_estudio" not in driver.current_url:
            raise RuntimeError(
                "El SIU no abrió el plan de estudio; verifica que la sesión esté iniciada."
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
    return list(analizar_materias_aprobadas(tablas).materias_aprobadas)


def analizar_materias_aprobadas(tablas):
    materias_por_codigo = {}
    filas_analizadas = 0
    filas_con_codigo = 0
    filas_con_tipo = 0
    filas_con_nota = 0
    descartadas = []

    for tabla in tablas:
        encabezados = tuple(encabezado.lower() for encabezado in tabla.encabezados)
        indices = {
            "codigo": _buscar_indice(encabezados, ("codigo", "código", "cod")),
            "materia": _buscar_indice(encabezados, ("materia", "asignatura", "actividad")),
            "estado": _buscar_indice(encabezados, ("estado", "condicion", "condición")),
            "nota": _buscar_indice(
                encabezados,
                (
                    "nota",
                    "calificacion",
                    "calificación",
                    "calif",
                    "resultado",
                    "puntaje",
                ),
            ),
            "tipo": _buscar_indice(encabezados, ("tipo", "instancia", "modalidad", "acta")),
        }

        for fila in tabla.filas:
            if not any(fila):
                continue
            filas_analizadas += 1
            texto = " | ".join(fila).lower()

            codigo = None
            if indices["codigo"] is not None and indices["codigo"] < len(fila):
                codigo = _buscar_codigo((fila[indices["codigo"]],), permitir_codigo_corto=True)
            else:
                codigo = _buscar_codigo(fila)
            if codigo is None:
                _agregar_descartada(descartadas, "no se identificó el código", fila)
                continue

            nombre = _buscar_nombre(fila, indices)
            estado = _buscar_estado(fila, indices)
            tipo = _buscar_tipo(fila, indices)
            nota = _buscar_nota(fila, indices)
            filas_con_codigo += 1

            tipo_aprobacion = _normalizar_tipo_aprobacion(tipo, estado, texto)
            if tipo_aprobacion:
                filas_con_tipo += 1
            if nota is not None:
                filas_con_nota += 1

            if not tipo_aprobacion:
                _agregar_descartada(
                    descartadas, "no se identificó Regularizada o Examen", fila
                )
                continue
            if nota is None:
                _agregar_descartada(descartadas, "no se identificó una nota", fila)
                continue
            if not materia_aprobada(tipo, estado, texto, nota):
                minimo = 6 if tipo_aprobacion == "Regularizada" else 4
                _agregar_descartada(
                    descartadas,
                    "nota {} menor al mínimo {}".format(nota, minimo),
                    fila,
                )
                continue

            materia = MateriaAprobadaSiu(
                codigo=codigo,
                nombre=nombre,
                tipo_aprobacion=tipo_aprobacion,
                nota=nota,
            )
            anterior = materias_por_codigo.get(codigo)
            prioridad = (
                1 if tipo_aprobacion == "Examen" else 0,
                nota,
            )
            prioridad_anterior = (
                (
                    1 if anterior.tipo_aprobacion == "Examen" else 0,
                    anterior.nota,
                )
                if anterior
                else None
            )
            if prioridad_anterior is None or prioridad > prioridad_anterior:
                materias_por_codigo[codigo] = materia

    return AnalisisSiu(
        materias_aprobadas=tuple(
            sorted(materias_por_codigo.values(), key=lambda materia: materia.codigo)
        ),
        filas_analizadas=filas_analizadas,
        filas_con_codigo=filas_con_codigo,
        filas_con_tipo=filas_con_tipo,
        filas_con_nota=filas_con_nota,
        descartadas=tuple(descartadas),
    )


def _agregar_descartada(descartadas, motivo, fila):
    if len(descartadas) < 10:
        descartadas.append(FilaSiuDescartada(motivo, tuple(fila)))


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
        if "regulariz" in texto or "examen" in texto:
            return celda
    return ""


def _buscar_tipo(fila, indices):
    indice = indices["tipo"]
    if indice is not None and indice < len(fila):
        if fila[indice]:
            return fila[indice]

    texto = " ".join(fila).lower()
    if "regulariz" in texto:
        return "Regularizada"
    if "examen" in texto:
        return "Examen"
    return ""


def _buscar_nota(fila, indices):
    indice = indices["nota"]
    if indice is None or indice >= len(fila):
        return None
    return _parsear_nota(fila[indice])


def _parsear_nota(texto):
    coincidencia = re.fullmatch(
        r"\s*(10(?:[.,]0+)?|[0-9](?:[.,][0-9]+)?)"
        r"(?:\s*\([^)]*\))?\s*",
        texto or "",
    )
    if coincidencia:
        return float(coincidencia.group(1).replace(",", "."))
    return None


def materia_aprobada(tipo, estado, texto, nota):
    if nota is None:
        return False

    tipo_aprobacion = _normalizar_tipo_aprobacion(tipo, estado, texto)
    if tipo_aprobacion == "Promocionada":
        return True
    if tipo_aprobacion == "Regularizada":
        return nota >= 6
    if tipo_aprobacion == "Examen":
        return nota >= 4
    return False


def _normalizar_tipo_aprobacion(tipo, estado, texto):
    tipo_texto = "{} {} {}".format(tipo or "", estado or "", texto).lower()
    tipo_texto = "".join(
        caracter
        for caracter in unicodedata.normalize("NFKD", tipo_texto)
        if not unicodedata.combining(caracter)
    )
    if re.search(r"\bno\s+promocion", tipo_texto):
        return ""
    if "regulariz" in tipo_texto:
        return "Regularizada"
    if "examen" in tipo_texto:
        return "Examen"
    if "promocion" in tipo_texto:
        return "Promocionada"
    return ""
