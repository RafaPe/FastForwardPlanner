import copy
from typing import List, Callable, Dict

class Proposition:
    def __init__(self, name:str, arg:str = '', negation:bool = False):
        self.name = name
        self.argument = arg
        self.negation = negation
        
    def __hash__(self):
        return hash((self.name, self.argument, self.negation))
    
    def __eq__(self, other):
        return isinstance(other, Proposition) and self.name == other.name and self.argument == other.argument and self.negation == other.negation
    
    def __invert__(self):
        if self.negation:
            return Proposition(self.name, self.argument, False)
        else:
            return Proposition(self.name, self.argument, True)
    
    def __str__(self):
        if self.negation:
            return f'¬{self.name}({self.argument})'
        else:
            return f'{self.name}({self.argument})'

# Se añadió el método de regresión para hacer la búsqueda sobre el espacio de objetivos
class Action:
    def __init__(self, name:str, preconditions:List[Proposition], delete:List[Proposition], effect:List[Proposition], variants:List[Proposition] = []):
        self.name = name
        self.preconditions = preconditions
        self.delete = delete
        self.effect = effect
        self.variants = variants
        
    def apply(self, state):
        state = copy.deepcopy(state)
        
        if len(self.variants) > 0:
            for condition, variant_effect, variant_delete in self.variants:
                if all(precondition in state for precondition in self.preconditions):
                    if condition in state: 
                        for element in variant_delete:
                            if element in state:
                                state.remove(element)
                        for element in variant_effect:
                            state.append(element)
                    else:
                        for element in self.delete:
                            if element in state:
                                state.remove(element)
                        for element in self.effect:
                            state.append(element)
        else:
            if all(precondition in state for precondition in self.preconditions):
                for element in self.delete:
                    if element in state:
                        state.remove(element)
                for element in self.effect:
                    state.append(element)
        return list(set(state))
    
    def regression(self, state:list):
        # Se verifica si el estado es regresable por la acción,
        # verificando si no existe una consistente con lo que se 
        # añade o se quita debido a la acción
        for remove_proposition in self.delete:
            if remove_proposition in state:
                return []
        for added_proposition in self.effect:
            if added_proposition not in state:
                return []
        
        # Se forma la regresión. De manera general, se agregan 
        # las proposiciones que la acción no añade y las precondiciones 
        # de la acción para poder activarse 
        regression_state = []
        # Cuando tiene variantes 
        if len(self.variants) > 0:
            for condition, variant_effect, variant_delete in self.variants:
                for proposition in variant_delete:
                    if proposition in state:
                        break
                for proposition in variant_effect:
                    if proposition not in state:
                        break
                for proposition in state:
                    if proposition not in variant_effect:
                        regression_state.append(proposition)
                regression_state.append(condition)
        else:
            for proposition in state:
                if proposition not in self.effect:
                    regression_state.append(proposition)
            for precondition in self.preconditions:
                regression_state.append(precondition)
            for proposition in self.delete:
                regression_state.append(proposition)

        return list(set(regression_state))

    def __str__(self):
        return f'{self.name}'

class Node:
    def __init__(self, state:List[Proposition], cost:int, heuristic:int, plan:str):
        self.state = state
        self.cost = cost
        self.heuristic = heuristic
        self.function = cost + heuristic
        self.plan = plan

def build_plan_graph(state:List[Proposition], goal:List[Proposition], actions:List[Action]) -> List[List[Proposition]]:   
    graph_levels = [state]
    
    i = 0
    while(True):
        new_level = [*graph_levels[i]]
        
        for action in actions:
            new_literals = action.apply(graph_levels[i])
            for lit in new_literals:
                new_level.append(lit)
                
        graph_levels.append(list(set(new_level)))
        
        if all(elem in new_level for elem in goal):
            break
        
        if len(list(set(new_level))) == len(graph_levels[i]):
            return []
            break
        
        i += 1
            
    return graph_levels

def graph_heuristic_backward(state:List[Proposition],planning_graph:List[List[Proposition]]) -> int:
    # Lo que se quiere es una heurística que indique en que nivel del grafo de 
    # planificación se encuentran todas las proposiciones de state
    level = 0
    try:
        while not all(proposition in planning_graph[level] for proposition in state):
            level += 1
        return level
    except:
        return float('inf')

def backward_A_star(initial_node:Node, goal:List[Proposition], actions:List[Action]) -> str:
    # Se calcula la gráfica de planeación del estado inicial que se usará como heurística
    planning_graph = build_plan_graph(initial_node.state,goal,actions)

    frontier = [initial_node]
    while len(frontier) > 0:
        node = frontier.pop(0)
        
        if SameList(node.state,goal):
            # Devuelve la lista de acciones en el orden 
            # inverso a como se agregaron y esta es el plan
            return node.plan[::-1]
            
        else:
            for action in actions:
                # Los nuevos estados son las regresiones del estado actual
                new_state = action.regression(node.state)
                   
                if all(elem in node.state for elem in new_state) and all(elem in new_state for elem in node.state) :
                    pass
                else:
                    h = graph_heuristic_backward(new_state,planning_graph)
                    c = node.cost + 1
                    new_node = Node(new_state, c, h, copy.deepcopy(node.plan))
                    new_node.plan.append(action)
                    
                    frontier.append(new_node)
            
            frontier = sorted(frontier, key = lambda x: x.function)
            
    return 'THERE IS NOT A FEASIBLE PLAN'

def SameList(state:List[Proposition],goal:List[Proposition]):
    # Esta función permite decidir cuando dos listas son iguales
    # tanto en tamaño como los elementos que contienen 
    if len(state) == len(goal):
        return all(proposition in state for proposition in goal)
    else:
        return False