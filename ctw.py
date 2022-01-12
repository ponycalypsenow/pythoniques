import numpy as np

class CTW():
	class Node():
		def __init__(self, symbols=2, parent=None):
			self.symbols = symbols
			self.parent = parent
			self.child = [None]*symbols
			self.depth = parent.depth + 1 if parent != None else 0
			self.c = [0]*symbols
			self.pe = self.pw = 0.0

	def __init__(self, max_depth=2, symbols=2, trace=None):
		if trace is None:
			trace = [0]*max_depth
		self.max_depth = max_depth
		self.root = CTW.Node(symbols=symbols)
		self.trace = trace

	def update(self, x, rollback, dummy):
		node = self.root
		for i in range(self.max_depth, -1, -1):
			if i != self.max_depth:
				if node.child[self.trace[i]] is None:
					node.child[self.trace[i]] = CTW.Node(symbols=node.symbols, parent=node)
				node = node.child[self.trace[i]]

			if not rollback:
				node.pe += np.log(node.c[x] + 1.0/node.symbols) - np.log(np.sum(node.c) + 1.0)
				node.c[x] += 1
			else:
				node.c[x] -= 1
				node.pe -= np.log(node.c[x] + 1.0/node.symbols) - np.log(np.sum(node.c) + 1.0)

		node.pw = node.pe
		while node.parent != None:
			node = node.parent
			pws = [node.child[i].pw if node.child[i] != None else 0.0 for i in range(node.symbols)]
			node.pw = np.log(0.5) + np.logaddexp(node.pe, np.sum(pws))

		if not dummy:
			self.trace = self.trace[1:] + [x]
   
	def train(self, train):
		for x in train:
			self.update(int(x), rollback=False, dummy=False)

	def predict(self):
		def probability(x):
			pw = self.root.pw
			self.update(x, rollback=False, dummy=True)
			pwx = self.root.pw
			self.update(x, rollback=True, dummy=True) 
			return np.exp(pwx - pw)
		return [probability(x) for x in range(self.root.symbols)]

	def report(self, node=None, suffix=[]):
		if node is None:
			node = self.root
		print("node {}: ({} {}), [{:.6f} {:.6f}]".format(str(suffix), node.c[0], node.c[1], np.exp(node.pe), np.exp(node.pw)))
		for i in [i for i in range(node.symbols) if node.child[i] != None]:
			self.report(node=node.child[i], suffix=[i] + suffix)

test = '012012012012012012012'
ctw = CTW(symbols=3)
ctw.train(test)
print(ctw.predict())
ctw.report()
