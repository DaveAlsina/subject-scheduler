from itertools import combinations
from copy import deepcopy

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

from sys import stdout
from time import time
from datetime import datetime


from auxiliary_functions import *


def find_solutions(graph: nx.Graph, num_subjects = (4, 10), creds_semester = (15,19), 
                   creds_hm = (1, 4), creds_elec = (2,3), verbose = False):

    """
        Wrapper para la función recursiva find_solutions_backtracking


        num_subjects    -> (mínimo de materias a inscribir en un semestre, máximo de materias a inscribir en un semestre)
        creds_semester  -> (minimo de créditos inscribible en un semestre, máximo de créditos inscribible en un semestre)
        creds_hm        -> (mínimo de créditos hm en un semestre, máximo de créditos hm en un semestre)
        creds_elec      -> (mínimo de créditos electiva general en semestre, máximo de créditos electiva general en semestre)
       
    """
    
    # obtiene el grafo con las materias que faltan por ver dentro de la malla académica
    graph = delete_seen_subjects(graph)

    #draw_graph(graph)
    
    # lee la malla completa y la transforma en un dataframe
    subjects_grid = pd.read_csv("./data/malla_completa.csv")
    
    # quita los espacios en blanco de los extremos de los strings
    subjects_grid.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    # busca una solución por backtracking
    solutions = find_solutions_bruteforce(graph, subjects_grid, num_subjects, creds_semester, creds_hm, creds_elec, verbose)

    save_solution_as_csv(solutions)


def find_solutions_bruteforce(graph: nx.Graph, subjects_grid: pd.DataFrame, num_subjects: tuple,
                              creds_semester:tuple, creds_hm:tuple, creds_elec: tuple, verbose = False):

    """
        
    """

    # obtiene las materias que se pueden ver 
    elegible_lectures = [lecture for lecture, indegree in graph.in_degree if indegree == 0]

    # obtiene una lista de soluciones validas
    valid_combinations = generate_valid_combinatorics(elegible_lectures, graph, num_subjects,
                                                      creds_semester, creds_hm, creds_elec, verbose)


    """
        Hay que hacer un loop en paralelo que se encargue de hacer la parte recursiva
        en 4 batches o tantas como el número de hilos del computador.

        Usar un set para ver si hay repeticiones de combinaciones de malla
        hay que ordenar alfabeticamente cada lista de combinaciones de la malla
    """

    solutions = set()
    ncombinations = int(len(valid_combinations))
    durations = []
    count = 0

    tic = 0.0
    toc = 0.0 
    total_duration = 0.0

    for combination in valid_combinations:

        # tiempo que duraria la ejecucion si todo durara lo mismo 
        # el '+ 0.00000001' es para evitar problemas por división entre cero
        mean = total_duration*ncombinations/(count + 0.00000001)

        # tiempo que falta para acabar asumiendo lo de arriba
        # (actualiza el tiempo faltante cada 4 iteraciones para que se vea mejor en la interfaz, 
        # sin tanta variación)
        if count % 4 == 0:
            remaining_time = mean - total_duration

        msg = "Progreso: %.3f%% | %d/%d, soluciones: %d, tiempo faltante: %.1f segs"

        if verbose:
            stdout.write('\n')
        else:
            stdout.write('\r')

        stdout.write(msg % ((count*100/ncombinations) , count, ncombinations, int(len(solutions)), remaining_time ) )
        stdout.flush()


        if verbose:
            print("iteración", count)


        tic = time()
        
        solution = recursive_trial( deepcopy(graph), combination, num_subjects, creds_semester, creds_hm, creds_elec, verbose)
        
        # si tiene una solución 
        # 1. Pongala en el orden correcto (desde lo que se inscribió primero hacia lo que se inscribió final)
        # 2. Las materias que se meten en cada semestre ordenelas alfabeticamente
        # (todo esto lo hago porque no se como hace el hashing la estructura de datos de set, 
        # por lo que trato de dejar todo uniforme para evitar que hayan soluciones iguales en el set pero 
        # con un orden distinto, y que no fueran consideradas como iguales por el hashing)

        if len(solution) != 0:

            fixed_solution = []

            # Pone reversa la tupla para que quede en el orden correcto 
            # ( desde lo primero en inscribir hasta lo último ) 
            for semester, creds in solution[::-1]:

                semester = list(semester)
                semester.sort()
                
                fixed_solution.append( (tuple(semester), creds) )


            solutions.add(tuple(fixed_solution))

        toc = time()
        total_duration += (toc - tic)

        count += 1

        if verbose:
            print("-"*10)


    if verbose:
        print(solutions)
        print(len(solutions))
    
    return solutions 

    




