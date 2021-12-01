import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt


def csv_to_graph():

    """

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
        G.add_node(subj, freq = freq, start = start)                    

        # toma las dependencias de esa materia y las separa
        subj_dependencies = str(row["dependency"]).split(';')            

        for subj_dep in subj_dependencies:

             # añade la arista al grafo en caso de que esta no tenga 'nan' como dependencia
            if subj_dep == 'nan':
                continue 

            G.add_edge(subj_dep.strip(), subj)

    
    return G



def draw_graph(graph):

    nx.draw_spring(graph, with_labels = True, font_weight = 'bold')
    #pos = nx.planar_layout(graph)
    plt.show()



draw_graph( csv_to_graph() ) 







