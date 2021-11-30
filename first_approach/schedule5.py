from numpy import arange
import cProfile, pstats, io
import pandas as pd
import networkx as nx
from matplotlib import pyplot as plt
from itertools import combinations, permutations
import assignment_plan

import sys

 # the setrecursionlimit function is
 # used to modify the default recursion
 # limit set by python. Using this,
 # we can increase the recursion limit
 # to satisfy our needs

sys.setrecursionlimit(10**6)


def filter_by_prereq(completed_lects, lectures_graph, test=False):

    """
        Input: completed_lects -> lista de las materias completadas
                lectures_graph -> grafo de los prerrequisitos inmediatamente anteriores
                de cada materia electiva

        Output: lista de materias que se pueden inscribir basado en los prerrequisitos
    """

    #obtiene las materias del grafo de dependencias
    lectures = list(lectures_graph.nodes())

    #obtiene los nodos para los que no hay prerrequisito
    #es decir los nodos iniciales (prerrequisitos que hay que desbloquear primero que nada)

    init_prereqs= [node for node in lectures if lectures_graph.in_degree(node) == 0]
    # print("prerrequisitos básicos para todas las electivas: ", init_prereqs)

    #materias de electivas de profundización que no han sido vistas
    main_lectures = [node for node in lectures if (node not in init_prereqs) and (node not in completed_lects)]

    #si una materia tiene todos sus prerrequisitos en la lista de completados
    #enconces añadalo a las materias inscribibles

    elegible_lectures = []                          #materias inscribibles

    for lecture in main_lectures:

        prereqs = list(lectures_graph.predecessors(lecture))
        elegible = True

        for prereq in prereqs:
            if prereq not in completed_lects:
                elegible = False
                break

        if elegible:
            elegible_lectures.append(lecture)

    if test: print("Materias elegibles basado en las materias completadas:", elegible_lectures)

    return elegible_lectures


def time_line_for_subject(lectures_info, n_semesters):

    """
        Input: lectures_info -> dataframe con toda la información relativa a las materias y sus tiempos
                n_semesters -> número de semestres que se tienen disponibles para ver las electivas de profundización

        Output: diccionario con los nombres de las materias como llaves y como valores respectivos la lista de tiempos en que
                se pueden ver las materias
    """

    subjects_timeline = {}
    localtimeline = 0

    #para cada materia
    for subject in lectures_info["lecture"].values:

        #obtiene la fecha de inicio de la materia en la próxima vez que se vaya a dictar clases de esta
        starting_date = lectures_info[ lectures_info["lecture"] == subject]["starting semester"].values[0]

        #si la frecuencia de la materia es 1 (semestral)
        if lectures_info[ lectures_info["lecture"] == subject]["frequency"].values[0] == 1:

            # escribe la linea de tiempo en que se pueden ir metiendo las materias
            localtimeline = arange(starting_date, 0.5*n_semesters + starting_date, 0.5)

        #en caso de ser anual
        else:

            localtimeline = arange(starting_date, 0.5*n_semesters + starting_date, 1)

        subjects_timeline[subject] = localtimeline.tolist()

    return subjects_timeline



def filter_by_date(curr_date, elegible_lectures, lectures_timeline):

    """
        Input: curr_date ->  fecha actual en la simulación
                elegible_lectures -> lista de materias que se pueden inscribir
                lectures_timeline -> diccionario con la linea de tiempo de las fechas posibles para ver cada una de las materias

        Output: elegible_lectures2 -> lista de materias elegibles en función del tiempo en que se dictan
    """
    elegible_lectures2 = []

    for lecture in elegible_lectures:

        if curr_date in lectures_timeline[lecture]:
            elegible_lectures2.append(lecture)

    return elegible_lectures2


def get_combinations(lecturesPerSem, elegible_lectures, test=False):

    """
        Input: elegible_lectures -> lista de materias elegibles a cursar (que cumplen las restricciones)
                lecturesPerSem  -> lista de cantidad de materias a cursar en el semestre (electivas de profundización)

        Output: lista de todas las combinaciones posibles de materias elegibles a inscribir
                en función de la cantidad de materias que se deban inscribir según lo que indica el semestre

                materias_elegibles COMBINADO cantidad_de_materias_a_inscribir
    """

    posib = []  #lista con las tuplas de las posibilidades a inscribir

    #si la cantidad de materias a elegir es mayor o igual a las que se deben elegir use
    #el método de hacer combinatiorias

    if len(elegible_lectures) >= lecturesPerSem:
        posib = list(combinations(elegible_lectures, lecturesPerSem))

    #en los casos en que hay más materias para meter en el semestre
    #que las que se pueden, ajusta la combinatoria a las condiciones
    else:
        posib = list(combinations(elegible_lectures, len(elegible_lectures)))

    if test: print("Combinaciones posibles dado que se deben inscribir", lecturesPerSem , " materias ", posib)

    return posib




