import os
from pickle import dump,load

## exportar un archivo binario
class Export():
    def __init__(self,materias: list,nombre_carrera):
        self.path = "bin_Carreras"

        try:
            with open(os.path.join(self.path, nombre_carrera),"wb") as file:
                dump(materias, file)

        except FileNotFoundError:
            print("ERROR: Directorio no encontrado.")
        except PermissionError:
            print("ERROR: Permiso denegado al archivo o directorio.")
        except Exception as e:
            print(f"ERROR: {e}")
    
    def set_path(self,new_path): self.path = new_path

## importar un archivo binario
class Import:
    def __init__(self,nombre_carrera: str):
        self.path = "bin_Carreras"
        self.load = []

        try:
            with open(os.path.join(self.path, nombre_carrera),"rb") as file: 
                self.load = load(file)

        except FileNotFoundError:
            print("ERROR: Directorio no encontrado.")
        except PermissionError:
            print("ERROR: Permiso denegado al archivo o directorio.")
        except Exception as e:
            print(f"ERROR: {e}")

    def set_path(self,new_path): self.path = new_path

    def get_load(self): return self.load


## Ejemplo
# Export(["hola",123,12,234,12],"mono")
# Import("mono").get_load()