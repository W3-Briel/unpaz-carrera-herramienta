from class_Alumno import GestionAlumno
import requests as r

google_sheets = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQzPj8uSYB44A6gnN2JkoYYrdkFKy5hQyS60OAby5Db014n3tuJRaAKjSxlHq-20WWprHsU6qW4uK7M/pub?output=csv"
response = r.get(google_sheets)

alumnos_carrera_materias = response.text.replace("\r","").strip(",").split("\n")[1::]
alumnos_head = []

for i,alumno_text in enumerate(alumnos_carrera_materias):
    aux = alumno_text.split(",")
    alumnos_carrera_materias[i] = {"nombre": aux[0],
                                   "materias": aux[2:-1],
                                   "carrera": aux[1]
                                   }
    alumnos_head.append(f" {i}: {alumnos_carrera_materias[i]["nombre"]}")

def seleccionar_alumno():
    for i in alumnos_head: print(i)

    aux = alumnos_carrera_materias[int(input("indice del alumno: "))]
    instancia_alumno = GestionAlumno(aux["nombre"],aux["materias"],aux["carrera"])
    return instancia_alumno

while True:
    print("menu: que deseas hacer?\n 0: interseccion alumnos")

    opt = input("opcion: ").lower()
    match opt:
        case "0":
            lista_alumnos = []
            for i in range(int(input("entre cuantos alumnos?"))):
                lista_alumnos.append(seleccionar_alumno())
            
            lista_alumnos[0].interseccion_materias_desbloqueadas(lista_alumnos[1::])
            for m in lista_alumnos: print(m.get_asignatura())