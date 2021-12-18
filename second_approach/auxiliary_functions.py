import matplotlib.pyplot as plt
import pandas as pd
import networkx as nx


import pprint
pp = pprint.PrettyPrinter(depth=3, width=50, indent=2, compact=True)


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




















