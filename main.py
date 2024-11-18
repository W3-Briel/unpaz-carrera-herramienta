from class_Alumno import GestionAlumno
import requests as r

google_sheets = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQzPj8uSYB44A6gnN2JkoYYrdkFKy5hQyS60OAby5Db014n3tuJRaAKjSxlHq-20WWprHsU6qW4uK7M/pub?output=csv"
response = r.get(google_sheets)

alumnos_carrera_materias = response.text.replace("\r","").strip(",").split("\n")[1::]
for alumno_text in alumnos_carrera_materias:
    aux = alumno_text.split(",")
    alumno = {
        "nombre": aux[0],
        "materias": aux[2:-1],
        "carrera": aux[1]
    }
    print(alumno)
    instancia = GestionAlumno(alumno["nombre"],alumno["materias"],alumno["carrera"])

    for i in instancia.get_materias_desbloqueadas(): print(i)