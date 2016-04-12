
DIRECTIONS = [
	( 1, 0),
	( 1,-1),
	( 0,-1),
	(-1, 0),
	(-1, 1),
	( 0, 1)
]

def totalAmountOfHexagons(radius):
	return 1 + 6 * (radius*(radius+1)/2)

def cube_add(coords, direction):
	return (coords[0] + direction[0], coords[1] + direction[1])

def cube_substract(coords, direction):
	return (coords[0] - direction[0], coords[1] - direction[1])

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

def getCircle(radius=1, x=0, y=0):
	for dx in range(-radius, radius+1):
		for dy in range(max(-radius, -dx-radius), min(radius, -dx+radius)+1):
			yield (dx+x, dy+y)

def mirrorCoordinate(coordinate, mirrorPoint=(0,0)):
	direction = cube_substract(mirrorPoint, coordinate)
	return cube_add(mirrorPoint, direction)
