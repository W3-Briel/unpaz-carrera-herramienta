from class_Alumno import GestionAlumno

## Con la instancia "alumno" gestionamos y calculamos la importancia de las materias aprobadas, y desbloqueadas.
alumno1 = GestionAlumno("Angel",[6001,6002,6003,6005,6006,6007,6038,6041,6043],"LGTI")
alumno2 = GestionAlumno("Nelson",[6001,6002,6003,6004,6010,6011],"LGTI")

## metodo para ver las materias que podrian cursar la instancia alumno1 con una lista de otros alumnos
for i in alumno1.interseccion_materias_desbloqueadas([alumno2]): print(i)