def recursion(viewed_lects, dependency_graph, inscription_plan,  time_line, lectures_timeline, valid_solutions):

    #revisa si aún quedan materias por ver en el plan de inscripción
    #en caso de que no acaba el algoritmo
    if (len(inscription_plan) == 0) or (len(time_line) == 0):
        return


    #obtine las materias disponibles para inscribirse
    elegible_lectures = filter_by_prereq(viewed_lects, dependency_graph)
    #print(elegible_lectures)

    elegible_lectures = filter_by_date(time_line.pop(0), elegible_lectures, lectures_timeline)
    #print(elegible_lectures)

    #obtiene la lista de combinaciones de materias a inscribir en el semestre
    combinations = get_combinations( inscription_plan.pop(0), elegible_lectures)

    for combination in combinations:

        #hace una copia de las materias vistas para enviarla a recursiones futuras
        viewed_lects_copy = viewed_lects.copy()

        #añade las materias de la combinación a las materias vistas
        for subject in combination:
            viewed_lects_copy.append(subject)

        #en caso de que se hayan inscrito todas las materias del grafo de dependencia
        #esto dice que se solucionó el problema, y se guarda la solución
        ok = True

        for required_lect in list(dependency_graph.nodes()):

            if required_lect not in viewed_lects_copy:
                ok = False
                break

        if (ok):

            valid_solutions.append( viewed_lects_copy )
            #print(viewed_lects_copy)
            continue


        #print(viewed_lects_copy)
        #vuelve a realizar el proceso de recursion para ver si esta combinación soluciona el problema
        recursion(viewed_lects_copy.copy(), dependency_graph, inscription_plan.copy(), time_line.copy(), lectures_timeline, valid_solutions)

    return


def ask_for_input():

    """
        Función que toma todas las entradas de usuario necesarias para correr el programa
    """

    curr_yr = float(input("ingrese el año actual con su semestre de la siguiente forma: [ej: 2021.5 para 2do semestre de 2021 o 2021 para 2021 semestre 1]: "))
    n_semesters = int(input("ingrese la cantidad de semestres disponibles para ver la cantidad de materias de profundización dadas: "))
    max_subjects = int(input("ingrese la cantidad de materias electivas de profundización máximas que va a meter en cada semestre: "))
    print()

    #linea de tiempo desde que se empiezan a inscribir materias electivas de profundización hasta el final de los tiempos :v
    time_line = arange(curr_yr, (0.5 * n_semesters) + curr_yr, 0.5).tolist()

    return time_line, n_semesters, max_subjects

def profile(fnc):

    """A decorator that uses cProfile to profile a function"""

    def inner(*args, **kwargs):

        pr = cProfile.Profile()
        pr.enable()
        retval = fnc(*args, **kwargs)
        pr.disable()
        s = io.StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())
        return retval

    return inner

def test():

    """
        Función donde se testea la correctitud de las funciones base de la función recursion
        que es la función principal
    """

    lecturesPerSemesters = [1, 1, 3, 2, 2]

    options = filter_by_prereq( list(H.nodes()), G , test=True)
    get_combinations(lecturesPerSemesters[0], options, test=True)


@profile
def a():

    #materias a cursar junto con sus dependencias y otros datos adicionales
    lectures = pd.read_csv("./Libro1.csv")

    #materias completadas
    completed_lect = pd.read_csv("./Libro2.csv")

    #matriz del prerrequisito y la materia que lo necesita
    matrix = lectures[["dependency", "lecture"]].values

    #generación del grafo a partir de la matriz de dependencias
    #de las materias
    G = nx.DiGraph()
    G.add_edges_from(matrix)

    H = nx.DiGraph()
    H.add_nodes_from(completed_lect["completed lecture"])


    #toma entrada del usuario
    time_line, n_semesters, max_subjects = ask_for_input()
    print("--"*30)
    print("la línea de tiempo desde que se empiezan a inscribir materias de profundización hasta que se termina: ")
    print(time_line)
    print()

#crea la linea de tiempo dentro de los límites estipulados para cada materia
    subjects_timeline = time_line_for_subject(lectures, n_semesters)
    print("--"*30)
    print("línea de tiempo para cada una de las materias particulares")
    print(subjects_timeline)
    print()

#obtiene el número de materias que no han sido vistas
    unseen_subjects = len([node for node in list(G.nodes()) if node not in list(H.nodes()) ])
    print("--"*30)
    print("número de materias por ver: ", unseen_subjects)
    print()


#creación de la lista con el número de electivas de profundización a inscribir en cada semestre
#deben meterse 9 materias en 5 semestres, a continuación se generarán todas las combinaciones
#que suman 9 en 5 intentos
    inscription_plan_solutions = []
    lecturesPerSemesters = assignment_plan.filter_combinations(unseen_subjects, inscription_plan_solutions, n_semesters, max_subjects)



#lista donde se guardan las soluciones válidas
    valid_solutions = []
    solutions_dict = {}

    for lecturesPerSemesters_option in lecturesPerSemesters:

        #obtiene las soluciones de la materias que se deben meter en cada semestre para lograr
        #verlas todas

        for permutation in list(permutations(lecturesPerSemesters_option)):

            if (permutation not in solutions_dict.keys()) and (permutation[0] == 1):

                #ejecuta la recursión pasando la lista de materias vistas, el grafo de dependencias, el plan de inscripciones,
                #un diccionario con las materias como llave y las fechas en que estas se dictan como valores, y una lista en la que se guardan todas las
                #soluciones válidas

                prev_len = len(valid_solutions)

                recursion( list(H.nodes()).copy(),  G, list(permutation).copy(), time_line.copy(), subjects_timeline, valid_solutions)
                new_solutions = valid_solutions[ prev_len: ]

                for solution in new_solutions:
                    solutions_dict[permutation] = new_solutions



    print()
    print("*"*30)
    print("Cantidad de soluciones")
    print("*"*30)
    print(solutions_dict.keys())
    print(solutions_dict[(1,1,2,2,3)])

#test()
    nx.draw_networkx(G, node_color="green")
    plt.show()



