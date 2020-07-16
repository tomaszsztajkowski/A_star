import pygame
from time import sleep
from tile import Tile
import colors as color
import constants as c
from random import shuffle, randint

def display(window, tiles):
	# background
	window.fill(color.EMPTY)
	rect_size = c.size*(c.t_size) + c.size + 1
	pygame.draw.rect(window, color.WALL, (c.border, c.border, rect_size, rect_size))

	# tiles
	for tile in tiles: tile.draw(window)

	pygame.display.update()

def around(center, tiles, cardinal=False, allow_walls=False, bias=None):
	xy = (center.x, center.y)
	out = []
	corners = []


	for i in ((-1, 0), (0, -1), (0, 1), (1, 0)):
		temp = (xy[0] + i[0], xy[1] + i[1])
		if not (-1 in temp or c.size in temp) and (tiles[temp[1]*c.size + temp[0]].state != color.WALL or allow_walls):
			out.append((tiles[temp[1]*c.size + temp[0]], 10))
			if cardinal and i in ((-1, 0), (1, 0)) and bias == 0: out.append((tiles[temp[1]*c.size + temp[0]], 10))
			if cardinal and i in ((0, -1), (0, 1)) and bias == 1: out.append((tiles[temp[1]*c.size + temp[0]], 10))
			corners.append(i)
	if cardinal: return out

	# not allowing going through connected corners
	coodinates = [] 
	for i in range(-1, 2, 2):
		for j in range(-1, 2, 2):
			if (i, 0) in corners or (0, j) in corners:
				coodinates.append((i, j))

	for i in coodinates:
		temp = (xy[0] + i[0], xy[1] + i[1])
		if not (-1 in temp or c.size in temp):
			out.append((tiles[temp[1]*c.size + temp[0]], c.search_type))
	
	return out

def find_next(active, search, current, end):
	for tile in search:
		if tile[0].state in (color.START, color.EXPLORED, color.WALL): continue
		x_distance = abs(end.x - tile[0].x)
		y_distance = abs(end.y - tile[0].y)
		if tile[0].score_to_end == 0:
			tile[0].score_to_end = min(x_distance, y_distance) * c.search_type + abs(x_distance - y_distance) * 10
			c.calculated += 1
		new_score = tile[0].score_to_end + tile[1] + current.score - current.score_to_end
		if tile[0].score == 0 or new_score < tile[0].score: tile[0].score = new_score
		tile[0].state = color.ACTIVE
		active.add(tile[0])

def random_walk(tile, tiles, bias):
	dirs = around(tile, tiles, cardinal=True, allow_walls=True, bias=bias)
	while dirs:
		shuffle(dirs)
		peek = dirs.pop()[0]
		if peek.neighbours < 3 and peek.state == color.WALL:
			peek.state = color.EMPTY
			for a in around(peek, tiles, allow_walls=True):
				a[0].neighbours += 1
			return peek

