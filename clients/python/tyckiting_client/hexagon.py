
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

def isInField(coords, radius):
	x,y = coords
	z = -x-y
	return -radius <= x <= radius and \
			-radius <= y <= radius and \
			-radius <= z <= radius

def extractValidCoordinates(coordinates, radius):
	validCoordinates = set()
	for coord in coordinates:
		if isInField(coord, radius):
			validCoordinates.add(coord)
	return validCoordinates