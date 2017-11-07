from z3 import *
from math import floor
from pprint import pprint
import itertools
import numbers
import json

init("..")

class Chip(object):
	ident = 0
	def __init__(self, width, height):
		self.width = width
		self.height = height
		self.components = []
	def add(self, component):
		if component.attached:
			raise Exception('Component already attached')
		component.attached = True
		Chip.ident += 1
		ident = str(Chip.ident)
		component.x = Int('cx'+ident);
		component.y = Int('cy'+ident);
		component.rotate = Bool('cr'+ident);
		component.wrot = If(component.rotate, component.height, component.width)
		component.hrot = If(component.rotate, component.width, component.height)
		self.components.append(component)
	def initializeSolver(self):
		self.solver = Solver()
	def expressContenancyConstraints(self):
		for c in self.components:
			self.solver.add(c.x + c.wrot	<= self.width)
			self.solver.add(c.y + c.hrot	<= self.height)
			self.solver.add(c.y >= 0)
			self.solver.add(c.x >= 0)
	def expressNoOverlap(self):
		for ca in self.components:
			for cb in self.components:
				if ca!=cb:
					self.solver.add(Or(
							Or(ca.x + ca.wrot	<= cb.x, ca.x >= cb.x + cb.wrot),
							Or(ca.y + ca.hrot	<= cb.y, ca.y >= cb.y + cb.hrot)
						))
	def expressNeedOfPower(self):
		powerComponents = [c for c in self.components if c.isPower]
		otherComponents = [c for c in self.components if not(c.isPower)]
		for c in otherComponents:
			def mirrOr(f):
				return lambda p: Or(f(c, p), f(p, c))
			l = map(mirrOr(lambda p, c : Or( # We need to cover 4 cases (4 edges) : we mirror 2 cases with mirrOr (super pun)
					And(p.y == c.y+c.hrot, 
						Or(And(c.x >= p.x, c.x <= p.x + p.wrot), And(c.x <= p.x, c.x + c.wrot >= p.x)),
						Or(And(c.x >= p.x, c.x <= p.x + p.wrot), And(c.x <= p.x, c.x + c.wrot >= p.x)),
					),
					And(p.x == c.x+c.wrot, 
						Or(And(c.y >= p.y, c.y <= p.y + p.hrot), And(c.y <= p.y, c.y + c.hrot >= p.y)),
						Or(And(c.y >= p.y, c.y <= p.y + p.hrot), And(c.y <= p.y, c.y + c.hrot >= p.y)),
					)
				)), powerComponents)
			self.solver.add(reduce(Or, l))
	def expressMinimalDistancePowers(self):
		powerComponents = [c for c in self.components if c.isPower]
		d = self.distancePowerComponents
		print("d="+str(d))
		for ca in powerComponents:
			for cb in powerComponents:
				if ca!=cb:
					dx = ca.x*2 - cb.x*2 - cb.wrot + cb.hrot
					dy = ca.y*2 - cb.y*2 - cb.hrot + cb.wrot
					cx = dx >= d*2
					cy = dy >= d*2
					cb = Or(cx, cy)
					c  = If(dx >= 0,
							If(dy >= 0, cb, cx),	# dx >= 0
							Implies(dy >= 0, cy)	# dx <= 0
						)
					self.solver.add(c)
	def computeSolution(self, distancePowerComponents):
		self.distancePowerComponents = distancePowerComponents
		self.initializeSolver()
		self.expressContenancyConstraints()
		self.expressNoOverlap()
		self.expressNeedOfPower()
		self.expressMinimalDistancePowers()
		print(self.solver.check())
		return self.solver.model()
	def extractRectangles(self, model):
		def gx(component):
			return int(str(model.get_interp(component.x)))
		def gy(component):
			return int(str(model.get_interp(component.y)))
		def grot(component):
			return str(model.get_interp(component.rotate))=="True"
		def gw(component):
			if grot(component):
				return component.height
			return component.width
		def gh(component):
			if grot(component):
				return component.width
			return component.height
		return map(lambda c: {
				"x": gx(c), 
				"y": gy(c),
				"w": gw(c),
				"h": gh(c),
				"specw": c.width,
				"spech": c.height,
				"isPower": c.isPower,
				"name": c.name
			}, self.components)
	def toHTML(self,model,outputFile):
		j = json.dumps(self.extractRectangles(model))
		html = """	<canvas id='draw'></canvas>
					<script>var exportedJSON = """+j+"""</script>
					<script type="text/javascript" src='dispExo2.js'></script>		"""
		with open(outputFile, 'w+') as f:
		    f.seek(0)
		    f.write(html)
		    f.truncate()


class Component(object):
	def __init__(self, width, height, isPower, name):
		self.width = width
		self.height = height
		self.isPower = isPower
		self.name = name
		self.attached = False

chip = Chip(30, 30)
components = [ 
		  Component(4, 5, False, 	'a')
		, Component(4, 6, False, 	'b')
		, Component(5, 20, False, 	'c')
		, Component(6, 9, False, 	'd')
		, Component(6, 10, False, 	'e')
		, Component(6, 11, False, 	'f')
		, Component(7, 8, False, 	'g')
		, Component(7, 12, False, 	'h')
		, Component(10, 10, False, 	'i')
		, Component(10, 20, False, 	'j')

		, Component(4, 3, True, 	'P1')
		, Component(4, 3, True, 	'P2')
	]
for c in components:
	chip.add(c)

for distance in [18, 20, 22]:
	m = chip.computeSolution(distance)
	chip.toHTML(m, 'output_'+str(distance)+".html")
	# chip.outputCharMatrix(m, "output_"+str(distance)+".html")