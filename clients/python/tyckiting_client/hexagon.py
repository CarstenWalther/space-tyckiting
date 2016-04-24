
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
		for _ in range(radius):
			results.add(cube)
			cube = neighbor(cube, i)
	return results

def isInField(coords, radius, center=(0,0)):
	x,y = coords
	z = -x-y
	centerX, centerY = center
	centerZ = -centerX-centerY
	return -radius <= x-centerX <= radius and \
			-radius <= y-centerY <= radius and \
			-radius <= z-centerZ <= radius

def extractValidCoordinates(coordinates, radius, center=(0,0)):
	validCoordinates = set()
	for coord in coordinates:
		if isInField(coord, radius, center):
			validCoordinates.add(coord)
	return validCoordinates

def getCircle(radius=1, x=0, y=0):
	for dx in range(-radius, radius+1):
		for dy in range(max(-radius, -dx-radius), min(radius, -dx+radius)+1):
			yield (dx+x, dy+y)

def mirrorCoordinate(coordinate, mirrorPoint=(0,0)):
	direction = cube_substract(mirrorPoint, coordinate)
	return cube_add(mirrorPoint, direction)

def distance(pos1, pos2):
	z1 = -pos1[0] - pos1[1]
	z2 = -pos2[0] - pos2[1]

	x_dist = abs(pos2[0] - pos1[0])
	y_dist = abs(pos2[1] - pos1[1])
	z_dist = abs(z2 - z1)

	dist = max(x_dist, y_dist, z_dist)

	return dist

def isStraightLine(pos1, pos2):
	dx = pos1[0] - pos2[0]
	dy = pos1[1] - pos2[1]
	dz = dx + dy
	return dx == 0 or dy == 0 or dz == 0