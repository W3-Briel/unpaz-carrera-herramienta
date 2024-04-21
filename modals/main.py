from class_Alumno import GestionAlumno

## Con la instancia "alumno" gestionamos y calculamos la importancia de las materias aprobadas, y desbloqueadas.
alumno = GestionAlumno("Angel",[],"LGTI")

for i in alumno.get_materias_aprob():
    print(i)

print("*"*10)
for i in alumno.get_materias_desbloqueadas():
    print(i)