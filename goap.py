from abc import ABC, abstractmethod

import copy

class Action:    
    def cost(self, state):
        return 1
    
    @abstractmethod
    def isValid(self, state):
        pass
    
    @abstractmethod
    def do(self, state):
        pass
    
class Goal:
    @abstractmethod
    def isValid(self, prevState, nextState):
        pass
    
class Step:
    parent = None
    state = None
    action = None
    cost = 0
    
class Planner:
    actions = []
    
    def registerAction(self, action):
        self.actions.append(action)
        
    def buildGraph(self, prevStep, steps, actions, goal):
        for action in actions:
            if not action.isValid(prevStep.state):
                continue
            nextState = action.do(copy.deepcopy(prevStep.state))
            nextStep = Step()
            nextStep.parent = prevStep
            nextStep.state = nextState
            nextStep.action = action
            nextStep.cost = prevStep.cost + action.cost(nextState)
            if goal.isValid(prevStep.state, nextState):
                steps.append(nextStep)
            else:
                self.buildGraph(nextStep, steps, [a for a in actions if a != action], goal)
        return
    
    def traverseGraph(self, step):
        plan = []
        while(step is not None):
            if step.action is not None:
                plan.append(step.action)
            step = step.parent
        plan.reverse()
        return plan

    def getPlan(self, state, goal):
        root = Step()
        root.state = state
        steps = []
        self.buildGraph(root, steps, copy.copy(self.actions), goal)
        return self.traverseGraph(sorted(steps, key=lambda x: x.cost)[0])
