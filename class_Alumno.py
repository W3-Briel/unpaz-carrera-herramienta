from class_Materias import Materia
from Bexport_Bimport import Import
from herramientas import buscar_obj_materias

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
        for cod in cod_materias_aprob: self.cod_materias_aprob.append(int(cod))

        self.materias_aprob = []
        self.cod_list_correlativas = []

        self.materias_desbloqueadas = []
        self.cod_materias_desbloqueadas = []

        ## iteramos todas las materias de la carrera y, buscamos las instancias de materias aprobadas,
        ## si no esta aprobada se prosigue a ver si es una materia desbloqueada.
        self.plan_de_estudio = Import(super().get_carrera()).get_load()
        for materia in self.plan_de_estudio:
            agregar_materia = (materia.get_codigo() in self.cod_materias_aprob) and (len(self.cod_materias_aprob) > len(self.materias_aprob))
            if agregar_materia:
                self.materias_aprob.append(materia)
                continue
            m_desbloqueada = set(self.cod_materias_aprob).issuperset(materia.get_correlativas())
            if m_desbloqueada or (len(materia.get_correlativas()) == 0): 
                self.materias_desbloqueadas.append(materia)
                self.cod_materias_desbloqueadas.append(materia.get_codigo())
            self.cod_list_correlativas += materia.get_correlativas()
        
        ## setteamos la importancia de todas las materias aprobadas y materias desbloqueadas.
        calc_importancia = self.materias_aprob+self.materias_desbloqueadas
        for importancia in calc_importancia:
            importancia.set_importancia(self.cod_list_correlativas.count(importancia.get_codigo()))
    ##getters
    def get_materias_aprob(self): return self.materias_aprob
    def get_materias_desbloqueadas(self): return self.materias_desbloqueadas
    def get_plan_de_estudio(self): return self.plan_de_estudio
    # def get_cod_materias_aprob(self): return self.cod_materias_aprob # es un metodo heredado.
    def get_cod_materias_desbloqueadas(self): return self.cod_materias_desbloqueadas

    ## interseccion de materias desbloqueadas entre uno o mas alumnos
    def interseccion_materias_desbloqueadas(self,list_alumnos: list):
        interseccion = set(self.get_cod_materias_desbloqueadas())
        m_temp = list()

        for alumno in list_alumnos:
            ## metemos las instancias de Materias en m_temp, para luego no iterar en todas las materias del plan de estudio
            m_temp += alumno.get_materias_desbloqueadas()
            interseccion = interseccion.intersection(alumno.get_cod_materias_desbloqueadas())
        
        obj_interseccion_materias = buscar_obj_materias(list(interseccion),m_temp); del m_temp

        return obj_interseccion_materias