def main():
	pygame.display.set_icon(pygame.image.load('icon.png'))

	# not meant to change
	tiles = [Tile(i%c.size, i//c.size) for i in range(c.size**2)]
	l = list(map(list, zip(*[[tiles[i*c.size + j] for j in range(c.size)] for i in range(c.size)])))
	tiles_t = []
	for sublist in l:
	    for item in sublist:
	        tiles_t.append(item)
	window = pygame.display.set_mode((c.win_size_x, c.win_size_y))

	# meant to change
	pos = (0, 0)
	start = tiles[0]
	start.state = color.START
	end = tiles[c.size ** 2 - 1]
	end.state = color.END
	solving = False
	active = set()
	smallest = start
	wheel = False
	shift = None
	c.calculated = 0
	length = 0
	peek = None
	generation = False
	bias = randint(0, 1)

	# main loop
	running = True
	while running:
		#-------EVENTS-------#
		for event in pygame.event.get():

			# quit
			if event.type == pygame.QUIT:
				running = False
				break

			# get mouse coordinates
			elif event.type == pygame.MOUSEMOTION:
				pos = pygame.mouse.get_pos()
				pos = [((pos[0] - c.border) // (c.t_size+1)), ((pos[1] - c.border) // (c.t_size+1))]
				if pos[0] < 0: pos[0] = 0
				if pos[1] < 0: pos[1] = 0
				if pos[0] >= c.size: pos[0] = c.size - 1
				if pos[1] >= c.size: pos[1] = c.size - 1
				

			elif event.type == pygame.KEYDOWN:

				# solving
				if event.key == pygame.K_SPACE:
					if solving: solving = False

					elif active and not smallest:
						for tile in tiles:
							if tile.state not in (color.START, color.END, color.WALL):
								tile.state = color.EMPTY
								tile.score = tile.score_to_end = 0
						active = set()
						smallest = start
						c.calculated = 0
						length = 0

					else:
						solving = True
						smallest = start
						generation = False

				# erase
				elif event.key == pygame.K_ESCAPE:
					if pygame.key.get_pressed()[pygame.K_LSHIFT]:
						erase = (color.START, color.END, color.WALL)
					else:
						erase = (color.START, color.END)
						peek = None
					for tile in tiles:
						if tile.state not in erase:
							tile.state = color.EMPTY
							tile.score = tile.score_to_end = 0
					active = set()
					smallest = start
					solving = False
					c.calculated = 0
					length = 0
					generation = False


				# solving type
				elif event.key == pygame.K_1:
					c.search_type = c.manhattan if c.search_type == c.euclidean else c.euclidean
					print(c.search_type)

				# maze generator
				elif event.key == pygame.K_m and not solving:
					if generation:
						generation = False
						continue
					if peek:
						generation = True
						continue
					for i in tiles:
						if i not in (start, end): i.state = color.WALL
						i.neighbours = 0
					for a in around(tiles[0], tiles): a[0].neighbours += 1

					generation = True	
					peek = tiles[randint(0, len(tiles) - 1)]
					

			elif event.type == pygame.MOUSEBUTTONDOWN and not (active and not smallest):
				if event.button == 4:
					solving = True
					wheel = True

		#-------SOLVING-------#
		if solving:
			if smallest != start: smallest.state = color.EXPLORED

			# after reaching the end
			surrounding = [tile[0] for tile in around(smallest, tiles)]
			if end in surrounding:
				solving = False
				wheel = False

				# the exact shortest path
				while start not in surrounding and active:
					smallest.state = color.PATH
					length += 1
					surrounding = [tile[0] for tile in around(smallest, tiles)]
					for tile in surrounding:
						if tile.state != color.EXPLORED: continue
						if smallest.state == color.PATH or (tile.score - tile.score_to_end) < (smallest.score - smallest.score_to_end):
							smallest = tile
					display(window, tiles)
				smallest = None
				continue

			# next tile with the smallest value
			find_next(active, around(smallest, tiles), smallest, end)

			for i, tile in enumerate(list(active)):
				if i == 0 or tile.score < smallest.score: smallest = tile
				if tile.score == smallest.score and tile.score_to_end < smallest.score_to_end: smallest = tile
			try:
				active.remove(smallest)
			except KeyError:
				solving = False
				wheel = False

			if wheel:
				solving = False
				wheel = False

		#-----GENERATION------#
		if generation:
			if peek:
				peek = random_walk(peek, tiles, bias)
				if randint(0, c.size // 10) == 0:
					bias = 0 if bias == 1 else 1
			if not peek:
				index = 0
				search = (tiles, tiles[::-1], tiles_t, tiles_t[::-1])[randint(0, 3)]
				while not peek:
					if search[index].state == color.EMPTY:
						for a in around(search[index], search, cardinal=True, allow_walls=True):
							if a[0].neighbours < 3 and a[0].state == color.WALL:
								peek = search[index]
								break
					index += 1
					if index == len(search):
						generation = False
						break
				bias = randint(0, 1)


		#--------MOUSE--------#
		mouse_pressed = pygame.mouse.get_pressed()
		clicked = tiles[pos[1] * c.size + pos[0]]
		if 1 in mouse_pressed:
			clicked = tiles[pos[1] * c.size + pos[0]]

			# forbidding overriting important tiles
			if clicked.state in (color.ACTIVE, color.PATH, color.EXPLORED): pass

			# grab and drag start
			elif mouse_pressed[0] and clicked.state != color.END and (shift == 'start' or (shift == None and clicked.state == color.START)):
				shift = 'start'
				start.state = color.EMPTY
				start = clicked
				start.state = color.START
				smallest = start

			# grab and drag goal
			elif mouse_pressed[0] and clicked.state != color.START and (shift == 'goal' or (shift == None and clicked.state == color.END)):
				shift = 'goal'
				end.state = color.EMPTY
				end = tiles[pos[1] * c.size + pos[0]]
				end.state = color.END

			# wall or start
			elif mouse_pressed[0] and clicked.state not in (color.START, color.END):
				if pygame.key.get_pressed()[pygame.K_LSHIFT]:
					start.state = color.EMPTY
					start = clicked
					start.state = color.START
					smallest = start
				else:
					clicked.state = color.WALL

			# empty or end
			elif mouse_pressed[2] and clicked.state not in (color.START, color.END):
				if pygame.key.get_pressed()[pygame.K_LSHIFT]:
					end.state = color.EMPTY
					end = tiles[pos[1] * c.size + pos[0]]
					end.state = color.END
				else:
					clicked.state = color.EMPTY

		# release safety
		elif clicked.state in (color.START, color.END): shift = None

		# release delay start
		elif shift == 'start':
			shift = None
			start.state = color.EMPTY
			start = tiles[pos[1] * c.size + pos[0]]
			start.state = color.START
			smallest = start

		# release delay end
		elif shift == 'goal':
			shift = None
			end.state = color.EMPTY
			end = tiles[pos[1] * c.size + pos[0]]
			end.state = color.END

		# active cells purge
		if -1 not in pos and active and shift:
			erase = (color.START, color.END, color.WALL)
			for tile in tiles:
				if tile.state not in erase:
					tile.state = color.EMPTY
					tile.score = tile.score_to_end = 0
			active = set()
			smallest = start
			solving = False
			c.calculated = 0
			length = 0

		display(window, tiles)

		#---CAPTION---#
		score = ',  sum: ' + str(tiles[pos[1]*c.size + pos[0]].score).rjust(4, '0')
		to_start = ' to start: ' + str(tiles[pos[1]*c.size + pos[0]].score - tiles[pos[1]*c.size + pos[0]].score_to_end).rjust(4, '0')
		to_end = ',  to goal: ' + str(tiles[pos[1]*c.size + pos[0]].score_to_end).rjust(4, '0')
		position = '' # 'Coordinates: ({}, {})'.format(str(pos[0]).rjust(2, '0'), str(pos[1]).rjust(2, '0'))
		mode = 'Euclidean, ' if c.search_type == c.euclidean else 'Manhattan, '
		calc = ', Active: {}'.format(c.calculated)
		pygame.display.set_caption(mode + position + ', Distance'+ to_start + to_end + score + calc + ' Length: {}'.format(length))
		#-------------#		


if __name__ == '__main__': main()
	