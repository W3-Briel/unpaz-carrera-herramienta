from class_Alumno import GestionAlumno

## Con la instancia "alumno" gestionamos y calculamos la importancia de las materias aprobadas, y desbloqueadas.
alumno1 = GestionAlumno("Angel",[6001,6002,6003,6004,6005],"LGTI")
den = GestionAlumno("den",[6001,6002,6003,6004,6005,6006,6007,6008,6038,6010,6019],"LGTI")

# for i in alumno1.get_materias_aprob(): print(i)

paulina = GestionAlumno("Paulina",[6001],"LGTI")

## metodo para ver las materias que podrian cursar la instancia alumno1 con una lista de otros alumnos
for i in alumno1.interseccion_materias_desbloqueadas([den]): print(i)