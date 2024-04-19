from .class_Plan_de_estudio import Plan_de_estudio
from .class_Materia import Materia

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