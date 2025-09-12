import os
import pygame
import numpy
from config import *
from button import Button
from timer import *
import re 
import glob
import random

os.makedirs("data", exist_ok=True)

def next_attempt_index():
    nums = []
    for p in glob.glob("data/attempt*.txt"):
        m = re.search(r"attempt(\d+)\.txt$", p)
        if m:
            nums.append(int(m.group(1)))
    return (max(nums) + 1) if nums else 1

ATTEMPT_IDX = next_attempt_index()                  # e.g., 1, 2, 3, ...
SESSION_FILE = f"data/attempt{ATTEMPT_IDX}.txt"     

class Visualization:
    def __init__(self, dataLength, screen=win, screen_width=WIDTH, screen_height=HEIGHT,
             x_offset=0, column_width=None, name="") -> None:
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.clock = clock

        self.x_offset = x_offset
        self.column_width = column_width if column_width is not None else screen_width
        self.name = name

        # data & layout
        self.dataLength = numpy.array(dataLength, dtype=int).copy()
        self.n = len(self.dataLength)
        self.states = numpy.zeros((self.n,), dtype=int)  # match data length

        self.barWidth = max(10, self.column_width // (self.n * 2))
        total_bar_width = self.n * self.barWidth
        space = self.column_width - total_bar_width
        self.gap = max(2, space // (self.n + 1))

        # sorting state
        self.i = 0
        self.j = 0
        self.sorted_tail = self.n
        self.done = False
        self.delay_compare = 200
        self.delay_swap = 200
        self.next_step_time = 0
        self.padding_bottom = 80

        # algo-specific flags
        self.isSwapped = False       # bubble early-exit flag (reset each pass)
        self.ins_inited = False      # insertion one-time init
        self.finished_at = None      # pygame ticks when finished

    # --- Bubble Sort (adjacent, early-exit) ---
    def bubbleSort(self):
        if self.done:
            return
        now = pygame.time.get_ticks()
        if now < self.next_step_time:
            return

        # mark sorted tail
        self.states[:] = 0
        for k in range(self.sorted_tail, self.n):
            self.states[k] = 2

        # finished?
        if self.i >= self.n - 1:
            self.states[:] = 2
            self.done = True
            if self.finished_at is None:
                self.finished_at = now
            return

        # start-of-pass hygiene (optional)
        if self.j == 0:
            self.isSwapped = False

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
            if not self.isSwapped:
                self.states[:] = 2
                self.done = True
                if self.finished_at is None:
                    self.finished_at = now
                return
            self.j = 0
            self.i += 1
            self.sorted_tail = self.n - self.i
            # self.isSwapped reset happens next pass (or here if you prefer)

    # --- Insertion Sort (pair-only highlight; all-green only at end) ---
    def insertionSort(self):
        if self.done:
            return
        now = pygame.time.get_ticks()
        if now < self.next_step_time:
            return

        if not self.ins_inited:
            self.i = 1
            self.j = 0
            self.ins_inited = True

        if self.i >= self.n:
            self.states[:] = 2
            self.done = True
            if self.finished_at is None:
                self.finished_at = now
            return

        self.states[:] = 0  # only highlight current pair

        # key placed? advance to next i
        if self.j < 0 or self.dataLength[self.j] <= self.dataLength[self.j + 1]:
            self.i += 1
            if self.i >= self.n:
                self.states[:] = 2
                self.done = True
                if self.finished_at is None:
                    self.finished_at = now
                return
            self.j = self.i - 1
            self.next_step_time = now + self.delay_compare
            return

        # compare/swap current adjacent pair
        a, b = self.j, self.j + 1
        self.states[a] = self.states[b] = 1
        self.dataLength[a], self.dataLength[b] = self.dataLength[b], self.dataLength[a]
        self.j -= 1
        self.next_step_time = now + self.delay_swap


    # --- Quick Sort Algorithm --- 
    def quickSort(self):
        pass

    # --- Merge Sort Algorithm ---
    def mergeSort(self):
        pass
    
    # --- Reset the data --- 
    def reset(self, data):
        self.dataLength = numpy.array(data, dtype=int).copy()
        self.n = len(self.dataLength)
        self.states = numpy.zeros((self.n,), dtype=int)
        self.i = 0; self.j = 0
        self.sorted_tail = self.n
        self.done = False
        self.next_step_time = 0
        self.isSwapped = False
        self.ins_inited = False
        self.finished_at = None
        self.delay_swap = 200
        self.delay_compare = 200

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
            case 3:
                self.quickSort()
                self.name = "Quick sort"
            case 4:
                self.mergeSort()
                self.name = "Merge sort"
        self.draw_bars()

    def render_title(self, font):
        # draw the title above this column
        label = font.render(f"{self.name}", True, WHITE)
        self.screen.blit(label, (self.x_offset + 10, 10))

    def speedUp(self):
        self.delay_compare = 10
        self.delay_swap = 10

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

left_algo, right_algo = random.sample(algorithms, 2)

start_visualize =False
hover_side = None

while running:
    # ---------------- EVENTS ----------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Start round
        if start_button.is_clicked(event):
            start_visualize = True
            start_time = pygame.time.get_ticks()
            elapsed_ms = 0
            timer_running = True
            reaction_logged = False
            prediction = None
            result_printed = False

        # Reset round
        if reset_button.is_clicked(event):
            base_data = numpy.random.randint(10, HEIGHT - 100, dataPoints)
            left_vis.reset(base_data)
            right_vis.reset(base_data)
            start_visualize = False
            start_time = None
            elapsed_ms = 0
            timer_running = False
            reaction_logged = False
            prediction = None
            result_printed = False
            left_algo, right_algo = random.sample(algorithms, 2)
            hover_side = None
            result_text = ""

        # Player click to choose
        if start_visualize and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if left_rect.collidepoint(event.pos) or right_rect.collidepoint(event.pos):
                if prediction is None:
                    prediction = 'left' if left_rect.collidepoint(event.pos) else 'right'
                    print(f"Picked: {prediction}")

                left_vis.speedUp()
                right_vis.speedUp()

                if timer_running and not reaction_logged and start_time is not None:
                    os.makedirs("data", exist_ok=True)
                    click_s = (pygame.time.get_ticks() - start_time) / 1000.0
                    with open(SESSION_FILE, "a", encoding="utf-8") as f:
                        f.write(f"{click_s:.3f}\n")
                    attempt_idx += 1
                    reaction_logged = True
                    timer_running = False

    # ---------------- CLEAR ----------------
    win.fill(BLACK)
    pygame.draw.line(win, WHITE, (left_width, 0), (left_width, HEIGHT - 80), 2)
    pygame.draw.line(win, WHITE, (0, HEIGHT - 70), (WIDTH, HEIGHT - 70), 5)

    # ---------------- UPDATE / DRAW ----------------
    if start_visualize and start_time is not None:
        if timer_running:
            elapsed_ms = pygame.time.get_ticks() - start_time

        left_vis.render_step(left_algo)    # Bubble
        right_vis.render_step(right_algo)   # Insertion

        # decide winner
        if prediction is not None and not result_printed:
            lf = getattr(left_vis, "finished_at", None)
            rf = getattr(right_vis, "finished_at", None)
            winner = None
            if lf is not None and rf is not None:
                winner = 'left' if lf < rf else ('right' if rf < lf else 'tie')
            elif lf is not None:
                winner = 'left'
            elif rf is not None:
                winner = 'right'
            if winner is not None:
                if winner == 'tie':
                    result_text = "Result: Tie"
                else:
                    result_text = "Correct!" if prediction == winner else f"Incorrect — {winner} finished first"
                result_printed = True

    else:
        # before Start: do NOT draw bars → columns remain black
        pass

    # ---------------- HOVER (only when running) ----------------
    if start_visualize:
        mx, my = pygame.mouse.get_pos()
        if left_rect.collidepoint((mx, my)):
            hover_side = 'left'
        elif right_rect.collidepoint((mx, my)):
            hover_side = 'right'
        else:
            hover_side = None

        if hover_side == 'left':
            overlay = pygame.Surface((left_rect.width, left_rect.height), pygame.SRCALPHA)
            overlay.fill(WHITE_TRANS)
            win.blit(overlay, left_rect.topleft)
        elif hover_side == 'right':
            overlay = pygame.Surface((right_rect.width, right_rect.height), pygame.SRCALPHA)
            overlay.fill(WHITE_TRANS)
            win.blit(overlay, right_rect.topleft)

    # ---------------- UI ----------------
    left_vis.render_title(font)
    right_vis.render_title(font)
    start_button.draw_start(win)
    reset_button.draw_start(win)

    timer_text = font.render(f"{format_time(elapsed_ms)} (s)", True, WHITE)
    win.blit(timer_text, (WIDTH - 160, HEIGHT - 40))

    if result_text:
        result_render = font.render(result_text, True, WHITE)
        win.blit(result_render, (WIDTH // 2 - result_render.get_width() // 2, HEIGHT - 40))


    pygame.display.update()
    clock.tick(FPS)