def generate_valid_combinatorics(subjects: list, graph: nx.Graph, num_subjects: tuple,
                                 creds_semester:tuple, creds_hm:tuple, creds_elec:tuple, verbose = False):

    """
        Dada una lista de materias validas a inscribir (subjects) se encarga de generar una lista de combinaciones 
        que cumplen con el requisito de que su suma de créditos está entre el mínimo de creditos (mincreds)
        y el máximo de creditos (maxcreds).

        retorna: 

                valid_combinations -> una lista de tuplas de la forma: 

                [
                    ( (combinacion), (numero_creditos_elec_gen, numero_creditos_elec_hm) ) 
                    ...
                    ( (combinacion), (numero_creditos_elec_gen, numero_creditos_elec_hm) ) 
                ]

                Donde *combinacion* es una tupla de strings que representan las materias a meter en ese semestre.
                En otras palabras retorna una lista de combinaciones de materias a inscribir.

    """

    # lista de combinaciones válidas
    valid_combinations = []

    # empieza a hacer todas las combinaciones posibles de la lista de materias 
    # elegibles

    for i in range(num_subjects[0], num_subjects[1] + 1):

        for combination in list( combinations(subjects, i) ):
            
            # dado que las electivas generales y las electivas HM 
            # son de un número de créditos variables dependiendo de que materia se escoge
            # la idea es añadir varias combinacines de la forma:

            # [
            #   ( (combinacion), (numero_creditos_elec_gen, numero_creditos_elec_hm) ) 
            #   ...
            #   ( (combinacion), (numero_creditos_elec_gen, numero_creditos_elec_hm) ) 
            # ]

            combinations_of_combination = []    # lista para guardar las combinaciones que salen de la combinación Dada
                                                # estas combinaciones surgen de asumir distintos valores para los créditos 
                                                # que se toman de elec generales o hm

            # lista de tuplas de la forma: (numero_creditos_elec_gen, numero_creditos_elec_hm)
            combs_creds = []

            if ('Electiva general' in combination) and ('Electiva HM' in combination): 
                
                available_creds_gen = graph["Electiva general"]["creds"]
                available_creds_hm = graph["Electiva HM"]["creds"]

                if (available_creds_gen < creds_elec[0]) or (available_creds_hm < creds_hm[0]):
                    continue

                # puede que hallan menos creditos disponibles que el máximo que se puede inscribir
                # o puede que hallan más creditos disponibles que los que se desean inscribir en un semestre
                # por lo que se debe escoger como cota superior el mínimo entre ambas

                maxval_gen = min(available_creds_gen, creds_elec[1])
                maxval_hm = min(available_creds_hm, creds_hm[1])

                
                for i in range(creds_elec[0], maxval_gen + 1):
                    for j in range(creds_hm[0], maxval_hm + 1):

                        combs_creds.append( (i, j) )

            # caso en el que solo hay como opción el meter electiva general
            elif ('Electiva general' in combination):

                available_creds_gen = graph.nodes["Electiva general"]["creds"]
                maxval_gen = min(available_creds_gen, creds_elec[1])

                if (available_creds_gen < creds_elec[0]):
                    continue

                for i in range(creds_elec[0], maxval_gen + 1):
                    combs_creds.append( (i, 0) )


            # caso en el que solo hay como opción el meter electiva hm
            elif ('Electiva HM' in combination):

                print(graph.nodes(data=True))
                available_creds_hm = graph.nodes["Electiva HM"]["creds"]
                maxval_hm = min(available_creds_hm, creds_hm[1])

                if (available_creds_hm < creds_hm[0]):
                    continue

                for j in range(creds_hm[0], maxval_hm + 1):
                    combs_creds.append( (0, j) )



            # creditos que vienen de meter todas las materias de la combinación 
            # excepto por la electiva general y la hm 
            num_creds = 0

            for lecture in combination:
                if lecture not in ['Electiva general', 'Electiva HM']:
                    num_creds += graph.nodes[lecture]["creds"]
    

            # en caso de que si hayan combinaciones de electivas
            if len(combs_creds) != 0:
                for cred_combination in combs_creds:

                    value = num_creds + sum(cred_combination)
                
                    if (value >= creds_semester[0]) and ( value <= creds_semester[1]):
                        valid_combinations.append( ( (combination), cred_combination ) )

            # en caso de que no se tenga en cuenta electivas en esta combinacion en particular
            elif ( num_creds >= creds_semester[0]) and ( num_creds <= creds_semester[1] ):

                valid_combinations.append( ( (combination), (0, 0) ) )
                

            

    #pp.pprint(valid_combinations)
    if verbose:
        print("numero de combinaciones válidas: ", len(valid_combinations))

    return valid_combinations


