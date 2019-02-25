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

class Model:
    population = []
    fitness = []
    
    def setCreator(self, creator, populationSize = 30):
        self.creator = creator
        self.population = [self.creator() for i in range(0, populationSize)]
        return self
    
    def setMutator(self, mutator):
        self.mutator = mutator
        return self
    
    def setEvaluator(self, evaluator):
        self.evaluator = evaluator
        self.fitness = [self.evaluator(g) for g in self.population]
        return self
            
    def evolve(self, maxGenerations = 3000, crossoverRatio = 0.9, mutationRatio = 0.3):
        getWorst = lambda: self.fitness.index(max(self.fitness))
        getBest = lambda: self.fitness.index(min(self.fitness))
        getRandom = lambda: random.randrange(0, len(self.population))
        for i in range(0, maxGenerations):
            candidate = self.creator()
            for j in range(0, len(candidate)):
                if random.random() < crossoverRatio:
                    candidate[j] = self.population[getRandom()][j]
                    if random.random() < mutationRatio:
                        candidate[j] = self.mutator(candidate)[j]
            candidateFitness = self.evaluator(candidate)
            worstIndex = getWorst()
            if self.fitness[worstIndex] > candidateFitness:
                self.population[worstIndex], self.fitness[worstIndex] = candidate, candidateFitness
        return self.population[getBest()]
