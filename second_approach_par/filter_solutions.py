import pandas as pd
from os import listdir 


class set_wraper:

    def __init__(self, subjects: str):

        self.subjects_in_semester = None

        if ';' in subjects:
            self.subjects_in_semester = set(subjects.split(";"))


    def contains(values: set):
        return self.subjects_in_semester.issuperset(values)







def load_sotutions_file():

    # busca los archivos csv que están en la carpeta de soluciones 
    all_files = listdir("./solutions") 
    csv_file  = [f for f in all_files if f.endswith('.csv')]

    # selecciona el archivo que contiene la información que se desea analizar
    print("Seleccione el archivo: ")
    count = 0

    for f in csv_file:
        print(str(count) + ". " + f)
        count += 1

    opt  = int(input("Escriba el número de la opción: "))
    print('Cargando: ', csv_file[opt], '...\n')

    # carga la solución 
    data = pd.read_csv("./solutions/" + csv_file[opt])
    
    # obtiene los indices de la lista de nombres de columnas
    # que corresponden a las columnas de nombre 'sem_i'
    idx = [i*3 for i in range( int(len(data.columns.values)/3) ) ]

    # para poder guardar las materias seradas por punto y comas
    # 'str;str;str;...;str' no se podían usar listas por lo que tocó crear un 
    # nuevo objeto que guarda un set (para búsqueda más rápida)

    # las columnas de 'sem_i' las cambia por objetos del tipo 
    # 'set_wraper'
    data[ data.columns.values[idx]  ]  =  data[ data.columns.values[idx] ].applymap(lambda x: set_wraper(x) )
    





load_sotutions_file()










