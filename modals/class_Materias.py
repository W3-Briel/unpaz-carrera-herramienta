# m1 = Materia(6001,"Análisis Matemático I","Cuatrimestral",4,[],1)

class Materia:
    def __init__(self,codigo: int, asignatura: str, regimen: str, horas: int,correlativas: list,año: int):
        self.codigo, self.asignatura, self.regimen, self.horas, self.correlativas, self.año = codigo, asignatura, regimen, horas, correlativas, año

    ## getters
    def get_codigo(self): return self.codigo
    def get_asignatura(self): return self.asignatura
    def get_regimen(self): return self.regimen
    def get_horas(self): return self.horas
    def get_correlativas(self): return self.correlativas
    def get_año(self): return self.año