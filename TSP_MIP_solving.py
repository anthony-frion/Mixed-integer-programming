# -*- coding: utf-8 -*-
"""
Created on Wed Jul 29 09:14:39 2020

@author: Anthony
"""

from TSP import *

from time import time
import random as rd

try :
    from pulp import *
except :
    print("You have not installed pulp : you will not be able to use it")
    
try :
    import gurobipy as grb
except :
    print("You have not installed gurobi : you will not be able to use it")

# Given a "solution", finds all the included subtours.
# A real TSP solution should have no subtours at all since it forms a loop including all the cities.
def findSubtours(solution) :
    n = len(solution)
    subtours = []
    visited = [False for i in range(n)]
    i = 0
    while i < n :
        if not visited[i] :
            visited[i] = True
            subtour = [i]
            j = 0
            while not solution[i][j] :
                j += 1
            while j != i :
                subtour.append(j)
                visited[j] = True
                new_j = 0
                while not solution[j][new_j] :
                    new_j += 1
                j = new_j
            subtours.append(subtour)
        i += 1
    return subtours

# Solves a given problem using MIP with the Dantzig-Fulkerson-Johnson (DFJ) formulation
# The argument 'subtourEliminations' is a list of subtours for which constraints should be added
# to prevent the algorithm from returning a solution including one of those subtours
# The argument solver enables the user to choose using the MIP solver software 'GLPK' or the
# 'COIN' solver (default, and usually faster)
def solveDFJPulp(problem, subtourEliminations = [], print_sol=False, solver=None) :
    distances = problem.distances
    n = problem.numberPoints
    
    model = LpProblem("problem", LpMinimize)
    
    x = {(i, j): LpVariable("x_{},{}".format(i, j), cat='Binary') for i in range(n) for j in range(n)}
    
    for i in range(n) :
        model += x[(i, i)] == 0
    
    for i in range(n) :
        model += lpSum(x[(i, j)] for j in range(n)) == 1
        
    for j in range(n) :
        model += lpSum(x[(i, j)] for i in range(n)) == 1
        
    for subset in subtourEliminations :
        model += lpSum(x[(i,j)] for j in subset for i in subset) <= len(subset) - 1
    
    model += lpSum(x[(i,j)] * distances[i][j] for j in range(n) for i in range(n))
    
    if solver == 'glpk' :
        model.solve(GLPK_CMD(options=["--pcost"]))
    else :
        model.solve()
    
    solution = []
    for i in range(n) :
        solution.append([round(x[(i, j)].varValue) for j in range(n)])
        if print_sol :
            print(solution[i])
    return solution, value(model.objective)

# Does the exact same as the previous function, but with gurobi, which is a better performing software
# The boolean argument 'printLog' enables you to choose whether you want to print the gurobi resolution log or not
def solveDFJGurobi(problem, subtourEliminations = [], print_sol=False, printLog=False) :
    distances = problem.distances
    n = problem.numberPoints
    
    model = grb.Model()
    
    x = {(i, j): model.addVar(vtype=grb.GRB.BINARY, name="x_{},{}".format(i, j)) for i in range(n) for j in range(n)}
    
    for i in range(n) :
        model.addConstr(x[(i, i)], grb.GRB.EQUAL, 0)
    
    for i in range(n) :
        model.addConstr(grb.quicksum(x[(i, j)] for j in range(n)), grb.GRB.EQUAL, 1)
        
    for j in range(n) :
        model.addConstr(grb.quicksum(x[(i, j)] for i in range(n)), grb.GRB.EQUAL, 1)
    
    for subset in subtourEliminations :
        model.addConstr(grb.quicksum(x[(i,j)] for j in subset for i in subset), grb.GRB.LESS_EQUAL, len(subset) - 1)
    
    objective = grb.quicksum(x[(i,j)] * distances[i][j] for j in range(n) for i in range(n))
    
    model.setObjective(objective)
    
    model.ModelSense = grb.GRB.MINIMIZE
    
    model.setParam(grb.GRB.Param.LogToConsole, printLog)
    
    model.optimize()
    
    solution = []
    for i in range(n) :
        solution.append([round(x[(i, j)].getAttr(grb.GRB.Attr.X)) for j in range(n)])
        if print_sol :
            print(solution[i])
    return solution, model.getObjective().getValue()

