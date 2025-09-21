import os, sys
os.environ["SDL_VIDEODRIVER"] = "dummy"   

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import pygame
import numpy as np
import pytest
from visualization import Visualization


# ---------- Helpers ----------
class Ticker:
    """fake clock for pygame.time.get_ticks()."""
    def __init__(self, step=1):
        self.t = 0
        self.step = step
    def __call__(self):
        self.t += self.step
        return self.t

def make_vis(arr, w=640, h=480):
    pygame.init()
    surf = pygame.Surface((w, h))
    return Visualization(
        dataLength=np.array(arr, dtype=int),
        screen=surf,
        screen_width=w,
        screen_height=h,
        x_offset=0,
        column_width=w,
        name=""
    )

def run_to_completion(vis, algo_id, max_steps=20000):
    # eliminate waiting so tests run fast
    vis.delay_compare = 0
    vis.delay_swap = 0
    steps = 0
    while not vis.done and steps < max_steps:
        vis.render_step(algo_id)
        steps += 1
    assert steps < max_steps, "algorithm did not terminate"


# ---------- Auto-fixture to make time deterministic ----------
@pytest.fixture(autouse=True)
def fake_ticks(monkeypatch):
    tick = Ticker(step=1)
    monkeypatch.setattr(pygame.time, "get_ticks", tick)
    return tick

# ---------- Correctness across all algorithms ----------
@pytest.mark.parametrize("algo_id", [1, 2, 3, 4, 5])  # bubble, insertion, quick, merge, selection
@pytest.mark.parametrize("arr", [
    [], [1], [2, 1], [3, 1, 2], [5, 1, 4, 2, 8, 5, 3], [2, 2, 2, 2],
    list(range(10, 0, -1)), [7, 3, 5, 3, 7, 1, 0, 9]
])
def test_algorithms_sort_correctly(algo_id, arr):
    vis = make_vis(arr)
    run_to_completion(vis, algo_id)
    assert list(vis.dataLength) == sorted(arr)
    assert vis.done is True
    if len(arr) > 0:
        # all bars marked sorted at the end
        assert set(vis.states.tolist()) == {2}


# ---------- Test each algo ----------
def test_quicksort_internal_state_drains():
    vis = make_vis([9, 1, 8, 3, 7, 2, 6, 4, 5])
    run_to_completion(vis, 3)  # quick sort
    if hasattr(vis, "quick_tasks"):
        assert vis.quick_tasks is None or vis.quick_tasks == []
    if hasattr(vis, "quick_in_progress"):
        assert vis.quick_in_progress is None

def test_mergesort_jobs_drain():
    vis = make_vis([5, 4, 3, 2, 1])
    run_to_completion(vis, 4)  # merge sort
    if hasattr(vis, "merge_tasks"):
        assert vis.merge_tasks == []

def test_selectionsort_indices_stay_in_bounds():
    vis = make_vis([3, 1, 2, 0])
    run_to_completion(vis, 5)  # selection sort
    # array remains same length and sorted
    assert len(vis.dataLength) == 4
    assert list(vis.dataLength) == [0, 1, 2, 3]


def test_speedup_changes_delays():
    vis = make_vis([3, 2, 1])
    old = (vis.delay_compare, vis.delay_swap)
    vis.speedUp()
    assert (vis.delay_compare, vis.delay_swap) == (10, 10)
    assert (vis.delay_compare, vis.delay_swap) != old


def test_reset():
    vis = make_vis([4, 1, 3, 2])
    run_to_completion(vis, 2)  # insertion
    vis.reset([10, 9, 8])
    assert list(vis.dataLength) == [10, 9, 8]
    assert vis.n == 3
    assert vis.done is False
    # common flags reinitialized
    assert vis.i == 0 and vis.j == 0
    assert vis.sorted_tail == vis.n
    assert getattr(vis, "quick_tasks") is None
    assert getattr(vis, "quick_in_progress") is None
    assert vis.merge_inited is False
    assert vis.sel_inited is False