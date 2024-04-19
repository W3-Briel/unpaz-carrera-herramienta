class Materia:
    def __init__(self,codigo,asignatura,regimen,horas_semanales,correlativas,año):
        self.codigo = codigo
        self.asignatura = asignatura
        self.regimen = regimen
        self.horas_semanales = horas_semanales
        self.correlativas = correlativas
        self.año = año

        self.importancia = 0
        self.materias_que_la_piden = []
    def __str__(self):
        return f"codigo {self.codigo}| año {self.año} | asignatura {self.asignatura}"
    #metodos

    # getters
    def get_codigo(self):
        return self.codigo
    def get_asignatura(self):
        return self.asignatura
    def get_regimen(self):
        return self.regimen
    def get_horas_semanales(self):
        return self.horas_semanales
    def get_correlativas(self):
        return self.correlativas
    def get_importancia(self):
        return self.importancia
    def get_materias_que_la_piden(self):
        return self.materias_que_la_piden
    def get_año(self):
        return self.año

    # setters
    def set_importancia(self):
        self.importancia = len(self.get_materias_que_la_piden())

    def set_materias_que_la_piden(self,materias):
        return self.materias_que_la_piden.append(materias)

    # prints
    def show_info(self):
        print(f"codigo: {self.codigo}")
        print(f"asignatura: {self.asignatura}")
        print(f"año : {self.año}")
        print(f"regimen: {self.regimen}")
        print(f"hora_semanales: {self.horas_semanales}")
        print(f"correlativas: {self.correlativas}")
        print(f"importancia: {self.importancia}")
        print(f"materias_que_la_piden: {self.materias_que_la_piden}")