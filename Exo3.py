from z3 import *
from math import floor
from pprint import pprint
import itertools
import numbers
import json

init("..")

class JobScheduler(object):
	def __init__(self, maxTime, jobs):
		self.jobs = jobs
		self.solver = Solver()
		self.maxTime = maxTime
		def replaceJobIdByJob(id):
			for j in jobs:
				if j.id==id:
					return j
			return id
		def replaceJobsIdByJobs(list):
			return [replaceJobIdByJob(i) for i in list]
		for j in jobs:
			j.startOnlyAfterJobsDone= replaceJobsIdByJobs(j.startOnlyAfterJobsDone)
			j.startNotEarlierThan	= replaceJobsIdByJobs(j.startNotEarlierThan)
			j.notInSameTimeThan		= replaceJobsIdByJobs(j.notInSameTimeThan)
	def expressWellDefineness(self):
		for j in self.jobs:
			self.solver.add(j.startTime >= 0)
	def expressMaximumTime(self):
		for j in self.jobs:
			self.solver.add(j.startTime + j.runningTime <= self.maxTime)
	def expressStartAfterDone(self):
		for j in self.jobs:
			for b in j.startOnlyAfterJobsDone:
				self.solver.add(j.startTime >= b.startTime + b.runningTime)
	def expressStartNotEarlier(self):
		for j in self.jobs:
			for b in j.startNotEarlierThan:
				self.solver.add(j.startTime >= b.startTime)
	def expressNotInSameTime(self):
		for j in self.jobs:
			for b in j.notInSameTimeThan:
				self.solver.add(Or(j.startTime + j.runningTime <= b.startTime, j.startTime >= b.startTime + b.runningTime))
	def expressAllAndCompute(self):
		self.expressMaximumTime()
		self.expressWellDefineness()
		self.expressStartNotEarlier()
		self.expressStartAfterDone()
		self.expressNotInSameTime()
		return self.compute()
	def compute(self):
		r = str(self.solver.check())
		print(r)
		result = r=="sat"
		if not(result):
			return False
		model = self.solver.model()
		for j in self.jobs:
			j.actualStartingTime = int(str(model.get_interp(j.startTime)))
		return map(lambda j: [j.actualStartingTime, j.runningTime, j.id], self.jobs)
	def toHTML(self,data,outputFile):
		j = json.dumps(data)
		if not(data):
			html = "UNSAT"
		else:
			html = """	<canvas id='draw'></canvas>
						<script>var exportedJSON = """+j+"""</script>
						<script type="text/javascript" src='../dispExo3.js'></script>		"""
		with open(outputFile, 'w+') as f:
		    f.seek(0)
		    f.write(html)
		    f.truncate()

class Job(object):
	def __init__(self, id, runningTime, startOnlyAfterJobsDone, startNotEarlierThan, notInSameTimeThan):
		self.id 		= id
		self.runningTime= runningTime
		self.startOnlyAfterJobsDone = startOnlyAfterJobsDone
		self.startNotEarlierThan 	= startNotEarlierThan
		self.notInSameTimeThan 		= notInSameTimeThan
		self.startTime = Int("j"+str(id))

jobs=	[ Job( 1, 1+5, [],		[],	[]		)
		, Job( 2, 2+5, [],		[],	[]		)
		, Job( 3, 3+5, [1,2],	[],	[]		)
		, Job( 4, 4+5, [],		[],	[]		)
		, Job( 5, 5+5, [3,4],	[],	[7,10]	)
		, Job( 6, 6+5, [],		[],	[]		)
		, Job( 7, 7+5, [3,4,6],	[],	[5,10]	)
		, Job( 8, 8+5, [],		[5],[]		)
		, Job( 9, 9+5, [5,8],	[],	[]		)
		, Job(10,10+5, [],		[],	[5,7]	)
		, Job(11,11+5, [10],	[],	[]		)
		, Job(12,12+5, [9,11],	[],	[]		)]

i = 1
last = False
scheduler = JobScheduler(i, jobs)
while True:
	scheduler = JobScheduler(i, jobs)
	last = scheduler.expressAllAndCompute()
	if last!=False:
		break
	print("Tried with "+str(i))
	i += 1
print("Found! i="+str(i))
scheduler.toHTML(last, "resultExo3/result.html")