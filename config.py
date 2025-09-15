import pygame

WIDTH = 1200
HEIGHT = 680
win = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
running = True 

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (34, 255, 0)
WHITE_TRANS = (255, 255, 255, 40)

FPS = 60

dataPoints = 20

SPEED_FACTOR = 0.35

attempt_line_id = 1        # increments each round in this session
pending_time_s = None      # store click time until result is known
prediction = None
result_text = ""
result_printed = False

algorithms = [1, 2, 4, 5]