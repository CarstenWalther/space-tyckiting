import os
import pandas as pd
import numpy as np
import json


# http://glowingpython.blogspot.de/2011/05/four-ways-to-compute-google-pagerank.html
def maximalEigenvector(A):
	""" using the eig function to compute eigenvectors """
	n = A.shape[1]
	w,v = np.linalg.eig(A)
	return abs(np.real(v[:n,0])/np.linalg.norm(v[:n,0],1))

def getTeleMatrix(A,m):
	""" return the matrix M
    	of the web described by A """
	n = A.shape[1]
	S = np.ones((n,n))/n
	return (1-m)*A+m*S


# http://arxiv.org/pdf/1503.01331.pdf
def test_pagerank_paper():
	players = ['A', 'B', 'C', 'D']
	n = len(players)
	d = 0.15

	# f = wins / games
	mat = np.matrix([
		[0, 2/3, 2/3, 1],
		[1/3, 0, 0, 1],
		[1/3, 1, 0, 1/3],
		[0, 0, 2/3, 0]
	])

	M = getTeleMatrix(mat,d)

	scores = maximalEigenvector(M)

	print(scores)


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
	#default = 0.0
	#mat[mat == 0] = default
	for player in files:
		for otherPlayer in files[player]:
			if otherPlayer == 'total':
				continue

			i = namePos[player]
			j = namePos[otherPlayer]

			#if i == j:
				#mat[i, j] = 0.5
				#continue

			attDefStats = files[player][otherPlayer]
			games = attDefStats['games']
			wins = int(attDefStats['wins']) if 'wins' in attDefStats else 0.0
			losses = games - wins

			mat[i, j] = wins / games
			#mat[j, i] = 1 - wins / games

	for i in range(0, len(names)+1):
		if i == 0:
			name = '      '
		else:
			name = names[i-1]
		print('{:6}'.format(name[:6]), end=' ')
	print()
	for i in range(len(names)):
		print('{:6}'.format(names[i][:6]), end=' ')
		for j in range(len(names)):
			print('{:6.3f}'.format(mat[i, j]), end=' ')
		print('')

	n = len(names)
	dumping_factor = 0.15
	
	M = getTeleMatrix(mat, dumping_factor)
	scores = maximalEigenvector(M)

	for score, name in sorted(zip(scores, names), reverse=True):
		print(name, score)

if __name__ == '__main__':
	rank_bots()