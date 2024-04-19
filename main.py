from funtions import herramientas
from model import Alumno


## para utilizar el programa, instanciamos un objeto Alumno y le pasamos el nombre de la carrera y luego settear las materias aprobadas.
## el cual, despues de un trabajo de dataEntry deberia estar en un archivo binario para trabajarlo.

angel = Alumno("LGTI")
angel.set_materias_aprobas([6001,6002,6003,6004,6005,6006,6007,6008])

# luci = a.Alumno("LGTI")
# luci.set_materias_aprobas([6001,6002,6003,6004,6005,6006,6007,6008,6010,6009,6011,6014])

for i in angel.get_materias_desbloqueadas():
    i.show_info()

# ## mostramos la interseccion entre una lista de Alumnos
# for i in herramientas.interseccion([luci,angel]):
#     angel.buscar_materia(i).show_info()
#     print("*"*20)