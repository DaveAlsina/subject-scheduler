import matplotlib.pyplot as plt
import pandas as pd
import networkx as nx

from datetime import datetime
import pprint
pp = pprint.PrettyPrinter(depth=3, width=100, indent=2, compact=True)



def delete_seen_subjects(graph: nx.Graph):

    """
        Recibe el grafo de la malla de las materias que se desean completar
        y elimina del grafo los nodos que corresponden a materias vistas

        return: grafo con las materias por ver y sus dependencias
    """


    # lee las materias vistas y las transforma en un dataframe
    seen_subjects = pd.read_csv("./data/completed_lectures.csv")
    seen_subjects.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    # crea una lista con los strings de las materias vistas
    seen_subjects_strip = [ lecture for lecture in list(seen_subjects["completed lecture"]) ]
    
    # busca las materias completamente vistas
    # (esto lo hice principalmente para el tema de los 11 creds de electivas generales y 6 de HM)
    # no trate estos casos en específico por aparte porque no se sentía generales
    # el código si hacía eso, por esa razón hago esta parte del código para todas las materias vistas
    # aunque en nuestro contexto no sea necesario

    completed_lecs = []

    for lecture in seen_subjects_strip:

        curr_lect = seen_subjects[ seen_subjects["completed lecture"] == lecture]

        # si se han visto todos los creditos que se deberían entonces es una materia vista
        if graph.nodes[lecture]["creds"] == int(curr_lect["creds"]):
            completed_lecs.append(lecture)

        # si aún le faltan actualice en el grafo cuántos le faltan
        else:
            graph.nodes[lecture]["creds"] = graph.nodes[lecture]["creds"] - int(curr_lect["creds"])


    graph.remove_nodes_from(completed_lecs)
    #print("número de materias completadas: ", len(completed_lecs))

    return graph


def csv_to_graph():

    """
        Lee el csv de la malla de la carrera y lo vuelve un grafo dirigido
        donde las dependencias son aristas de la forma (materia_que_es_prerreq, materia_que_tiene_prerreq)
        y donde cada nodo almacena información como si hay correquisitos (*codep*),
        la periodicidad con  que se dicta la materia (*freq*), 
        y el semestre en que comienza a dictarse dicha materia (*start*)
    """

    # lee la malla completa y la transforma en un dataframe
    subjects_grid = pd.read_csv("./data/malla_completa.csv")

    # quita los espacios a los lados de todos los strings
    subjects_grid.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    # toma las electivas de profundización que el usuario desea tomar

    print("¿Qué ramas de profundización desea estudiar? ")
    print(" 1. Inteligencia Artificial\n 2. Ciencia de Datos\n 3. Ciber-Seguridad\n 4. Actuaría\n -1. Omitir")
    selection = input("Su selección (escriba numeros separados por comas): ")
    selection = selection.split(',')
    selection = [int(option) for option in selection]

    print("\nCargando archivos ...")


    # diccionario con los nombres de los archivos y su correspondiente seleccion de usuario
    files = {1: './data/inteligencia_artificial.csv', 2: './data/ciencia_de_datos.csv',
             3: './data/ciber_seguridad.csv', 4: './data/actuaria.csv'}



    # si no se omitio entonces agregue los datos necesarios
    if -1 not in selection: 

        for i in selection:
            print(files[i])

        for profundization_line in selection:

            data = pd.read_csv(files[profundization_line])
            data.applymap(lambda x: x.strip() if isinstance(x, str) else x)

            subjects_grid = pd.concat([subjects_grid, data])

    else:
        print("Se omitieron las electivas")

    # toma la columna de nombres de materias y las transforma en una lista
    subjects_names = list(subjects_grid["lecture"].values) 
    
    # crea el grafo 
    G = nx.DiGraph()


    # revisa si todas las columnas que deberían tener información, tienen esa información
    if subjects_grid[ ["lecture", "frequency", "starting semester"] ].isnull().values.any():
        raise Exception("Hay un error en el csv, alguna materia no tiene la información necesaria")
    

    # añade las materias al grafo junto con sus dependencias 
    for idx, row in subjects_grid.iterrows():
        
        subj = row["lecture"].strip()
        freq = row["frequency"]
        start = row["starting semester"]
        creds = row["creds"]

        
        # añade la materia al grafo
        G.add_node(subj, freq = freq, start = start, creds = creds, codep = "")                    

        # toma las dependencias de esa materia y las separa
        subj_dependencies = str(row["dependency"]).split(';')            
        subj_codependecies = str(row["special dependency"]).split(';')

        for subj_dep, subj_codep in zip(subj_dependencies, subj_codependecies):


             # añade la arista al grafo en caso de que esta no tenga 'nan' como dependencia
            if subj_dep != 'nan':
                G.add_edge(subj_dep.strip(), subj)

            # añade la codependencia al grafo como un atributo del nodo
            if subj_codep != 'nan':
                G.nodes[subj]["codep"] = subj_codep

    return G


