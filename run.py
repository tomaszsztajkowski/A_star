import pygame
from time import sleep
from tile import Tile
import colors as color
import constants as c

def display(window, tiles):
	# background
	window.fill(color.EMPTY)
	rect_size = c.size*(c.t_size) + c.size + 1
	pygame.draw.rect(window, color.WALL, (c.border, c.border, rect_size, rect_size))

	# tiles
	for tile in tiles: tile.draw(window)

	pygame.display.update()

def around(center, tiles):
	xy = (center.x, center.y)
	out = []
	corners = []


	for i in ((-1, 0), (0, -1), (0, 1), (1, 0)):
		temp = (xy[0] + i[0], xy[1] + i[1])
		if not (-1 in temp or c.size in temp) and tiles[temp[1]*c.size + temp[0]].state != color.WALL:
			out.append((tiles[temp[1]*c.size + temp[0]], 10))
			corners.append(i)

	# not allowing going through connected corners
	coodinates = [] 
	for i in range(-1, 2, 2):
		for j in range(-1, 2, 2):
			if (i, 0) in corners or (0, j) in corners:
				coodinates.append((i, j))

	for i in coodinates:
		temp = (xy[0] + i[0], xy[1] + i[1])
		if not (-1 in temp or c.size in temp):
			out.append((tiles[temp[1]*c.size + temp[0]], 14))
	
	return out

def find_next(active, search, current, end):
	for tile in search:
		if tile[0].state in (color.START, color.EXPLORED, color.WALL): continue
		x_distance = abs(end.x - tile[0].x)
		y_distance = abs(end.y - tile[0].y)
		if tile[0].score_to_end == 0:
			tile[0].score_to_end = min(x_distance, y_distance) * 14 + abs(x_distance - y_distance) * 10
		new_score = tile[0].score_to_end + tile[1] + current.score - current.score_to_end
		if tile[0].score == 0 or new_score < tile[0].score: tile[0].score = new_score
		tile[0].state = color.ACTIVE
		active.add(tile[0])

def main():
	pygame.display.set_icon(pygame.image.load('icon.png'))

	# not meant to change
	tiles = [Tile(i%c.size, i//c.size) for i in range(c.size**2)]
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

				#---CAPTION---#
				if -1 not in pos and c.size not in pos:
					score = ',  sum: ' + str(tiles[pos[1]*c.size + pos[0]].score).rjust(3, '0')
					to_start = ' to start: ' + str(tiles[pos[1]*c.size + pos[0]].score - tiles[pos[1]*c.size + pos[0]].score_to_end).rjust(3, '0')
					to_end = ',  to goal: ' + str(tiles[pos[1]*c.size + pos[0]].score_to_end).rjust(3, '0')
					position = 'Coordinates: ({}, {})'.format(str(pos[0]).rjust(2, '0'), str(pos[1]).rjust(2, '0'))
					pygame.display.set_caption(position + ', Distance'+ to_start + to_end + score)
				#-------------#

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

					else: solving = True

				# erase
				elif event.key == pygame.K_ESCAPE:
					if pygame.key.get_pressed()[pygame.K_LSHIFT]:
						erase = (color.START, color.END, color.WALL)
					else: erase = (color.START, color.END)
					for tile in tiles:
						if tile.state not in erase:
							tile.state = color.EMPTY
							tile.score = tile.score_to_end = 0
					active = set()
					smallest = start
					solving = False

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
				while start not in surrounding:
					smallest.state = color.PATH
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


		#-------MOUSE-------#
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

		elif clicked.state in (color.START, color.END): shift = None

		# release safety start
		elif shift == 'start':
			shift = None
			start.state = color.EMPTY
			start = tiles[pos[1] * c.size + pos[0]]
			start.state = color.START
			smallest = start

		# release safety end
		elif shift == 'goal':
			shift = None
			end.state = color.EMPTY
			print(pos)
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

		display(window, tiles)


if __name__ == '__main__': main()
	