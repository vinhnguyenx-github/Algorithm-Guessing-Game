import pygame
import time

def partition(array, low, high, draw_func, speed):
    pivot = array[high]
    i = low - 1

    for j in range(low, high):
        if array[j] <= pivot:
            i += 1
            array[i], array[j] = array[j], array[i]
            draw_func(array, {i: "green", j: "red"})
            time.sleep(speed)

    array[i + 1], array[high] = array[high], array[i + 1]
    draw_func(array, {i + 1: "green", high: "red"})
    time.sleep(speed)
    return i + 1

def quick_sort(array, low, high, draw_func, speed):
    if low < high:
        pi = partition(array, low, high, draw_func, speed)
        quick_sort(array, low, pi - 1, draw_func, speed)
        quick_sort(array, pi + 1, high, draw_func, speed)
