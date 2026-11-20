# UNPAZ Carrera Herramienta

Aplicación de consola para registrar alumnos, importar materias aprobadas desde SIU Guaraní y recomendar materias mediante el plan de estudios y sus correlativas.

## Arquitectura

- `unpaz_carrera/domain`: modelo de materia y scoring.
- `unpaz_carrera/application`: casos de uso académicos.
- `unpaz_carrera/infrastructure`: SQLite, carga de planes y acceso al SIU.
- `data/planes`: definición fuente de los planes en JSON. Al inicializarse la base se cargan a SQLite; el resto de la aplicación usa SQLite.
- `tests`: pruebas unitarias y de integración.

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

Para aplicar cambios de `data/planes/*.json` a una base existente sin borrar alumnos ni historiales:

```powershell
python -m unpaz_carrera sincronizar-planes
```

La sincronización actualiza materias y correlativas en una transacción. Si el plan intenta quitar una materia que figura como aprobada por algún alumno, la operación se cancela y conserva los datos.

El menú permite:

0. **Cargar alumno:** ingresar el nombre y seleccionar una carrera cargada en la base.
1. **Cargar materias aprobadas:** seleccionar un alumno, iniciar sesión manualmente en SIU Guaraní, revisar las materias detectadas y confirmar cuáles guardar.
2. **Recomendación:** seleccionar un alumno y generar el ranking con el scoring existente, usando su plan y las materias aprobadas de SQLite.
3. **Salir.**

La importación SIU considera aprobadas las materias marcadas como `Promocionada`, `Regularizada` con nota 6 o superior, o `Examen` con nota 4 o superior. Las materias que no coincidan con el plan del alumno se muestran, pero no se guardan. Las credenciales no se solicitan ni se guardan.

Los cambios en los JSON no modifican la base automáticamente: ejecuta el comando de sincronización. Borrar `datos_academicos.sqlite3` elimina también alumnos e historiales y no es necesario para actualizar los planes.

## Scoring

El scoring cuenta las dependencias globales directas e indirectas y ordena las materias habilitadas considerando el impacto en materias pendientes y su distancia de correlativas. Los parámetros iniciales (`alpha = 1`, `decay = 0.5`) son experimentales; las distancias no representan cuatrimestres ni oferta real.

## Pruebas

```powershell
python -m unittest discover -s tests -v
```
