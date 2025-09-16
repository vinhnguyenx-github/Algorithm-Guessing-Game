import os
import pygame
import numpy
import re 
import glob
import random
import csv
from config import *
from timer import *
from button import Button


os.makedirs("data", exist_ok=True)

def next_attempt_index():
    nums = []
    for p in glob.glob("data/attempt*.csv"):
        m = re.search(r"attempt(\d+)\.csv$", p)
        if m:
            nums.append(int(m.group(1)))
    return (max(nums) + 1) if nums else 1

ATTEMPT_IDX = next_attempt_index()
SESSION_FILE = f"data/attempt{ATTEMPT_IDX}.csv"

# Create headers if this is a new file 
if not os.path.exists(SESSION_FILE):
    with open(SESSION_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "time", "result"])  # columns     

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
        self.merge_inited = False    # merge one-time init
        self.finished_at = None      # pygame ticks when finished
        self.sel_inited = False      # selection one-time init
        self.sel_min_idx = 0         # min flag 
        self.quick_tasks = None
        self.quick_in_progress = None


    # --- Bubble Sort  ---
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

    # --- Insertion Sort  ---
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
       # --- Quick Sort Algorithm --- 
    def quickSort(self):
        if self.done:
            return

        now = pygame.time.get_ticks()
        if now < self.next_step_time:
            return

        # one-time setup: use a simple stack of (low, high) tasks
        if not hasattr(self, "quick_tasks") or self.quick_tasks is None:
            self.quick_tasks = [(0, self.n - 1)]
            self.quick_in_progress = None

        # if no tasks and nothing in progress -> finished
        if not self.quick_tasks and self.quick_in_progress is None:
            self.states[:] = 2
            self.done = True
            if self.finished_at is None:
                self.finished_at = now
            return

        # start a new partition task if none in progress
        if self.quick_in_progress is None:
            # pop next range
            low, high = self.quick_tasks.pop()
            # if trivial range, mark it sorted and continue next frame
            if low >= high:
                # single element or empty
                if 0 <= low < self.n:
                    self.states[low] = 2
                return
            pivot = high
            i = low - 1
            j = low
            self.quick_in_progress = [low, high, pivot, i, j]

        # unpack current partition state
        low, high, pivot, i, j = self.quick_in_progress

        # visualization highlights
        self.states[:] = 0
        if 0 <= pivot < self.n:
            self.states[pivot] = 1
        if low <= j < self.n:
            self.states[j] = 1

        # walk j from low..high-1 comparing to pivot
        if j <= high - 1:
            if self.dataLength[j] <= self.dataLength[pivot]:
                i += 1
                # swap into place
                self.dataLength[i], self.dataLength[j] = self.dataLength[j], self.dataLength[i]
                self.next_step_time = now + self.delay_swap
            else:
                self.next_step_time = now + self.delay_compare
            j += 1
            self.quick_in_progress = [low, high, pivot, i, j]
            return
        else:
            # put pivot into final place at i+1
            pivot_final = i + 1
            self.dataLength[pivot_final], self.dataLength[pivot] = \
                self.dataLength[pivot], self.dataLength[pivot_final]

            # mark pivot_final as sorted
            if 0 <= pivot_final < self.n:
                self.states[pivot_final] = 2

            # push subranges (right and left). push larger first or either order is fine.
            # We'll push right then left so left is processed next (LIFO stack).
            if pivot_final + 1 < high:
                self.quick_tasks.append((pivot_final + 1, high))
            if low < pivot_final - 1:
                self.quick_tasks.append((low, pivot_final - 1))

            # done with this partition
            self.quick_in_progress = None
            self.next_step_time = now + self.delay_swap

            # if no more tasks, mark complete in next frame
            if not self.quick_tasks:
                self.states[:] = 2
                self.done = True
                if self.finished_at is None:
                    self.finished_at = now


    # --- Merge Sort Algorithm ---
    def mergeSort(self):
        if self.done:
            return
        now = pygame.time.get_ticks()
        if now < self.next_step_time:
            return

        # one-time setup (first frame)
        if not self.merge_inited:
            if not hasattr(self, "merge_tasks"):
                self.merge_tasks = []
            if not hasattr(self, "merge_buffer"):
                self.merge_buffer = None

            # generate all merge jobs for progressively larger block sizes (bottom-up)
            size = 1
            while size < self.n:
                for left in range(0, self.n, 2*size):
                    mid = min(left + size - 1, self.n - 1)
                    right = min(left + 2*size - 1, self.n - 1)
                    if mid < right:
                        self.merge_tasks.append((left, mid, right))
                size *= 2
            self.merge_inited = True

        # if no jobs, mark as complete
        if not self.merge_tasks:
            self.states[:] = 2
            self.done = True
            if self.finished_at is None:
                self.finished_at = now
            return

        # init buffer for current merge job if not already active
        if self.merge_buffer is None:
            l, m, r = self.merge_tasks[0]
            self.merge_buffer = (l, m, r, l, m+1, [])

        # unpack state for ongoing merge
        l, m, r, i, j, merged = self.merge_buffer

        # elements being compared for visualization
        self.states[:] = 0
        if i <= m and (j > r or self.dataLength[i] <= self.dataLength[j]):
            merged.append(self.dataLength[i])
            self.states[i] = 1
            i += 1
        elif j <= r:
            merged.append(self.dataLength[j])
            self.states[j] = 1
            j += 1

        # if both halves finished, add merged block back to array
        if i > m and j > r:
            for k, val in enumerate(merged):
                self.dataLength[l + k] = val
            self.merge_tasks.pop(0)
            self.merge_buffer = None
        else:
            # otherwise continue next frame
            self.merge_buffer = (l, m, r, i, j, merged)

        # frames delay
        self.next_step_time = now + self.delay_swap
        
    # --- selection sort ---   
    def selectionSort(self):
        if self.done:
            return
        now = pygame.time.get_ticks()
        if now < self.next_step_time:
            return

        # one-time init
        if not self.sel_inited:
            self.i = 0
            self.j = 1
            self.sel_min_idx = 0
            self.sel_inited = True
            
        if self.i >= self.n - 1:
            self.states[:] = 2
            self.done = True
            if self.finished_at is None:
                self.finished_at = now
            return

        self.states[:] = 0
        if self.i > 0:
            self.states[:self.i] = 2

        # end of scan → swap min into position i
        if self.j >= self.n:
            if self.sel_min_idx != self.i:
                self.dataLength[self.i], self.dataLength[self.sel_min_idx] = \
                    self.dataLength[self.sel_min_idx], self.dataLength[self.i]
                # highlight swap pair
                self.states[self.i] = self.states[self.sel_min_idx] = 1
                self.i += 1
                self.j = self.i + 1
                self.sel_min_idx = self.i
                self.next_step_time = now + self.delay_swap
                return
            else:
                # no swap needed
                self.i += 1
                self.j = self.i + 1
                self.sel_min_idx = self.i
                self.next_step_time = now + self.delay_compare
                return

        # compare a[j] with current min
        # highlight current j and current min
        self.states[self.sel_min_idx] = 1
        self.states[self.j] = 1

        if self.dataLength[self.j] < self.dataLength[self.sel_min_idx]:
            self.sel_min_idx = self.j  # new min found

        self.j += 1
        self.next_step_time = now + self.delay_compare


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
        self.merge_inited = False
        self.merge_tasks = []
        self.merge_buffer = None
        self.sel_inited = False
        self.sel_min_idx = 0
        self.quick_tasks = None
        self.quick_in_progress = None


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
            case 5:
                self.selectionSort()
                self.name = "Selection sort"
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
            result_text = ""
            result_printed = False
            pending_time_s = None
            # randomize algorithms per round (assumes `algorithms` list exists)
            left_algo, right_algo = random.sample(algorithms, 2)

        # Reset round (new shared data)
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
            result_text = ""
            result_printed = False
            pending_time_s = None
            hover_side = None

        # First click inside a column → choose, speed up, capture time, freeze timer
        if start_visualize and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if left_rect.collidepoint(event.pos) or right_rect.collidepoint(event.pos):
                if prediction is None:
                    prediction = 'left' if left_rect.collidepoint(event.pos) else 'right'
                # speed up both
                left_vis.speedUp()
                right_vis.speedUp()
                
                # capture reaction time once; freeze timer
                if timer_running and not reaction_logged and start_time is not None:
                    pending_time_s = (pygame.time.get_ticks() - start_time) / 1000.0
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

        left_vis.render_step(left_algo)
        right_vis.render_step(right_algo)

        # decide winner and set on-screen result + append CSV row once
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
                # append CSV row: id,time,result  (pending_time_s is reaction time at click)
                if pending_time_s is not None:
                    with open(SESSION_FILE, "a", newline="", encoding="utf-8") as f:
                        writer = csv.writer(f)
                        writer.writerow([attempt_line_id, f"{pending_time_s:.3f}", "Correct" if result_text.startswith("Correct") else ("Tie" if winner == "tie" else "Incorrect")])
                    attempt_line_id += 1
                    pending_time_s = None
                result_printed = True
    else:
        # keep columns black until Start
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