def save_solution_as_csv(solutions: list):

    """
        Recibe la lista de soluciones de la forma:

        [
            (
                ( (str, ..., str), (int, int) ),
                ( (str, ..., str), (int, int) ),
                ( (str, ..., str), (int, int) ),
            )

            , ... ,

            (
                ( (str, ..., str), (int, int) ),
                ( (str, ..., str), (int, int) ),
                ( (str, ..., str), (int, int) ),
            ),

        ]

        Y la transforma en dataframe para guardarlo como csv,
        el dataframe es de la forma: 

            +--------------------------------------------------------------------------------+
            +    sem_1    + creds_gen_sem_1 +   creds_hm_sem_1 +  ...  +    sem_n    +  ...  +
            + str;...;str +       int       +        int       +  ...  + str;...;str +  ...  +
            +     ...     +       ...       +        ...       +  ...  +     ...     +  ...  +
            +--------------------------------------------------------------------------------+

    """

    # obtiene el número máximo de semestres que contempla una solución
    number_of_semesters = 0
    
    for complete_solutions in solutions:

        if number_of_semesters < len(complete_solutions):
            number_of_semesters = len(complete_solutions)

    # titulos de las columnas de los dataframes
    titles = []

    for i in range(1, number_of_semesters + 1):

        titles.append( "sem_"           + str(i))
        titles.append( "creds_gen_sem_" + str(i))   
        titles.append( "creds_hm_sem_"  + str(i))

    data = pd.DataFrame(columns = titles)
    

    # contador de la fila en la que se está
    count = 0

    for solution in solutions:
        
        row = []

        for semester in solution:

            
            row.append( ";".join(semester[0]) )
            row.append( str(semester[1][0]) ) 
            row.append( str(semester[1][1]) ) 

        # si esta solucion tiene menos semestres que los de la solución máxima 
        # rellene las columnas faltantes con '-'
        # (recuerde que por cada semestre hay 3 columnas)

        if len(row) < number_of_semesters:
            [ row.append('-') for i in range( (number_of_semesters - len(row))*3 ) ] 


        data.loc[count] = row
        count += 1

    
    dateTimeObj = datetime.now()
    filename = dateTimeObj.strftime("%d_%b_%Y_%Hh_%Mmin")
    filename = './solutions/' + filename + '.csv'

    data.to_csv(filename, sep=',', index = False, encoding = 'UTF-8')
    
    return 


def take_usr_input():
    
    """
        Función para tomar input del usuario
    """

    print('*'*50)
    print("Ingrese numeros enteros mayores o iguales a 1")
    print('*'*50)


    # obtiene el numero minimo y maximo de materias que se van a meter 
    # en un semestre
    min_subjects = int(input("Ingrese el número mínimo de materias que quiere ver en un semestre: "))
    max_subjects = int(input("Ingrese el número máximo de materias que quiere ver en un semestre: "))
    
    subjects = (min_subjects, max_subjects)
    print("-"*50)

    # obtiene el numero minimo y maximo de creditos que se van a meter 
    # en un semestre
    min_creds = int(input("Ingrese el número mínimo de créditos que quiere tomar en un semestre: "))
    max_creds = int(input("Ingrese el número máximo de créditos que quiere tomar en un semestre: "))

    creds_semester = (min_creds, max_creds)
    print("-"*50)

    # obtiene el numero minimo y maximo de creditos de electiva general que se van a meter 
    # en un semestre
    min_creds_gen = int(input("Ingrese el número mínimo de créditos de *electiva general* que quiere tomar en un semestre: "))
    max_creds_gen = int(input("Ingrese el número máximo de créditos de *electiva general* que quiere tomar en un semestre: "))
    
    creds_elec = (min_creds_gen, max_creds_gen)
    print("-"*50)

    # obtiene el numero minimo y maximo de creditos de electiva HM que se van a meter 
    # en un semestre
    min_creds_hm = int(input("Ingrese el número mínimo de créditos de *electiva HM* que quiere tomar en un semestre: "))
    max_creds_hm = int(input("Ingrese el número máximo de créditos de *electiva HM* que quiere tomar en un semestre: "))
    
    creds_hm = (min_creds_hm, max_creds_hm)
    print("-"*50)

    return subjects, creds_semester, creds_hm, creds_elec



##############################
#          CHECKERS    
##############################


def draw_graph(graph):

    """
        Función para dibujar el grafo dado con un layout basado en simulación 
        de resortes
    """

    nx.draw_spring(graph, with_labels = True, font_weight = 'bold')
    plt.show()



def check_graph_attrs(graph):

    """
    Función para revisar cuales son los atributos de los nodos del grafo
    """

    for node in graph.nodes():
        pp.pprint([ node, list( graph.nodes[node].items()) ])
        print("-"*50)




















