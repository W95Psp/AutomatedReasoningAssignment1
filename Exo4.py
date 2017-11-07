from z3 import *
from math import floor
from pprint import pprint
import itertools
import numbers
import operator
import json
import time

init("..")

def boolToInt(x):
	return If(x,1,0)

class Process(object):
	def __init__(self, id, max_i):
		self.id = id
		# self.i = Int("i"+str(id))
		self.max_i = max_i

class Computer(object):
	def __init__(self, processes, specC):
		self.processes = processes
		self.specC = specC
		self.numberSteps = reduce(operator.add, [p.max_i for p in processes])
		for p in processes:
			p.isActiveVars = [Bool("p"+str(p.id)+"a"+str(n)) for n in xrange(1, self.numberSteps+1)]
		self.solver = Solver()
	def expressActiveVarsWelldefiness(self):
		for p in self.processes:
			self.solver.add(reduce(operator.add, [boolToInt(v) for v in p.isActiveVars]) == p.max_i)
		for s in xrange(1, self.numberSteps):
			# self.solver.add(reduce(Or, [p.isActiveVars[s-1] for p in self.processes]))
			def getV(p):
				return p.isActiveVars[s-1]
			def ID(x):
				return x
			self.solver.add(reduce(
   				  Or
				, map(
					  lambda pa: And(*[(ID if pb==pa else Not)(getV(pb)) for pb in self.processes])
					, self.processes
					)
				))
			# for pa in self.processes:
			# 	self.solver.add(Implies(pa.isActiveVars[s-1], reduce(And, [pb.isActiveVars[s-1] for pb in self.processes if pb!=pa])))
	def expressC(self):
		def getIForNthStepAndProcessor(p, n): # n start at 0
			if n==self.numberSteps-1:
				return p.max_i
			return reduce(operator.add, [boolToInt(v) for v in p.isActiveVars[:n]], 1)
		self.inspectIVars = map(lambda x:False, xrange(0,self.numberSteps))
		self.inspectCVars = map(lambda x:False, xrange(0,self.numberSteps))
		def getIForNthStep(n):
			s = 0
			for p in self.processes:
				s += If(p.isActiveVars[n], getIForNthStepAndProcessor(p, n), 0)
			return s
		def getCForNthStep(n): # n start at 0
			currentC = min(n+1, 20)
			for x in xrange(20,n+1):
				currentC += getIForNthStep(x)
			return currentC

		for i in xrange(0,self.numberSteps):
			if self.inspectIVars[i]==False:
				self.inspectIVars[i] = Int("i_at_step_"+str(i))
				self.solver.add(self.inspectIVars[i] == getIForNthStep(i))
			if self.inspectCVars[i]==False:
				self.inspectCVars[i] = Int("c_at_step_"+str(i))
				self.solver.add(self.inspectCVars[i] == getCForNthStep(i))
			
		self.C = Int("C")
		self.solver.add(getCForNthStep(self.numberSteps-1) == self.C)
		self.solver.add(self.specC(self.C))
	def compute(self, timeout=0):
		if timeout>0:
			self.solver.set("timeout", timeout);
		r = str(self.solver.check())
		print(r)
		result = r=="sat"
		if r=="unknown":
			return r
		if result==False:
			return False
		# print(self.solver.to_smt2())
		m = self.solver.model()
		def getIntInModel(v):
			if v==False:
				return -1
			return int(getInModel(v))
		def getInModel(v):
			return str(m.get_interp(v))
		def getIsActiveVars(p):
			return [getInModel(v)=="True" for v in p.isActiveVars]
		# print("self.C = ", getInModel(self.C))
		return {
				  "processes": 	[[getIsActiveVars(p), p.id, p.max_i] for p in self.processes]
				, "C": 			getIntInModel(self.C)
				, "steps":		[[getIntInModel(self.inspectIVars[step]), getIntInModel(self.inspectCVars[step])] for step in xrange(0, self.numberSteps)]
			}
	def toHTML(self,data,outputFile):
		if not(data):
			html = "UNSAT"
			return
		else:
			j = json.dumps(data)
			html = """	<canvas id='draw'></canvas>
						<script>var exportedJSON = """+j+"""</script>
						<script type="text/javascript" src='../dispExo4.js'></script>		"""
		with open(outputFile, 'w+') as f:
			f.seek(0)
			f.write(html)
			f.truncate()

def lookForValues(_min, _max, timeout=0, child=False):
	if _min > _max:
		return False
	print("")
	startTime = time.time()
	print("Search between "+str(_min)+" and "+str(_max)+"...")
	c = Computer([Process(1,20), Process(2,20)], lambda x: And(x >= _min, x <= _max))
	c.expressActiveVarsWelldefiness()
	c.expressC()
	r = c.compute(timeout)
	if r=="unknown":
		print("\t-- Timeout between "+str(_min)+" and "+str(_max)+"|")
		return False
	if r==False:
		print("\t-- Nothing found between "+str(_min)+" and "+str(_max)+"|")
		return False
	rC = r["C"]
	print("\t-> Found "+str(rC)+" between "+str(_min)+" and "+str(_max)+"|")
	c.toHTML(r, 'resultExo4/out'+str(rC)+'.html')
	lookForValues(_min, rC-1, timeout, True)
	lookForValues(rC+1, _max, timeout, True)
	if child==False:
		print("Searched into ["+str(_min)+", "+str(_max)+"] in "+str(time.time() - startTime)+"s")

# lookForValues(249, 250)
# lookForValues(10, 300)
# lookForValues(300, 400)

# lookForValues(300, 400)

# lookForValues(230, 230)
# lookForValues(281, 281)
# lookForValues(330, 330)

# lookForValues(0, 500)
lookForValues(0, 500, 4*60*1000)

# c = Computer([Process(1,20), Process(2,20)], lambda x: And(x > 330))
# c.expressActiveVarsWelldefiness()
# c.expressC()
# r = c.compute()

# print(r)

# lookForValues(330, 500)
# lookForValues(281, 300)

# if len(sys.argv)>1:
# 	CI = int(sys.argv[1])
# else:
# 	CI = -1
# print("CI = " + str(CI))
# # for i in xrange(1, 50):
# for i in xrange(332,333):
# 	if CI==-1 or i%4==CI:
# 		print("Compute i = "+str(i))
# 		c = Computer([Process(1,20), Process(2,20)], lambda x: And(x >= i))
# 		c.expressActiveVarsWelldefiness()
# 		c.expressC()
# 		c.toHTML(c.compute(), 'resultExo4/out'+str(i)+'.html')