# m1 = Materia(6001,"Análisis Matemático I","Cuatrimestral",4,[],1)

class Materia:
    def __init__(self,codigo: int, asignatura: str, regimen: str, horas: int,correlativas: list,año: int):
        self.codigo, self.asignatura, self.regimen, self.horas, self.correlativas, self.año = codigo, asignatura, regimen, horas, correlativas, año
        
        self.importancia_directa = 0
        self.importancia_indirecta = 0
        self.importancia_total = 0
        self.importancia = 0

    def __str__(self):
        return (
            f"codigo {self.codigo}| año {self.año} | asignatura {self.asignatura} "
            f"| dependencias directas {self.get_importancia_directa()} "
            f"| indirectas {self.get_importancia_indirecta()} "
            f"| total {self.get_importancia_total()}"
        )

    ## getters
    def get_codigo(self): return self.codigo
    def get_asignatura(self): return self.asignatura
    def get_regimen(self): return self.regimen
    def get_horas(self): return self.horas
    def get_correlativas(self): return self.correlativas
    def get_año(self): return self.año
    def get_importancia_directa(self): return getattr(self, "importancia_directa", 0)
    def get_importancia_indirecta(self): return getattr(self, "importancia_indirecta", 0)
    def get_importancia_total(self): return getattr(self, "importancia_total", getattr(self, "importancia", 0))
    def get_importancia(self): return self.get_importancia_total()

    ## setters
    def set_importancias_globales(self, directas, indirectas):
        self.importancia_directa = directas
        self.importancia_indirecta = indirectas
        self.importancia_total = directas + indirectas
        self.importancia = self.importancia_total

    def set_importancia(self, x):
        self.importancia = x
        self.importancia_total = x