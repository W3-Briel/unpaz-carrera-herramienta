class Materia:
    def __init__(self, codigo, asignatura, regimen, horas, correlativas, año):
        self.codigo = int(codigo)
        self.asignatura = str(asignatura)
        self.regimen = str(regimen)
        self.horas = int(horas)
        self.correlativas = [int(codigo) for codigo in correlativas]
        self.año = int(año)
        self.importancia_directa = 0
        self.importancia_indirecta = 0
        self.importancia_total = 0

    def __str__(self):
        return (
            f"codigo {self.codigo}| año {self.año} | asignatura {self.asignatura} "
            f"| dependencias directas {self.importancia_directa} "
            f"| indirectas {self.importancia_indirecta} "
            f"| total {self.importancia_total}"
        )

    def get_codigo(self):
        return self.codigo

    def get_asignatura(self):
        return self.asignatura

    def get_regimen(self):
        return self.regimen

    def get_horas(self):
        return self.horas

    def get_correlativas(self):
        return self.correlativas

    def get_año(self):
        return self.año

    def get_importancia_directa(self):
        return self.importancia_directa

    def get_importancia_indirecta(self):
        return self.importancia_indirecta

    def get_importancia_total(self):
        return self.importancia_total

    def get_importancia(self):
        return self.importancia_total

    def set_importancias_globales(self, directas, indirectas):
        self.importancia_directa = directas
        self.importancia_indirecta = indirectas
        self.importancia_total = directas + indirectas

    def set_importancia(self, valor):
        self.importancia_total = valor