from z3 import *
from math import floor
from pprint import pprint
import itertools
import numbers
import time

init("..")


def getVarName(truck, pallet):
	return "t"+truck.getIdent()+"p"+pallet.getIdent()

class Truck(object):
	ident = 0
	lst = []
	def __init__(self, cooled, weightCapacity, palletsCapacity):
		self.cooled 			= cooled
		self.weightCapacity 	= weightCapacity
		self.palletsCapacity 	= palletsCapacity
		Truck.ident 		   += 1
		self.ident 				= self.ident;
		Truck.lst.append(self)
	def getIdent(self):
		return str(self.ident)
	def generateVars(self, s):
		self.vars = [
				(p, Int(getVarName(self, p)))
				for p in PalletKind.lst
			]
		for p, v in self.vars:
			p.vars.append((self, v))
			s.add(v >= 0)

class PalletKind(object):
	ident = 0
	lst = []
	constraints = []
	def __init__(self, needCooled, weight, quantity, name):
		PalletKind.ident   += 1
		PalletKind.lst.append(self)
		self.needCooled		= needCooled
		self.name			= name
		self.weight			= weight
		self.ident 			= self.ident
		self.vars 			= []
		if isinstance(quantity, numbers.Number):
			self.nquantity	= str(quantity)
			self.quantity 	= Int("q"+str(self.ident))
			PalletKind.constraints.append(self.quantity == quantity)
		else:
			self.nquantity	= "?"
			self.quantity 	= quantity
	def getIdent(self):
		return str(self.ident)

def extractSeconds(l):
	return [b for a,b in l]
def findInCommon(truck, pallet):
	return list(set(extractSeconds(truck.vars)).intersection(extractSeconds(pallet.vars)))[0]
def addConstraints(s, avoidTogether):
	for p in PalletKind.lst:
		p.vars = []
	for t in Truck.lst:
		t.generateVars(s)
	for c in PalletKind.constraints:
		s.add(c)
	notCooledTrucks = [t for t in Truck.lst if not(t.cooled)]
	for pallet in PalletKind.lst:
		# There has to be a specific amount of pallet of this palletkind  
		s.add(reduce(
				lambda p, c : p + c,
				[t[1] for t in pallet.vars]
			) == pallet.quantity)
		if(pallet.needCooled):
			# if need cooled, no truck not cooled carry that kind of pallet 
			conditions = map(lambda t : findInCommon(t, pallet) == 0, notCooledTrucks)
			for c in conditions:
				s.add(c)

	for truck in Truck.lst:
		# A truck transport a maximum of pallets
 		s.add(reduce(
				lambda p, c : p + c,
				[t[1] for t in truck.vars]
			) <= truck.palletsCapacity)
		# A truck transport a maximum of weight
		s.add(reduce(
				lambda p, c : (0, c[1] * c[0].weight + p[1]),
				truck.vars, (0,0)
			)[1] <= truck.weightCapacity)
		# For each truck we want to know that avoidTogether
		for pA, pB in avoidTogether:
			if pA == pB:
				s.add(findInCommon(truck, pA) <= 1) # Then, we want maximum one pallet per truck maximum
			else:
				s.add(Or(findInCommon(truck, pA) == 0, findInCommon(truck, pB) == 0))
def outputSumup(model):
	for truck in Truck.lst:
		weight = 0
		for pallet in PalletKind.lst:
			var = model.get_interp(findInCommon(pallet, truck))
			value = int(str(var))
			weight += value * pallet.weight
		tname = "\t# Truck number "+str(truck.ident)
		if truck.cooled:
			tname += " (cooled)"
		else:
			tname += " (not cooled)"
		tname += " ["+str(weight)+"/"+str(truck.weightCapacity)+"kg]"
		print(tname)
		for pallet in PalletKind.lst:
			var = model.get_interp(findInCommon(pallet, truck))
			value = int(str(var))
			weight += value * pallet.weight
			if value > 0:
				print("\t\t"+str(var)+" "+pallet.name)
	print("\t# Sum up of palletkind")
	for pallet in PalletKind.lst:
		n = 0
		for truck in Truck.lst:
			var = model.get_interp(findInCommon(pallet, truck))
			value = int(str(var))
			n = n + value
		print("\t\t"+pallet.name+":\t "+str(n)+"/"+pallet.nquantity)

