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
	for i in ((-1, -1), (1, 1), (-1, 1), (1, -1)):
		temp = (xy[0] + i[0], xy[1] + i[1])
		if not (-1 in temp or c.size in temp):
			out.append((tiles[temp[1]*c.size + temp[0]], 14))
	for i in ((-1, 0), (1, 0), (0, -1), (0, 1)):
		temp = (xy[0] + i[0], xy[1] + i[1])
		if not (-1 in temp or c.size in temp):
			out.append((tiles[temp[1]*c.size + temp[0]], 10))
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
		# print(tile[0].x, tile[0].y, tile[0].score_to_end, tile[0].score)

def main():

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
				pos = (((pos[0] - c.border) // (c.t_size+1)), ((pos[1] - c.border) // (c.t_size+1)))
				if -1 not in pos and c.size not in pos:
					score = ' ' + str(tiles[pos[1]*c.size + pos[0]].score)
					to_start = ' ' + str(tiles[pos[1]*c.size + pos[0]].score - tiles[pos[1]*c.size + pos[0]].score_to_end)
					to_end = ' ' + str(tiles[pos[1]*c.size + pos[0]].score_to_end)
					pygame.display.set_caption(str(pos) + to_start + to_end + score)

			elif event.type == pygame.KEYDOWN:

				# solving
				if event.key == pygame.K_SPACE:
					if solving: solving = False

					elif active:
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

		#-------SOLVING-------#
		if solving:
			if smallest != start: smallest.state = color.EXPLORED

			# after reaching the end
			surrounding = [tile[0] for tile in around(smallest, tiles)]
			if end in surrounding:
				solving = False

				# the exact shortest path
				while start not in surrounding:
					smallest.state = color.PATH
					surrounding = [tile[0] for tile in around(smallest, tiles)]
					for tile in surrounding:
						if tile.state != color.EXPLORED: continue
						if smallest.state == color.PATH or (tile.score - tile.score_to_end) < (smallest.score - smallest.score_to_end):
							smallest = tile
					display(window, tiles)
				continue

			# next tile with the smallest value
			find_next(active, around(smallest, tiles), smallest, end)
			for i, tile in enumerate(list(active)):
				if i == 0 or tile.score < smallest.score: smallest = tile
				if tile.score == smallest.score and tile.score_to_end < smallest.score_to_end: smallest = tile
			try:
				active.remove(smallest)
			except KeyError:
				soling = False

			# solving = False



		#-------MOUSE-------#
		mouse_pressed = pygame.mouse.get_pressed()
		if 1 in mouse_pressed:
			clicked = tiles[pos[1] * c.size + pos[0]]
			if clicked.state in (color.END, color.START, color.ACTIVE, color.PATH, color.EXPLORED): pass
			elif mouse_pressed[0] and clicked.state not in (color.START, color.END):
				
				if pygame.key.get_pressed()[pygame.K_LSHIFT]:
					start.state = color.EMPTY
					start = clicked
					start.state = color.START
					smallest = start
				else:
					clicked.state = color.WALL

			elif mouse_pressed[2] and clicked.state not in (color.START, color.END):
				if pygame.key.get_pressed()[pygame.K_LSHIFT]:
					end.state = color.EMPTY
					end = tiles[pos[1] * c.size + pos[0]]
					end.state = color.END
				else:
					clicked.state = color.EMPTY



		display(window, tiles)


if __name__ == '__main__': main()
	