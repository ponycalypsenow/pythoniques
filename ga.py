import random

class Creators:
    def Real(n, low = 0.0, high = 1.0):
        def realCreator():
            return [random.uniform(low, high) for _ in range(0, n)]
        return realCreator
    
    def Discrete(n, alphabetSize):
        def discreteCreator():
            return [random.randint(0, alphabetSize) for _ in range(0, n)]
        return discreteCreator

class Mutators:
    def Real(low = 0.0, high = 1.0, gamma = 0.01):
        def realMutator(g):
            d = abs(high - low)*gamma
            return [max(min(v + random.uniform(-d, d), high), low) for v in g]
        return realMutator
    
    def Discrete(alphabetSize, gamma = 1):
        def discreteMutator(g):
            return [max(min(v + random.randint(-gamma, gamma), alphabetSize), 0) for v in g]
        return discreteMutator
    
class Evaluators:
    def Beale(x):
        return (1.5 - x[0] + x[0]*x[1])**2 + (2.25 - x[0] + x[0]*(x[1]**2))**2 + (2.625 - x[0] + x[0]*(x[1]**3))**2
    
    def DummyDiscrete(x):
        return abs(sum([(a - b)**2 for a, b in zip(x, [1,2,3,4])]))

class Model:
    population = []
    fitness = []
    
    def setCreator(self, creator, populationSize = 30):
        self.creator = creator
        self.population = [self.creator() for i in range(0, populationSize + 1)]
        return self
    
    def setMutator(self, mutator):
        self.mutator = mutator
        return self
    
    def setEvaluator(self, evaluator):
        self.evaluator = evaluator
        self.fitness = [self.evaluator(g) for g in self.population]
        return self
    
    def getBest(self):
        return self.fitness.index(min(self.fitness))
    
    def getWorst(self):
        return self.fitness.index(max(self.fitness))
            
    def evolve(self, maxGenerations = 3, crossoverRatio = 0.9, mutationRatio = 0.3):
        for i in range(0, maxGenerations):
            self.population[-1] = self.creator()
            for j in range(0, len(self.population[-1])):
                if random.random() < crossoverRatio:
                    self.population[-1][j] = self.population[random.randrange(0, len(self.population) - 1)][j]
                    if random.random() < mutationRatio:
                        self.population[-1][j] = self.mutator(self.population[-1])[j]
                self.fitness[-1] = self.evaluator(self.population[-1])
            worstIndex = self.getWorst()
            if worstIndex < len(self.population) - 1:
                self.population[worstIndex] = self.population[-1]
                self.fitness[worstIndex] = self.fitness[-1]
        return self.population[self.getBest()]
            
m = Model()
m.setCreator(Creators.Real(2, -4.5, 4.5))
m.setMutator(Mutators.Real(-4.5, 4.5))
m.setEvaluator(Evaluators.Beale)
print(m.evolve())
