from class_Materias import Materia
from Bexport_Bimport import Export

##           codigo,asignatura,regimen,horas_semanales,correlativas,año

##primer año
m1 = Materia(1,"Tecnología y Sociedad","Cuatrimestral",4,[],1)
m2 = Materia(2,"Inglés I","Cuatrimestral",4,[],1)
m3 = Materia(3,"Principios de Economía","Cuatrimestral",4,[],1)
m4 = Materia(4,"Comunicación Institucional","Cuatrimestral",4,[],1)
m5 = Materia(5,"Internet: Infraestructura y redes","Cuatrimestral",4,[],1)
m6 = Materia(6,"Semántica de las interfaces","Cuatrimestral",4,[],1)
m7 = Materia(7,"Introducción al comercio electrónico","Cuatrimestral",4,[],1)
m8 = Materia(8,"Usabilidad, seguridad y Estándares Web","Cuatrimestral",4,[5],1)
m9 = Materia(9,"Inglés II","Cuatrimestral",4,[2],1)

##segundo año

m10 = Materia(10,"Investigación de mercado","Cuatrimestral",4,[3,7],2)
m11 = Materia(11,"Marco legal de negocios electrónicos","Cuatrimestral",4,[7],2)
m12 = Materia(12,"Gestión del conocimiento","Cuatrimestral",4,[1],2)
m13 = Materia(13,"Desarrollo Web","Cuatrimestral",4,[6,8],2)
m14 = Materia(14,"Formulación, incubación y evaluación de proyectos","Cuatrimestral",4,[3],2)
m15 = Materia(15,"Métricas del mundo digital","Cuatrimestral",4,[],2)
m16 = Materia(16,"Desarrollo de Productos y Servicios","Cuatrimestral",4,[10],2)
m17 = Materia(17,"Taller de Comunicación","Cuatrimestral",4,[4],2)
m18 = Materia(18,"Desarrollos para Dispositivos móviles","Cuatrimestral",4,[13],2)

##tercer año

m19 = Materia(19,"Calidad y Servicio al Cliente","Cuatrimestral",4,[16],3)
m20 = Materia(20,"Marketing digital","Cuatrimestral",4,[17],3)
m21 = Materia(21,"Taller de Práctica Integradora","Cuatrimestral",4,[16,17],3)
m22 = Materia(22,"Competencias emprendedoras","Cuatrimestral",4,[14],3)
m23 = Materia(23,"Gestión de Proyectos","Cuatrimestral",4,[7,14],3)

materias = [m1,m2,m3,m4,m5,m6,m7,m8,m9,
            m10,m11,m12,m13,m14,m15,m16,m17,m18,
            m19,m20,m21,m22,m23]

Export(materias,"COMERCIO_ELECTRONICO")