from class_Materias import Materia

## con esta funcion, le pasamos una lista de codigos de materias(int), y otra lista de todas las materias (instancias de Materia)
## nos devuelve los objetos Materia que esten en la lista de codigos.

def buscar_obj_materias(codigos: list,plan_de_estudio: list):
    obj_materias = []
    for materia in plan_de_estudio:
        if materia.get_codigo() in codigos: obj_materias.append(materia)
    return obj_materias