from Matrix import Matrix
import time
matrix = Matrix()

def loop():
   
    MAX_X = 8
    MAX_Y = 16

    ball_x = 0
    ball_y = 0
    
    matrix.fill(0)

    while matrix.running:
        # Можна впливати на кульку кнопками!
        if matrix.key("LEFT") and ball_x > 0: ball_x -= 1
        if matrix.key("RIGHT") and ball_x < MAX_X-1: ball_x += 1
        if matrix.key("UP") and ball_y > 0: ball_y -= 1
        if matrix.key("DOWN") and ball_y < MAX_Y-1: ball_y += 1
        
        # Ресет на кнопку Z
        if matrix.key("Z"):
            ball_x, ball_y = 0, 0 # Повернення в центр
            
        # --- 4. Малювання ---
        matrix.fill(0)
        matrix.pixel(ball_x, ball_y, 1)
        matrix.show()
        
        # --- 5. Пауза ---
        time.sleep(0.05)

# Запуск
matrix.loop(loop)