def recursive_trial(graph: nx.Graph, combination: tuple,  num_subjects: tuple, 
                    creds_semester: tuple, creds_hm: tuple, creds_elec: tuple, verbose = False):

    """

    """
    
    if verbose:
        print(graph, "...")


    # lista de materias completadas ese semestre
    completed_lecs = []

    # rellena la lista de materias completadas y modifica el grafo 
    # en caso de que haya que restar créditos de electivas HM o generales

    for lecture in combination[0]:

        if (lecture != 'Electiva general') and (lecture != 'Electiva HM'):
            completed_lecs.append( lecture ) 

        elif lecture == 'Electiva general':
            graph.nodes[lecture]["creds"] = graph.nodes[lecture]["creds"] - combination[1][0]
            
            # si se completaron todos los créditos de electiva general 
            # añadala a las materias completadas
            if graph.nodes[lecture]["creds"] == 0:
                completed_lecs.append(lecture)

            # si se excede la cantidad de electivas generales que se debían meter descarte la 
            # combinación
            elif graph.nodes[lecture]["creds"] < 0:
                print('secuencia descartada')
                return []

        else: 

            graph.nodes[lecture]["creds"] = graph.nodes[lecture]["creds"] - combination[1][1]
            
            # si se completaron todos los créditos de electiva general 
            # añadala a las materias completadas
            if graph.nodes[lecture]["creds"] == 0:
                completed_lecs.append(lecture)

            # si se excede la cantidad de electivas generales que se debían meter descarte la 
            # combinación
            elif graph.nodes[lecture]["creds"] < 0:
                print('secuencia descartada')
                return []

    # quita del grafo los nodos de las materias ya vistas
    graph.remove_nodes_from(completed_lecs)

    if verbose:
        print(graph)

    # obtiene las materias que se pueden ver 
    elegible_lectures = [lecture for lecture, indegree in graph.in_degree if indegree == 0]

    # crea las combinaciones viables de materias a inscribir
    valid_combinations = generate_valid_combinatorics(elegible_lectures, graph, num_subjects, 
                                                      creds_semester, creds_hm, creds_elec)

    if verbose:
        print("para", len(elegible_lectures), "materias elegibles hay: ", len(valid_combinations), "combinaciones validas")
    
    # si el numero de nodos que quedan en el grafo llega a ser cero 
    # quiere decir que se solucionó el problema
    if graph.number_of_nodes() == 0:
        return [ combination ]

    elif len(valid_combinations) == 0:
        return []

    else: 

        for new_combination in valid_combinations:

            solution = recursive_trial( deepcopy(graph), new_combination, num_subjects, creds_semester, 
                                        creds_hm, creds_elec, verbose)

            if len(solution) > 0:
                solution.append( combination ) 
                return solution

        return []
     


def correr_todo():

    num_subjects, creds_semester, creds_hm, creds_elec = take_usr_input()

    grafito = csv_to_graph()
    find_solutions(grafito, num_subjects, creds_semester, creds_hm, creds_elec, verbose = False)


start_time = datetime.now()
correr_todo()
end_time = datetime.now()
print('\nDuration: {}'.format(end_time - start_time))



#draw_graph(grafito) 
#check_graph_attrs(grafito)

#print("materias sin prerrquisitos")
#print(find_subjects_without_prerreqs(grafito))









