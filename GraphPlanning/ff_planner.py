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

def graph_heuristic(state:List[Proposition], goal:List[Proposition], actions:List[Action]) -> int:
    graph = build_plan_graph(state, goal, actions)
    if len(graph) > 0:
        return len(graph) - 1
    else:
        return float('inf')

def fastforward_A_star(initial_node:Node, goal:List[Proposition], actions:List[Action]) -> str:
    frontier = [initial_node]
    while len(frontier) > 0:
        node = frontier.pop(0)
        
        if all(elem in node.state for elem in goal):
            return node.plan
            break
            
        else:
            for action in actions:
                new_state = action.apply(node.state)
                   
                if all(elem in node.state for elem in new_state) and all(elem in new_state for elem in node.state) :
                    pass
                else:
                    h = graph_heuristic(new_state, goal, actions)
                    c = node.cost + 1
                    new_node = Node(new_state, c, h, copy.deepcopy(node.plan))
                    new_node.plan.append(action)
                    
                    frontier.append(new_node)
            
            frontier = sorted(frontier, key = lambda x: x.function)
            
    return 'THERE IS NOT A FEASIBLE PLAN'


        
        