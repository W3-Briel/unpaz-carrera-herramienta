from class_Materias import Materia
from Bexport_Bimport import Import

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

        self.materias_aprob = []
        self.materias_desbloqueadas = []
        self.cod_list_correlativas = []

        ## iteramos todas las materias de la carrera y, buscamos las instancias de materias aprobadas,
        ## si no esta aprobada se prosigue a ver si es una materia desbloqueada.
        for materia in Import(super().get_carrera()).get_load():
            agregar_materia = (materia.get_codigo() in self.cod_materias_aprob) and (len(self.cod_materias_aprob) > len(self.materias_aprob))    
            if agregar_materia:
                self.materias_aprob.append(materia)
                continue
            m_desbloqueada = set(cod_materias_aprob).issuperset(materia.get_correlativas())
            if m_desbloqueada or (len(materia.get_correlativas()) == 0): self.materias_desbloqueadas.append(materia)
            self.cod_list_correlativas += materia.get_correlativas()
        
        ## setteamos la importancia de todas las materias aprobadas y materias desbloqueadas.
        calc_importancia = self.materias_aprob+self.materias_desbloqueadas
        for importancia in calc_importancia:
            importancia.set_importancia(self.cod_list_correlativas.count(importancia.get_codigo()))

    ##getters
    def get_materias_aprob(self): return self.materias_aprob
    def get_materias_desbloqueadas(self): return self.materias_desbloqueadas