
DIRECTIONS = [
	( 1, 0),
	( 1,-1),
	( 0,-1),
	(-1, 0),
	(-1, 1),
	( 0, 1)
]

def cube_add(coords, direction):
	return (coords[0] + direction[0], coords[1] + direction[1])

def neighbor(coords, direction):
	return cube_add(coords, DIRECTIONS[direction])

def get_ring(coords=(0,0), radius=1):
	if radius == 0:
		return set([coords])
	results = set()
	cube = cube_add(coords, (-radius, radius))
	for i in range(6):
		for j in range(radius):
			results.add(cube)
			cube = neighbor(cube, i)
	return results