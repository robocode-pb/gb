import tkinter as tk
import time
import threading
import random
import sys

# ==========================================
# 1. ЕМУЛЯТОР ЗАЛІЗА (GameBoy Class)
# ==========================================
class GameBoyEmulator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("RP2040 GameBoy Emulator")
        self.root.geometry("420x750")
        self.root.configure(bg="#2b2b2b")
        
        # --- Налаштування екрану ---
        self.rows = 16
        self.cols = 8
        self.buffer = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.led_objects = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        
        self.btn_state = {"UP": False, "DOWN": False, "LEFT": False, "RIGHT": False, "Z": False, "X": False}
        self.gui_buttons = {}
        self.running = True

        self._build_ui()
        self._bind_keys()
        
        # Обробка закриття вікна
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):
        # Головний фрейм
        main_frame = tk.Frame(self.root, bg="#2b2b2b")
        main_frame.pack(pady=20)

        # 1. Екран матриці
        self.canvas = tk.Canvas(main_frame, width=self.cols*25, height=self.rows*25, bg="black", highlightthickness=0)
        self.canvas.pack(pady=10)
        
        # Малюємо сітку діодів
        for r in range(self.rows):
            for c in range(self.cols):
                x1, y1 = c * 25 + 4, r * 25 + 4
                self.led_objects[r][c] = self.canvas.create_oval(x1, y1, x1+22, y1+22, fill="#333", outline="#222")

        # 2. Зумер
        self.buzzer_canvas = tk.Canvas(main_frame, width=40, height=40, bg="#2b2b2b", highlightthickness=0)
        self.buzzer_canvas.pack(anchor="w", padx=20)
        self.buzzer_id = self.buzzer_canvas.create_oval(5, 5, 35, 35, fill="#111", outline="gray", width=2)
        tk.Label(main_frame, text="Buzzer", bg="#2b2b2b", fg="#aaa", font=("Arial", 8)).pack(anchor="w", padx=20)

        # 3. Кнопки
        controls = tk.Frame(main_frame, bg="#2b2b2b")
        controls.pack(pady=30)

        # Хрестовина
        dpad = tk.Frame(controls, bg="#2b2b2b")
        dpad.grid(row=0, column=0, padx=20)
        self._add_btn(dpad, "▲", "UP", 0, 1)
        self._add_btn(dpad, "◀", "LEFT", 1, 0)
        self._add_btn(dpad, "▶", "RIGHT", 1, 2)
        self._add_btn(dpad, "▼", "DOWN", 2, 1)

        # Дії (Z/X)
        actions = tk.Frame(controls, bg="#2b2b2b")
        actions.grid(row=0, column=1, padx=20)
        self._add_btn(actions, "X", "X", 0, 1, color="#8b0000") # Верхня
        self._add_btn(actions, "Z", "Z", 1, 0, color="#8b0000") # Нижня

    def _add_btn(self, parent, text, name, r, c, color="#444"):
        btn = tk.Button(parent, text=text, width=5, height=2, bg=color, fg="white", relief="raised", font=("Arial", 10, "bold"))
        btn.grid(row=r, column=c, padx=3, pady=3)
        btn.orig_color = color
        self.gui_buttons[name] = btn
        
        btn.bind('<ButtonPress>', lambda e: self._set_btn(name, True))
        btn.bind('<ButtonRelease>', lambda e: self._set_btn(name, False))

    def _bind_keys(self):
        mapping = {
            '<Up>': 'UP', '<Down>': 'DOWN', '<Left>': 'LEFT', '<Right>': 'RIGHT',
            'z': 'Z', 'Z': 'Z', 'x': 'X', 'X': 'X'
        }
        for k, name in mapping.items():
            self.root.bind(k, lambda e, n=name: self._set_btn(n, True))
            self.root.bind(f'<KeyRelease-{k.strip("<>")}>', lambda e, n=name: self._set_btn(n, False))

    def _set_btn(self, name, state):
        self.btn_state[name] = state
        # Візуальний ефект натискання
        if name in self.gui_buttons:
            btn = self.gui_buttons[name]
            if state:
                btn.configure(relief="sunken", bg="#666")
            else:
                btn.configure(relief="raised", bg=btn.orig_color)

    def _on_close(self):
        self.running = False
        self.root.destroy()
        sys.exit()

    # --- API (Як у бібліотеки MAX7219 + Hardware) ---
    def pixel(self, x, y, value):
        if 0 <= x < self.cols and 0 <= y < self.rows:
            self.buffer[y][x] = value

    def fill(self, value):
        for r in range(self.rows):
            for c in range(self.cols):
                self.buffer[r][c] = value

    def show(self):
        if not self.running: return
        # Оновлення UI
        for r in range(self.rows):
            for c in range(self.cols):
                color = "#ff0000" if self.buffer[r][c] else "#333"
                # Оптимізація: оновлюємо тільки якщо колір змінився (Tkinter це любить)
                curr_color = self.canvas.itemcget(self.led_objects[r][c], "fill")
                if curr_color != color:
                    self.canvas.itemconfig(self.led_objects[r][c], fill=color)
        self.root.update_idletasks()

    def brightness(self, val): pass

    # --- API (Ввід/Вивід) ---
    def key(self, name):
        return self.btn_state.get(name, False)
    
    def tone(self, freq=440, duration=100):
        # Візуалізація звуку
        self.buzzer_canvas.itemconfig(self.buzzer_id, fill="red")
        self.root.after(int(duration*1000) if duration < 1 else duration, 
                        lambda: self.buzzer_canvas.itemconfig(self.buzzer_id, fill="#111"))

# ==========================================
# 2. ТВІЙ КОД (Logic Layer)
# ==========================================

# Твій клас-обгортка для матриці (щоб код був 1-в-1 як на RP2040)
class Matrix(GameBoyEmulator):
    def pixel(self, x, y, value):
        super().pixel(x, y, value) # Викликаємо метод емулятора

    def show(self): super().show()
    def fill(self, v): super().fill(v)
    def brightness(self, v): pass
    
    def loop(self, loop_func):
        # Запускаємо логіку в окремому потоці
        game_thread = threading.Thread(target=loop_func)
        game_thread.daemon = True # Закриється разом з вікном
        game_thread.start()

        # Запускаємо GUI (блокує головний потік)
        self.root.mainloop()