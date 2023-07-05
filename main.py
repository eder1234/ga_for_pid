from deap import base, creator, tools
import random
import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt

# Define the PID controller.
def pidController(system, P, I, D, t):
    # The 'system' is a list with two elements: the setpoint and the actual value.
    setpoint, actual = system

    # Compute the error.
    error = setpoint - actual

    # Compute the P term.
    Pterm = P * error

    # Compute the I term.
    Iterm = I * np.sum(error) * t

    # Compute the D term.
    Dterm = D * (error[-1] - error[-2]) / t if len(error) > 1 else 0

    # Return the PID controller output.
    return Pterm + Iterm + Dterm

# Define the system to control.
def system(y, t, pidOutput):
    # This could be anything, like a physical process or a mathematical function.
    return -pidOutput * t

# Define the fitness function.
def fitness(individual):
    P, I, D = individual

    # Run the system with the PID controller.
    t = np.linspace(0, 10, 100)
    solution = odeint(system, [0], t, args=(pidController([1,0], P, I, D, t),))

    # Compute the fitness as the sum of the absolute error.
    return np.sum(np.abs(1 - solution)),

# Set up the genetic algorithm.
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)
toolbox = base.Toolbox()
toolbox.register("attr_float", random.random)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_float, n=3)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("evaluate", fitness)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=1, indpb=0.1)
toolbox.register("select", tools.selTournament, tournsize=3)

# Run the genetic algorithm.
population = toolbox.population(n=50)
NGEN = 100
for gen in range(NGEN):
    offspring = toolbox.select(population, len(population))
    offspring = list(map(toolbox.clone, offspring))
    for child1, child2 in zip(offspring[::2], offspring[1::2]):
        if random.random() < 0.5:
            toolbox.mate(child1, child2)
            del child1.fitness.values
            del child2.fitness.values
    for mutant in offspring:
        if random.random() < 0.2:
            toolbox.mutate(mutant)
            del mutant.fitness.values
    invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
    fitnesses = map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit
    population[:] = offspring
best = tools.selBest(population, 1)[0]
print("Best individual: P={}, I={}, D={}".format(best[0], best[1], best[2]))
