from pickle import dump, load

class Plan_de_estudio():
    def __init__(self,carrera):
        self.carrera = carrera
        self.materias = []
    def __str__(self):
        return f"carrera {self.carrera} - materias {len(self.materias)}"

    ## getters
    def get_carrera(self):
        return self.carrera
    def get_materias(self):
        return self.materias
    def get_materia(self,indice):
        return self.materias[indice]
    def get_materias_sin_correlativas(self):
        try:
            default = []
            for i in self.materias:
                if i.get_correlativas() == []: default.append(i)
            return default
        except: print("error al obtener las materias sin correlativas")

    ## setters
    def set_materias(self,materias):
        for materia in materias:
            self.materias.append(materia)

    def calcular_importancias_y_materias(self):
        for materia in self.materias:
            for otra_materia in self.materias:
                if materia.get_codigo() == otra_materia.get_codigo(): continue

                if materia.get_codigo() in otra_materia.get_correlativas():
                    materia.set_materias_que_la_piden((otra_materia.get_año(),otra_materia.get_codigo()))
                    materia.set_importancia()

    ## serializar --  capaz deberia estar en otra clase para no mezclar capas
    def exportar_materias(self):
        self.calcular_importancias_y_materias()
        with open(f"plan_de_estudio_{self.get_carrera()}","wb") as f:
            dump(self.get_materias(),f)
        del f; print("completado")

    def importar_materias(self):
        try:
            with open(f"bPlan-estudio/plan_de_estudio_{self.get_carrera()}","rb") as f:
                self.materias = load(f)
            del f
        except: print("| no se encuentra el plan de estudio de esta carrera")