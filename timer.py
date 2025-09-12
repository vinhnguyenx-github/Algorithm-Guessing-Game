def format_time(ms):
    seconds = ms // 1000
    millis  = ms % 1000
    return f"{seconds:02d}.{millis:03d}"

start_time = None       
elapsed_ms = 0           
attempt_idx = 1
timer_running = False
reaction_logged = False