from class_Materias import Materia

## con esta funcion, le pasamos una lista de codigos de materias(int), y otra lista de todas las materias (instancias de Materia)
## nos devuelve los objetos Materia que esten en la lista de codigos.

def buscar_obj_materias(codigos: list,plan_de_estudio: list):
    obj_materias = []
    cod_agregados = []

    for materia in plan_de_estudio:
        m_codigo = materia.get_codigo()
        if (m_codigo in codigos) and (m_codigo not in cod_agregados): 
            cod_agregados.append(m_codigo)
            obj_materias.append(materia)

    return obj_materias