import os
import numpy as np
import json

# http://glowingpython.blogspot.de/2011/05/four-ways-to-compute-google-pagerank.html
def maximalEigenvector(A):
	""" using the eig function to compute eigenvectors """
	n = A.shape[1]
	_,v = np.linalg.eig(A)
	return abs(np.real(v[:n,0])/np.linalg.norm(v[:n,0],1))

def getTeleMatrix(A,m):
	""" normalizes the matrix and adds dumping factor """
	n = A.shape[1]
	S = np.ones((n,n))/n
	return (1-m)*A+m*S

def rank_bots():
	files = dict()

	for file in os.listdir("."):
		if file.endswith(".txt"):
			files[file.split('.txt')[0]] = json.loads(''.join(open(file).readlines()))

	names = set(files.keys())
	names -= set(['total'])
	names = sorted(list(names))

	namePos = dict()
	for i, name in enumerate(names):
		namePos[name] = i

	mat = np.zeros(shape=(len(names),len(names)))
	for player in files:
		for otherPlayer in files[player]:
			if otherPlayer == 'total':
				continue

			i = namePos[player]
			j = namePos[otherPlayer]

			attDefStats = files[player][otherPlayer]
			games = attDefStats['games']
			wins = int(attDefStats['wins']) if 'wins' in attDefStats else 0.0

			mat[i, j] = wins / games

	dumping_factor = 0.15
	
	M = getTeleMatrix(mat, dumping_factor)
	scores = maximalEigenvector(M)

	for score, name in sorted(zip(scores, names), reverse=True):
		print(name, score)

if __name__ == '__main__':
	rank_bots()