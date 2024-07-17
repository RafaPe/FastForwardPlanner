# PlanGraphSearch
Este repositorio implementa un enfoque de planificación inspirado en los planificadores Fast Forward, utilizando el algoritmo de búsqueda A* para una exploración eficiente del espacio de soluciones.

## Introducción
Llamaremos planificación al proceso de búsqueda y articulación de una secuencia de acciones que permitan alcanzar un objetivo.
Para un problema de planificación necesitaremos proposiciones (las cuales llamaremos literales), que describan los estados, y acciones, las cuales serán operaciones que cambian los literales (alteran el estado). 

Para la definición de las literales y acciones se usa generalmente el lenguaje STRIPS (STandford Research Institute Problem Solver), pero se ha visto que este no presenta la suficiente expresividad para algunos problemas, por lo cual se han desarrollado extensiones de este como sería el el ADL (Action Description Language)

Dentro de los algoritmos planificación, el base es el Graph Plan, el cual se basa en la construcción de la gráfica de planeación y el lenguaje ADL. Este algoritmo presenta mucha complejidad por lo cual se construyó una versión relajada que inspiró a los llamados Fast Forward Planner. Estos utilizan la idea de Graph Plan pero en una versión relajada que se usa como heurística.

El algoritmo A* es un algoritmo de búsqueda heurística utilizado para encontrar la ruta más corta en un grafo. A* utiliza una función de costo \( f(n) = g(n) + h(n) \), donde \( g(n) \) es el costo desde el nodo inicial hasta el nodo actual \( n \) y \( h(n) \) es una estimación heurística del costo desde \( n \) hasta el nodo objetivo. Selecciona los nodos a explorar basándose en esta función, priorizando aquellos que parecen más prometedores para llegar al objetivo con el menor costo total, lo que lo hace muy efectivo para problemas de planificación.

## Algoritmo
El algoritmo usa la búsqueda A* clásica de la siguiente manera
```
función FastForward_A*(estado_inicial, objetivo, acciones):
    frontera ← [estado_inicial]
    
    mientras frontera no esté vacía:
        nodo ← primer elemento de frontera
        eliminar primer elemento de frontera
        
        si todos los elementos de objetivo están en nodo.estado:
            regresar nodo.plan
            
        de lo contrario:
            para cada acción en acciones:
                nuevo_estado ← acción.aplicar(nodo.estado)
                
                h ← heurística(nuevo_estado, objetivo, acciones)
                c ← nodo.costo + 1
                nuevo_nodo ← Nodo(nuevo_estado, c, h, nodo.plan)
                nuevo_nodo.plan ← nuevo_nodo.plan + acción
                    
                añadir nuevo_nodo a frontera
            
            frontera ← ordenar(frontera por función de costo)
            
    regresar "NO HAY RESPUESTA"
```
Para el cálculo de la heurística, nos basamos en la gráfica de planeación, la cual se construye añadiendo los efectos de todas las acciones en cada nivel hasta que en algún nivel se encuentren todas las proposiciones del estado objetivo.
```
función construir_grafica(estado, objetivo, acciones):
    niveles_grafo ← [estado]
    i ← 0
    
    mientras Verdadero:
        nuevo_nivel ← copiar elementos de niveles_grafo[i]
        
        para cada acción en acciones:
            nuevas_literales ← acción.aplicar(niveles_grafo[i])
            para cada literal en nuevas_literales:
                añadir literal a nuevo_nivel
        
        añadir nuevo_nivel a niveles_grafo
        
        si todos los elementos de objetivo están en nuevo_nivel:
            romper ciclo
        
        si la longitud de nuevo_nivel es igual a la longitud de niveles_grafo[i]:
            regresar lista vacía  # No hay solución
        
        i ← i + 1
    
    regresar niveles_grafo
```
Finalmente la heurística que seguiremos es la cantidad de niveles que se necesitan para obtener las proposiciones del objetivo. Esta claramente es una heurística aceptable y óptima.
```
función heurística(estado, objetivo, acciones):
    grafo ← construir_grafica(estado, objetivo, acciones)
    
    si longitud de grafo > 0:
        regresar longitud de grafo - 1
    sino:
        regresar infinito
```