# This function takes a TSP instance as input and iteratively solves it with MIP and eliminates
# the subtours from the solution, until it finds a solution with no subtours at all, which will
# actually be the best valid solution of the TSP instance
def solveIterativeSubtourEliminationPulp(problem) :
    t0 = time()
    subtourEliminations = []
    solution, value = solveDFJPulp(problem, subtourEliminations)
    newSubtours = findSubtours(solution)
    while len(newSubtours) > 1 :
        subtourEliminations += newSubtours
        solution, value = solveDFJPulp(problem, subtourEliminations)
        newSubtours = findSubtours(solution)
    #print(solution)
    print("Overall computing time : {} seconds".format(time() - t0))
    return solution, time() - t0

# Does the exact same as the previous function, but with gurobi
def solveIterativeSubtourEliminationGurobi(problem) :
    t0 = time()
    subtourEliminations = []
    solution, value = solveDFJGurobi(problem, subtourEliminations)
    newSubtours = findSubtours(solution)
    while len(newSubtours) > 1 :
        subtourEliminations += newSubtours
        solution, value = solveDFJGurobi(problem, subtourEliminations)
        newSubtours = findSubtours(solution)
    #print(solution)
    print("Overall computing time : {} seconds".format(time() - t0))
    return solution, time() - t0

nb_points = 60
size = (1200, 600)

problem = generateRandomTSP(nb_points, size[0], size[1])

try :
    solution, comp_time = solveIterativeSubtourEliminationGurobi(problem)
except :
    solution, comp_time = solveIterativeSubtourEliminationPulp(problem)
    
'''
for line in solution :
    print(line)
'''

# Importing pygame to visualise the solution
import pygame as pg
from pygame.locals import *

# A few variables for the graphical representation
window_size_x = size[0] + 50
window_size_y = size[1] + 50
offset = 25
radius = 8

pg.init()

window = pg.display.set_mode((window_size_x, window_size_y))

def show_cities(problem, window) :
    pg.draw.rect(window, (255, 255, 255), pg.Rect(0, 0, window_size_x, window_size_y))
    points = problem.points
    for point in points :
        draw_position = (fst(point) + offset, snd(point) + offset)
        color = (255, 0, 0) if point == points[0] else (0, 0, 0)
        pg.draw.circle(window, color, draw_position, radius)
    pg.display.flip()

# Shows the solution to a problem on the argument window
def show_solution(problem, solution, window) :
    pg.draw.rect(window, (255, 255, 255), pg.Rect(0, 0, window_size_x, window_size_y))
    points = problem.points
    for point in points :
        draw_position = (fst(point) + offset, snd(point) + offset)
        color = (255, 0, 0) if point == points[0] else (0, 0, 0)
        pg.draw.circle(window, color, draw_position, radius)
    for i in range(len(solution)) :
        for j in range(len(solution[i])) :
            if solution[i][j] == 1 :
                draw_position_i = (fst(points[i]) + offset, snd(points[i]) + offset)
                draw_position_j = (fst(points[j]) + offset, snd(points[j]) + offset)
                pg.draw.line(window, (0, 0, 0), draw_position_i, draw_position_j)
    pg.display.flip()
    
print("The optimal solution of the problem has been computed.")
print("The positions of the cities will now be showed.")
print("You can press SPACE at any time to show/hide the optimal solution.")

show_cities(problem, window)

keep = True
solution_showed = False

while keep :
    
    pg.time.Clock().tick(100)
    for event in pg.event.get() :
        if event.type == KEYDOWN and event.key == K_SPACE :
            if not solution_showed :
                solution_showed = True
                show_solution(problem, solution, window)
            else :
                solution_showed = False
                show_cities(problem, window)
        if event.type == KEYDOWN and event.key == K_ESCAPE :
            keep = False

pg.quit()
