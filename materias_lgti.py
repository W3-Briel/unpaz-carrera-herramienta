from class_Materia import *

##           codigo,asignatura,regimen,horas_semanales,correlativas,año

# primer año
m1 = Materia(6001,"Análisis Matemático I","Cuatrimestral",4,[],1)
m2 = Materia(6002,"Arquitectura de Computadoras I","Cuatrimestral",4,[],1)
m3 = Materia(6003,"Introducción a la Programación","Cuatrimestral",4,[],1)
m4 = Materia(6004,"Estructuras Discretas","Cuatrimestral",4,[],1)
m5 = Materia(6005,"Ciencia, Tecnología y Sociedad","Cuatrimestral",4,[],1)
m6 = Materia(6006,"Análisis Matemático II","Cuatrimestral",4,[6001],1)
m7 = Materia(6007,"Álgebra y Geometría Analítica","Cuatrimestra",4,[6001],1)
m8 = Materia(6008,"Algoritmos y Programación","Cuatrimestral",4,[6003,6004],1)
m9 = Materia(6009,"Arquitectura de Computadoras II","Cuatrimestral",4,[6002,6005],1)
m10 = Materia(6010,"Inglés I","Cuatrimestral",4,[6005],1)
# segundo año
m11= Materia(6011,"Sistemas Operativos I","Cuatrimestral",4,[6002,6010],2)
m12= Materia(6012,"Economía General","Cuatrimestral",4,[6001],2)
m13= Materia(6013,"Inglés II","Cuatrimestral",4,[6010],2)
m14= Materia(6014,"Ingeniería de Software I","Cuatrimestral",4,[6003,6004,6005],2)
m15= Materia(6015,"Paradigmas de Programación","Cuatrimestral",4,[6003],2)
m16= Materia(6016,"Sistemas Operativos II","Cuatrimestral",4,[6011],2)
m17= Materia(6017,"Laboratorio de Programación y Lenguajes","Cuatrimestral",4,[6015],2)
m18= Materia(6018,"Programación Orientada a Objetos","Cuatrimestral",4,[6008],2)
m19= Materia(6019,"Base de Datos I","Cuatrimestral",4,[6004,6007],2)
m20= Materia(6020,"Administración I","Cuatrimestral",4,[],2)
# tercer año
m21 = Materia(6021,"Probabilidad y Estadísticas","Cuatrimestral",4,[6006,6007],3)
m22 = Materia(6022,"Comunicaciones y Redes","Cuatrimestral",6,[6004,6011],3)
m23 = Materia(6023,"Ingeniería de Software II","Cuatrimestral",6,[6014],3)
m24 = Materia(6024,"Administración II","Cuatrimestral",4,[6020],3)
m25 = Materia(6025,"Laboratorio de Software","Cuatrimestral",4,[6014,6018,6019],3)
m26 = Materia(6026,"Base de Datos II","Cuatrimestral",4,[6019],3)
m27 = Materia(6027,"Contabilidad I","Cuatrimestral",6,[6020],3)
m28 = Materia(6028,"Trabajo de Campo","Cuatrimestral",6,[6018,6022,6023],3)
# cuarto año
m29 = Materia(6029,"Investigación Operativa","Cuatrimestral",4,[6021],4)
m30 = Materia(6030,"Arquitectura Web","Cuatrimestral",4,[6022],4)
m31 = Materia(6031,"Seguridad Informática","Cuatrimestral",4,[6017,6018,6022,6023],4)
m32 = Materia(6032,"Administración de Recursos Humanos","Cuatrimestral",4,[6020,6024],4)
m33 = Materia(6033,"Contabilidad Avanzada","Cuatrimestral",6,[6027],4)
m34 = Materia(6034,"Sistemas Inteligentes","Cuatrimestral",4,[6021,6023],4)
m35 = Materia(6035,"Gestión de la Tecnología","Cuatrimestral",4,[6022,6023],4)
m36 = Materia(6036,"Comercialización","Cuatrimestral",6,[6020,6024],4)
m37 = Materia(6037,"Planificación Financiera y Proyecto de Inversión","Cuatrimestral",6,[6006,6012,6020,6027],4)
m38 = Materia(6038,"Optativa I","Cuatrimestral",4,[],4)
# quinto año
m39 = Materia(6039,"Gestión de Proyectos","Cuatrimestral",4,[6012,6021,6023,6029],5)
m40 = Materia(6040,"Inteligencia de los Negocios","Cuatrimestral",4,[6023,6025,6026],5)
m41 = Materia(6041,"Optativa II","Cuatrimestral",4,[],5)
m42 = Materia(6042,"Dirección Estratégica","Cuatrimestral",4,[6036],5)
m43 = Materia(6043,"Trabajo Final de Grado","Cuatrimestral",6,[],5)

# LGTI_MATERIAS= [m1,m2,m3,m4,m5,m6,m7,m8,m9,m10,
#                 m11,m12,m13,m14,m15,m16,m17,m18,m19,m20,
#                 m21,m22,m23,m24,m25,m26,m27,m28,
#                 m29,m30,m31,m32,m33,m34,m35,m36,m37,m38,
#                 m39,m40,m41,m42,m43
#                 ]

# lgti = Plan_de_estudio("LGTI")

# lgti.set_materias(LGTI_MATERIAS)
# lgti.exportar_materias()