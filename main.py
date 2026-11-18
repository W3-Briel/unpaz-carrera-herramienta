from class_Alumno import GestionAlumno
import requests as r
from siu_guarani import (
    abrir_plan_estudio_siu,
    extraer_materias_aprobadas,
)
from Bexport_Bimport import Import

google_sheets = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQzPj8uSYB44A6gnN2JkoYYrdkFKy5hQyS60OAby5Db014n3tuJRaAKjSxlHq-20WWprHsU6qW4uK7M/pub?output=csv"
response = r.get(google_sheets)

alumnos_carrera_materias = response.text.replace("\r","").split("\n")[1:]
alumnos_head = []
for i,alumno_text in enumerate(alumnos_carrera_materias):
    aux = alumno_text.strip(",").split(",")
    alumnos_carrera_materias[i] = {"nombre": aux[0],
                                   "materias": aux[2:],
                                   "carrera": aux[1]
                                   }
    alumnos_head.append(f" {i}: {alumnos_carrera_materias[i]["nombre"]}")

def seleccionar_alumno():
    for i in alumnos_head: print(i)

    aux = alumnos_carrera_materias[int(input("indice del alumno: "))]
    instancia_alumno = GestionAlumno(aux["nombre"],aux["materias"],aux["carrera"])
    return instancia_alumno

def buscar_materia_plan(codigo):
    for carrera in ("LGTI", "COMERCIO_ELECTRONICO"):
        for materia in Import(carrera).get_load():
            if materia.get_codigo() == codigo:
                return materia
    return None

def formatear_materia_aprobada(materia_siu):
    materia_plan = buscar_materia_plan(materia_siu.codigo)
    if materia_plan is not None:
        return "{} | aprobada por {} | nota {}".format(
            materia_plan,
            materia_siu.tipo_aprobacion,
            materia_siu.nota,
        )
    return (
        "codigo {} | asignatura {} | aprobada por {} | nota {}".format(
            materia_siu.codigo,
            materia_siu.nombre,
            materia_siu.tipo_aprobacion,
            materia_siu.nota,
        )
    )

while True:
    print("menu: que deseas hacer?\n 0: interseccion alumnos\n 1: materias desbloqueadas\n 2: materias aprob\n 3: recomendar materias\n 4: importar materias desde SIU")

    opt = input("opcion: ").lower()
    match opt:
        case "0":
            lista_alumnos = []
            for i in range(int(input("entre cuantos alumnos?"))):
                lista_alumnos.append(seleccionar_alumno())
            
            materias = lista_alumnos[0].interseccion_materias_desbloqueadas(lista_alumnos[1::])
            for m in materias: print(m)
        case "1":
            alumno = seleccionar_alumno()
            for m in alumno.get_materias_desbloqueadas(): print(m)
        case "2":
            alumno = seleccionar_alumno()
            for m in alumno.get_materias_aprob(): print(m)
        case "3":
            alumno = seleccionar_alumno()
            for recomendacion in alumno.get_recomendaciones():
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
                        else "MateriasFaltantes: {}".format(contribucion.materias_faltantes)
                    )
                    print(
                        "  {} | {} | importancia global {} | aporte {:.2f}".format(
                            estado,
                            contribucion.materia.get_asignatura(),
                            contribucion.importancia_global,
                            contribucion.puntos,
                        )
                    )
        case "4":
            try:
                tablas = abrir_plan_estudio_siu()
                aprobadas = extraer_materias_aprobadas(tablas)
                print("Materias aprobadas detectadas:")
                for materia in aprobadas:
                    print("  {}".format(formatear_materia_aprobada(materia)))
                print("Codigos: {}".format(",".join(str(materia.codigo) for materia in aprobadas)))
            except RuntimeError as error:
                print("No se pudo importar desde el SIU: {}".format(error))
        case _:
            print("\n"*10,"bueno hace lo que quieras. chau")
            break