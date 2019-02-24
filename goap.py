import copy

class Action:    
    def cost(self, state):
        return 1
    
    def isValid(self, state):
        raise NotImplementedError
    
    def do(self, state):
        raise NotImplementedError
    
class Goal:
    def isValid(self, prevState, nextState):
        raise NotImplementedError
    
class Step:
    parent = None
    state = None
    action = None
    cost = 0
    
    def __init__(self, state):
        self.state = state
    
class Planner:
    actions = []
    
    def registerAction(self, action):
        self.actions.append(action)
        
    def buildGraph(self, prevStep, steps, actions, goal):
        for action in actions:
            if not action.isValid(prevStep.state):
                continue
            nextStep = Step(action.do(copy.deepcopy(prevStep.state)))
            nextStep.parent = prevStep
            nextStep.action = action
            nextStep.cost = prevStep.cost + action.cost(nextStep.state)
            if goal.isValid(prevStep.state, nextStep.state):
                steps.append(nextStep)
                steps.sort(key=lambda x: x.cost)
            else:
                if len(steps) == 0 or steps[0].cost > nextStep.cost:
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
        steps = []
        self.buildGraph(Step(state), steps, copy.copy(self.actions), goal)
        return self.traverseGraph(steps[0])
