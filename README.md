# UNPAZ Carrera Herramienta

Aplicación de consola para registrar alumnos, importar materias aprobadas desde SIU Guaraní y recomendar materias mediante el plan de estudios y sus correlativas.

## Requisitos

- Python 3.12 o posterior.
- Microsoft Edge o Google Chrome.
- Acceso a internet para abrir SIU Guaraní.

Instala Selenium:

```powershell
python -m pip install -r requirements.txt
```

La aplicación usa SQLite incluido en Python. En el primer inicio crea `datos_academicos.sqlite3` e importa los planes existentes de `bin_Carreras`. La base de datos queda local y está excluida de Git.

## Uso

Ejecuta:

```powershell
python main.py
```

El menú permite:

0. **Cargar alumno:** ingresar el nombre y seleccionar una carrera cargada en la base.
1. **Cargar materias aprobadas:** seleccionar un alumno, iniciar sesión manualmente en SIU Guaraní, revisar las materias detectadas y confirmar cuáles guardar.
2. **Recomendación:** seleccionar un alumno y generar el ranking con el scoring existente, usando su plan y las materias aprobadas de SQLite.
3. **Salir.**

La importación SIU considera aprobadas las materias marcadas como `Promocionada`, `Regularizada` con nota 6 o superior, o `Examen` con nota 4 o superior. Las materias que no coincidan con el plan del alumno se muestran, pero no se guardan. Las credenciales no se solicitan ni se guardan.

Si necesitás volver a importar los planes desde los archivos binarios, cierra la aplicación y elimina manualmente `datos_academicos.sqlite3`. Esto también elimina los alumnos e historiales guardados.

## Scoring

El scoring cuenta las dependencias globales directas e indirectas y ordena las materias habilitadas considerando el impacto en materias pendientes y su distancia de correlativas. Los parámetros iniciales (`alpha = 1`, `decay = 0.5`) son experimentales; las distancias no representan cuatrimestres ni oferta real.

## Pruebas

```powershell
python -m unittest test_scoring test_siu_guarani test_repositorio -v
```
