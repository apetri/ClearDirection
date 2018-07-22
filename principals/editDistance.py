##########################################################
##Compute the edit distance between two iterables######### 
##of known length (arrays, strings, etc...) given the##### 
##cost functions for insertion/deletion/substitution######
##########################################################

import numpy as np

SUBSTITUTE = 0
INSERT = 1
DELETE = 2

class DistanceCalculator(object):

	#Initialize dynamic programming table (edit distance of matching pattern up to i to text up to j)
	def __init__(self,max_size=100):
		self._cost = np.zeros((max_size+1,)*2,dtype=np.int)
		self._parent = np.zeros((max_size+1,)*2,dtype=np.int)
		self._parent[0,0] = -1

	#Initialize rows
	def init_rows(self,text):
		for n,c in enumerate(text):
			self._cost[0,n+1] = self._cost[0,n] + self.cost_insertion(text[n])
			self._parent[0,n+1] = INSERT

	#Initialize columns
	def init_columns(self,pattern):
		for n,c in enumerate(pattern):
			self._cost[n+1,0] = self._cost[n,0] + self.cost_deletion(pattern[n])
			self._parent[n+1,0] = DELETE

	#############################################################

	#Cost of substitution
	def cost_substitution(self,x,y):
		return x.lower()!=y.lower()

	#Cost of deletion
	def cost_deletion(self,x):
		return 1

	#Cost of insertion
	def cost_insertion(self,x):
		return 1

	##############################################################

	#Edit distance calculator
	def editDistance(self,pattern,text):

		#Placeholder
		opt = np.zeros(3,dtype=np.int)
		
		#Initialize
		self.init_rows(text)
		self.init_columns(pattern)

		#Build the dinamic programming table iteratively
		for i in range(1,len(pattern)+1):
			for j in range(1,len(text)+1):

				#Evaluate the cost of the three options
				opt[SUBSTITUTE] = self._cost[i-1,j-1] + self.cost_substitution(pattern[i-1],text[j-1])
				opt[INSERT] = self._cost[i,j-1] + self.cost_insertion(text[j-1])
				opt[DELETE] = self._cost[i-1,j] + self.cost_deletion(pattern[i-1])

				#Choose the optimal option
				self._cost[i,j] = opt[SUBSTITUTE]
				self._parent[i,j] = SUBSTITUTE
				for k in [INSERT,DELETE]:
					if opt[k]<self._cost[i,j]:
						self._cost[i,j] = opt[k]
						self._parent[i,j] = k

		#Return the distance
		return self._cost[self.goalCell(pattern,text)]

	#Goal cell
	def goalCell(self,pattern,text):
		return (len(pattern),len(text))

	##############################################################

	#Reconstruct the path
	def reconstructPath(self,pattern,text,i=None,j=None):
		
		#Initialize
		if (i is None) and (j is None):
			i = len(pattern)
			j = len(pattern)
			self.editDistance(pattern,text)

		#Termination
		if self._parent[i,j]==-1:
			return

		#Recursion
		if self._parent[i,j]==SUBSTITUTE:
			self.reconstructPath(pattern,text,i-1,j-1)
			self.callback_substitution(pattern[i-1],text[j-1])

		elif self._parent[i,j]==INSERT:
			self.reconstructPath(pattern,text,i,j-1)
			self.callback_insertion(text[j-1])

		elif self._parent[i,j]==DELETE:
			self.reconstructPath(pattern,text,i-1,j)
			self.callback_deletion(pattern[i-1])		

	#Callbacks on substitutions,match, insertion, deletion
	def callback_substitution(self,x,y):
		if x==y:
			print("Match {0}".format(x))
		else:
			print("Substitute {0}-->{1}".format(x,y))

	def callback_insertion(self,x):
		print("Insert {0}".format(x))

	def callback_deletion(self,x):
		print("Delete {0}".format(x))