import sys
import pygame
import numpy
from config import *
from button import Button
from timer import *

class Visualization:
    def __init__(self, dataLength, screen=win, screen_width=WIDTH, screen_height=HEIGHT,
                 x_offset=0, column_width=None, name="") -> None:
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.clock = clock

        self.x_offset = x_offset
        self.column_width = column_width if column_width is not None else screen_width
        self.name = name  # dynamic title

        self.states = numpy.zeros((dataPoints,), dtype=int)
        self.dataLength = dataLength

        self.barWidth = max(10, self.column_width // (dataPoints * 2))
        total_bar_width = dataPoints * self.barWidth
        space = self.column_width - total_bar_width
        self.gap = max(2, space // (dataPoints + 1))

        self.i = 0
        self.j = 0
        self.n = len(self.dataLength)
        self.sorted_tail = self.n
        self.done = False
        self.delay_compare = 100
        self.delay_swap = 100
        self.next_step_time = 0
        
        self.padding_bottom = 80

        self.ins_inited = False

    def bubbleSort(self):
        if self.done:
            return

        now = pygame.time.get_ticks()
        if now < self.next_step_time:
            return

        # reset state
        self.states[:] = 0
        for k in range(self.sorted_tail, self.n):
            self.states[k] = 2

        if self.i >= self.n - 1:
            self.states[:] = 2
            self.done = True
            return

        a, b = self.j, self.j + 1
        self.states[a] = self.states[b] = 1

        if self.dataLength[a] > self.dataLength[b]:
            self.dataLength[a], self.dataLength[b] = self.dataLength[b], self.dataLength[a]
            self.isSwapped = True
            self.next_step_time = now + self.delay_swap
        else:
            self.next_step_time = now + self.delay_compare

        # advance inner index
        self.j += 1
        if self.j >= self.sorted_tail - 1:
            # end of one full pass
            if not self.isSwapped:
                # no swaps at all → finished
                self.states[:] = 2
                self.done = True
                return
            self.j = 0
            self.i += 1
            self.sorted_tail = self.n - self.i
            self.isSwapped = False

    def insertionSort(self):
        if self.done:
            return

        now = pygame.time.get_ticks()
        if now < self.next_step_time:
            return

        if not getattr(self, "ins_inited", False):
            self.i = 1
            self.j = 0
            self.ins_inited = True

        if self.i >= self.n:
            self.states[:] = 2
            self.done = True
            return

        self.states[:] = 0

        if self.j < 0 or self.dataLength[self.j] <= self.dataLength[self.j + 1]:
            self.i += 1
            if self.i >= self.n:
                self.states[:] = 2
                self.done = True
                print("Insertion Sort finished:", self.dataLength.tolist())
                return
            self.j = self.i - 1
            self.next_step_time = now + self.delay_compare
            return
        
        a, b = self.j, self.j + 1          # current pair
        self.states[a] = self.states[b] = 1 # highlight ONLY this pair
        self.dataLength[a], self.dataLength[b] = self.dataLength[b], self.dataLength[a]
        self.j -= 1
        self.next_step_time = now + self.delay_swap

    def reset(self, data):
        if data is None:
            self.dataLength = numpy.random.randint(10, self.screen_height - 50, dataPoints)
        else:
            self.dataLength = numpy.array(data, dtype=int).copy()  # independent copy
        # reset sort state
        self.states = numpy.zeros((dataPoints,), dtype=int)
        self.n = len(self.dataLength)
        self.i = 0; self.j = 0
        self.sorted_tail = self.n
        self.done = False
        self.next_step_time = 0

    def draw_bars(self):
        for i in range(len(self.dataLength)):
            x = self.x_offset + self.gap * (i + 1) + self.barWidth * i
            color = WHITE if self.states[i] == 0 else (RED if self.states[i] == 1 else GREEN)
            pygame.draw.rect(
                self.screen, color,
                (x, self.screen_height - self.dataLength[i] -self.padding_bottom, self.barWidth, self.dataLength[i])
            )

    def render_step(self, random):
        match random:
            case 1:
                self.bubbleSort()
                self.name = "Bubble Sort"
            case 2:
                self.insertionSort()
                self.name = "Insertion sort"
        self.draw_bars()

    def render_title(self, font):
        # draw the title above this column
        label = font.render(f"{self.name}", True, WHITE)
        self.screen.blit(label, (self.x_offset + 10, 10))

# ---- main ----
pygame.init()
font = pygame.font.SysFont(None, 24)

base_data = numpy.random.randint(10, HEIGHT - 100, dataPoints)

left_width = WIDTH // 2
right_width = WIDTH - left_width

left_vis = Visualization(dataLength=base_data, x_offset=0, column_width=left_width)
right_vis = Visualization(dataLength=base_data, x_offset=left_width, column_width=right_width)

left_rect  = pygame.Rect(0, 0, left_width, HEIGHT - 80)          # exclude bottom padding
right_rect = pygame.Rect(left_width, 0, right_width, HEIGHT - 80)

start_button = Button( 30, HEIGHT - 55, 120, 40, "Start", font)
reset_button = Button(180, HEIGHT - 55, 120, 40, "Reset", font)

start_visualize =False
hover_side = None

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if start_button.is_clicked(event):
            start_visualize = True
            start_time = pygame.time.get_ticks()

        if reset_button.is_clicked(event):
            base_data = numpy.random.randint(10, HEIGHT - 100, dataPoints)
            left_vis.reset(base_data)
            right_vis.reset(base_data)
            start_visualize = False
            start_time = None
            elapsed_ms = 0


    win.fill(BLACK)
    pygame.draw.line(win, WHITE, (left_width, 0), (left_width, HEIGHT - 80), 2)
    pygame.draw.line(win, WHITE, (0, HEIGHT-70), (WIDTH, HEIGHT - 70), 5)

    # --- title --- 
    if start_visualize  and start_time is not None:
        left_vis.render_step(1)
        right_vis.render_step(2)
        now = pygame.time.get_ticks()
        elapsed_ms = now - start_time
        if event.type == pygame.MOUSEMOTION:
            if left_rect.collidepoint(event.pos):
                hover_side = 'left'
            elif right_rect.collidepoint(event.pos):
                hover_side = 'right'
            else:
                hover_side = None

    
    if start_visualize and hover_side == 'left':
        overlay = pygame.Surface((left_rect.width, left_rect.height), pygame.SRCALPHA)
        overlay.fill(WHITE_TRANS)  # white translucent
        win.blit(overlay, left_rect.topleft)

    elif start_visualize and hover_side == 'right':
        overlay = pygame.Surface((right_rect.width, right_rect.height), pygame.SRCALPHA)
        overlay.fill(WHITE_TRANS)
        win.blit(overlay, right_rect.topleft)

        
    left_vis.render_title(font)
    right_vis.render_title(font)

    start_button.draw_start(win)
    reset_button.draw_start(win)

    timer_text = font.render(f"Time: {format_time(elapsed_ms)} (s)", True, WHITE)
    win.blit(timer_text, (WIDTH - 140, HEIGHT - 40))  # adjust x to taste

    pygame.display.update()
    clock.tick(FPS)
