import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import pprint

pp = pprint.PrettyPrinter(depth=3, width=50, indent=2, compact=True)


def csv_to_graph():

    """
        Lee el csv de la malla de la carrera y lo vuelve un grafo dirigido
        donde las dependencias son aristas de la forma (materia_que_es_prerreq, materia_que_tiene_prerreq)
        y donde cada nodo almacena información como si hay correquisitos (*codep*),
        la periodicidad con  que se dicta la materia (*freq*), 
        y el semestre en que comienza a dictarse dicha materia (*start*)
    """

    # lee la malla completa y la transforma en un dataframe
    subjects_grid = pd.read_csv("./malla_completa.csv")

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

        
        # añade la materia al grafo
        G.add_node(subj, freq = freq, start = start, codep = "")                    

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



def find_subjects_without_prerreqs(graph):

    """
        Encuentra las materias del grafor que no poseen prerrequisitos
    """

        return [ node for node in graph.nodes if graph.in_degree(node) == 0]



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



grafito = csv_to_graph()

draw_graph(grafito) 
check_graph_attrs(grafito)

print("materias sin prerrquisitos")
print(find_subjects_without_prerreqs(grafito))








