# from Bexport_Bimport import Import
# from class_Materias import Materia
from class_Alumno import GestionAlumno

# materia = Import("LGTI").get_load()

hola = GestionAlumno("Angel",[6001,6002,6004,6013],"LGTI")

for i in hola.get_materias_aprob():
    print(i.get_importancia())

## materia aprobada => lista de codigo de materias que el alumno ingresa

## calcular la importancia de todas las materias (depende de las materias aprobadas del alumno)
## => cantidad de veces que aparece en el [conjunto listas de correlativas].count() de materias no aprobadas

## materias desbloqueadas => una materia estara desbloqueada si todas las correlativas estan aprobadas

## buscar interseccion entre dos sets de materias desbloqueadas