def getOutputTable(model):
	header = ["T"]
	for pallet in PalletKind.lst:
		header.append(pallet.name[0])
		header.append("$"+pallet.name[0]+"_w$")
	header.append("T$_p$")
	header.append("T$_w$")
	tab = []
	for truck in Truck.lst:
		line = [str(truck.ident) + ("*" if truck.cooled else "")]
		n = 0
		w = 0
		for pallet in PalletKind.lst:
			var = model.get_interp(findInCommon(pallet, truck))
			value = int(str(var))
			line.append(value)
			line.append(value * pallet.weight)
			n += value
			w += value * pallet.weight
		line.append(n)
		line.append(w)
		tab.append(line)
	totalBottom = [""]
	for pallet in PalletKind.lst:
		v = 0
		for line in tab:
			v += line[len(totalBottom)]
		totalBottom.append(v)
		totalBottom.append("")
	totalBottom.append("")
	totalBottom.append("")
	tab.insert(0, header)
	tab.append(totalBottom)
	return tab
def outputCSV(model):
	return '\n'.join(map(lambda l: ','.join(map(str, l)), getOutputTable(model)))


def outputLatexLike(model):
	data = getOutputTable(model)
	for x in xrange(0,len(data)):
		l = data[x]
		i = 2
		for x in PalletKind.lst:
			l[i] = "\\tiny \\color{gray} " + str(l[i])
			i += 2

	lStr = map(lambda l: ' & '.join(map(str, l)) + " \\\\", data)
	lStr.insert(1, "\hline")
	lStr.insert(0, "\hline")
	lStr.insert(len(lStr)-1, "\hline")
	lStr.insert(len(lStr), "\hline")
	body = '\n\t'.join(lStr)
	align = '|c|' + ('cc|'*len(PalletKind.lst)) + 'c|c|'
	return '\\begin{tabular}{'+align+'}\n'+body+'\n\\end{tabular}'

def checkSatForNumberOfPrittles(n, avoidTogether):
	s = Solver()
	addConstraints(s, avoidTogether)
	s.add(nPrittles >= n)
	r = str(s.check())=="sat"
	return r
def searchProperNumberOfPrittles(avoidTogether):
	dn = 1
	n = dn
	while(checkSatForNumberOfPrittles(n, avoidTogether)):
		n *= 2
	if n==dn:
		print("Error: UNSAT, problem could not be solved")
		return -1
	return binarySearch(int(n/2), n, avoidTogether)
def binarySearch(a,b, avoidTogether): # Assumption: checkSatForNumberOfPrittles(a) ^ not(checkSatForNumberOfPrittles(b))
	if a+1==b:
		return a
	else:
		middle = int((a+b)/2)
		if checkSatForNumberOfPrittles(middle, avoidTogether):
			return binarySearch(middle,b, avoidTogether)
		else:
			return binarySearch(a,middle, avoidTogether)

# print(s.to_smt2())
# exit()

# s.push()

def showResult(avoidTogether):
	# cacheCheckFor = {}
	numberOfPrittles = searchProperNumberOfPrittles(avoidTogether)
	
	print("## Computation if we avoid: "+("; ".join(a.name+" and "+b.name+" in the same truck" for a,b in avoidTogether)))

	print("\tFound numberOfPrittles= "+str(numberOfPrittles))

	solver = Solver()
	addConstraints(solver, avoidTogether)
	solver.add(nPrittles >= numberOfPrittles)
	solver.check()
	print(outputLatexLike(solver.model()))
	print("")
	print("")


nPrittles = Int("nPrittles")
Nuzzles	= PalletKind(False, 800	, 4, 			"Nuzzles")
Prittles= PalletKind(False, 1100, nPrittles, 	"Prittles")
Skipples= PalletKind(True , 1000, 8, 			"Skipples")
Crottles= PalletKind(False, 2500, 10, 			"Crottles")
Dupples	= PalletKind(False, 200	, 20, 			"Dupples")

Truck(False, 8000, 8);
Truck(False, 8000, 8);
Truck(False, 8000, 8);
Truck(False, 8000, 8);
Truck(False, 8000, 8);

Truck(True, 8000, 8);
Truck(True, 8000, 8);
Truck(True, 8000, 8);

# showResult([(Nuzzles, Nuzzles)])
showResult([(Nuzzles, Nuzzles), (Prittles, Crottles)])