from Bexport_Bimport import Import
from class_Materias import Materia

materia = Import("LGTI").get_load()


## calcular la importancia de todas las materias => 

## materias desbloqueadas => una materia estara desbloqueada si todas las correlativas estan aprobadas

## buscar interseccion entre dos sets de materias desbloqueadas