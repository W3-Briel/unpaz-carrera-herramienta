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
        self.cod_list_correlativas = []

        ## iteramos en todas las materias.get_codigo() y vemos si estan dentro de la lista de aprobadas.
        ## tambien, aprovechamos las iteraciones y agregamos la lista de correlativas de todas las no aprobadas.

        for materia in Import(super().get_carrera()).get_load():
            agregar_materia = (materia.get_codigo() in self.cod_materias_aprob) and (len(self.cod_materias_aprob) > len(self.materias_aprob))    
            if agregar_materia:
                self.materias_aprob.append(materia)
                continue
            self.cod_list_correlativas += materia.get_correlativas()
        
        ## setteamos la importancia de todas las materias aprobadas.
        for importancia in self.materias_aprob:
            importancia.set_importancia(self.cod_list_correlativas.count(importancia.get_codigo()))

    ##getters
    def get_materias_aprob(self): return self.materias_aprob