## calcular la interseccion entre listas de materias de alumnos
## devuelve una lista de codigos.

def interseccion(alumnos: list):
    try:
        interseccion = set()
        for alumno in alumnos:
            if len(interseccion) == 0:
                for materia in alumno.get_materias_desbloqueadas():
                    interseccion.add(materia.get_codigo())
                continue
            materias = set()
            for i in alumno.get_materias_desbloqueadas():
                materias.add(i.get_codigo())
            interseccion &= materias
        return list(interseccion)
    except: print("error en parametros")