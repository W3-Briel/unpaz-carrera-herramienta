from class_Materias import Materia
from Bexport_Bimport import Import
from herramientas import buscar_obj_materias
from scoring import puntuar_materias_cursables

class Alumno:
    def __init__(self, nombre: str, cod_materias_aprob: list, carrera: str):
        self.nombre, self.cod_materias_aprob, self.carrera = nombre, cod_materias_aprob, carrera
    
    ##getters
    def get_nombre(self): return self.nombre
    def get_cod_materias_aprob(self): return self.cod_materias_aprob
    def get_carrera(self): return self.carrera

class GestionAlumno(Alumno):
    def __init__(self,nombre: str, cod_materias_aprob: list, carrera: str):
        super().__init__(nombre, cod_materias_aprob, carrera)

        self.cod_materias_aprob = []
        for cod in cod_materias_aprob:
            if isinstance(cod, str) and not cod.strip():
                continue
            try:
                codigo = int(cod)
            except (TypeError, ValueError):
                raise ValueError("Código de materia aprobada inválido: {!r}".format(cod))
            if codigo not in self.cod_materias_aprob:
                self.cod_materias_aprob.append(codigo)

        self.plan_de_estudio = Import(super().get_carrera()).get_load()
        self.recomendaciones = puntuar_materias_cursables(
            self.plan_de_estudio, self.cod_materias_aprob
        )
        codigos_aprobados = set(self.cod_materias_aprob)
        self.materias_aprob = [
            materia for materia in self.plan_de_estudio
            if materia.get_codigo() in codigos_aprobados
        ]
        self.materias_desbloqueadas = [
            recomendacion.materia for recomendacion in self.recomendaciones
        ]
        self.cod_materias_desbloqueadas = [
            materia.get_codigo() for materia in self.materias_desbloqueadas
        ]
    ##getters
    def get_materias_aprob(self): return self.materias_aprob
    def get_materias_desbloqueadas(self): return self.materias_desbloqueadas
    def get_plan_de_estudio(self): return self.plan_de_estudio
    def get_recomendaciones(self): return self.recomendaciones
    # def get_cod_materias_aprob(self): return self.cod_materias_aprob # es un metodo heredado.
    def get_cod_materias_desbloqueadas(self): return self.cod_materias_desbloqueadas

    ## interseccion de materias desbloqueadas entre uno o mas alumnos
    def interseccion_materias_desbloqueadas(self,list_alumnos: list):
        interseccion = set(self.get_cod_materias_desbloqueadas())
        m_temp = list()

        for compañero in list_alumnos:
            ## metemos las instancias de Materias en m_temp, para luego no iterar en todas las materias del plan de estudio
            m_temp += compañero.get_materias_desbloqueadas()
            interseccion = interseccion.intersection(compañero.get_cod_materias_desbloqueadas())
        
        obj_interseccion_materias = buscar_obj_materias(list(interseccion),m_temp); del m_temp

        return obj_interseccion_materias