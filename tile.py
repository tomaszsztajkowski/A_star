import pygame
import colors as color
import constants as c

class Tile():
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.state = color.EMPTY
		self.score_to_end = 0
		self.score = 0
		self.neighbours = 0

	def draw(self, window):
		#print(self.x, self.y)
		x = c.border + 1 + c.t_size * self.x + self.x
		y = c.border + 1 + c.t_size * self.y + self.y
		rect = (x, y, c.t_size, c.t_size)
		pygame.draw.rect(window, self.state, rect)