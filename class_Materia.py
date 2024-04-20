from pickle import dump, load

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
            with open(f"plan_de_estudio_{self.get_carrera()}","rb") as f:
                self.materias = load(f)
            del f
        except: print("| no se encuentra el plan de estudio de esta carrera")

class Alumno():
    def __init__(self,carrera):
        self.plan_de_estudio = Plan_de_estudio(carrera)
        self.plan_de_estudio.importar_materias()
        self.cantidad_de_materias = len(self.plan_de_estudio.get_materias())
        self.aprobadas = []
        self.materias_desbloqueadas = []
    # realizamos una busqueda binaria del codigo de la materia
    def buscar_materia(self,codigo):
        lista = self.plan_de_estudio.get_materias()
        primero = 0
        ultimo = len(lista)-1

        while primero <= ultimo:
            puntoMedio = (primero + ultimo)//2
            medio_de_la_lista = lista[puntoMedio].get_codigo()

            if medio_de_la_lista == codigo:
                # print(f"la materia encontrada es\n{lista[puntoMedio]}")
                return lista[puntoMedio]
            elif codigo < medio_de_la_lista:
                ultimo = puntoMedio-1
            elif codigo > medio_de_la_lista:
                primero = puntoMedio+1
        return f"no se encuentra la materia {codigo}"

    ## getters
    def get_aprobadas(self):
        return self.aprobadas
    def get_materias_desbloqueadas(self):
        return self.materias_desbloqueadas
    def get_plan_de_estudio(self):
        for i in self.plan_de_estudio:
            print(i)
    def get_porcentaje_cursado(self):
        print(f"llevas {(len(self.aprobadas)*100/self.cantidad_de_materias):.2f}% de materias aprobadas en toda la carrera")

    ## setters
    def set_materias_sin_correlativas(self):
        for i in self.plan_de_estudio.get_materias_sin_correlativas():
            if i not in self.aprobadas: self.materias_desbloqueadas.append(i)

    def set_materias_desbloqueadas(self):
        codigos_aprobadas = set()
        for i in self.aprobadas: codigos_aprobadas.add(i.get_codigo())
        
        materias_desbloqueadas = []
        for aprobada in self.aprobadas:
            for codigo in aprobada.get_materias_que_la_piden():
                if codigo[1] in codigos_aprobadas: continue

                materia_temp = self.buscar_materia(codigo[1])

                desbloqueada = codigos_aprobadas.issuperset(set(materia_temp.get_correlativas()))
                agregar = materia_temp not in materias_desbloqueadas

                if desbloqueada and agregar:
                    materias_desbloqueadas.append(materia_temp)

        self.materias_desbloqueadas = materias_desbloqueadas
        self.set_materias_sin_correlativas()

    def set_materias_aprobas(self,lista):
        for aprobada in lista:
            materia = self.buscar_materia(aprobada)

            if f"no se encuentra la materia {aprobada}" == materia: continue
            self.aprobadas.append(materia)
        self.set_materias_desbloqueadas()