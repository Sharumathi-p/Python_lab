import tkinter as tk
import time
import threading
from tkinter import ttk, messagebox, simpledialog
import math
import random

class TowerOfHanoi:
    def __init__(self, root):
        self.root = root
        self.root.title("Tower of Hanoi Solver")
        self.root.geometry("1200x700")
        self.root.resizable(True, True)
        
        self.set_theme()
        
        self.disk_count = 3
        self.animation_speed = 0.5
        self.is_running = False
        self.pause_execution = False
        self.total_moves = 0
        self.current_move = 0
        self.move_history = []
        self.animation_in_progress = False
        self.fps = 60
        self.frame_time = 1.0 / self.fps
        
        self.tower_color = "#7f8c8d"
        self.base_color = "#34495e"
        self.disk_colors = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12", "#9b59b6", 
                          "#1abc9c", "#d35400", "#c0392b", "#16a085", "#8e44ad"]
        
        self.animation_frames = 30
        self.disk_in_motion = None
        self.disk_motion_path = []
        self.disk_motion_frame = 0
        
        self.towers = [[], [], []]
        
        self.create_ui()
        self.initialize_towers()
        self.draw_towers()
        
    def set_theme(self):
        self.root.configure(bg="#1e272e")
        
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('TButton', 
                        background="#3498db", 
                        foreground="white", 
                        font=('Helvetica', 10, 'bold'),
                        borderwidth=0,
                        focusthickness=3,
                        focuscolor='none')
        style.map('TButton', 
                 background=[('active', '#2980b9'), ('disabled', '#95a5a6')])
        
        style.configure('TScale', 
                       background="#1e272e", 
                       troughcolor="#34495e", 
                       sliderrelief="flat")
        
        style.configure('TCombobox', 
                       fieldbackground="#34495e",
                       background="#3498db",
                       foreground="white",
                       arrowcolor="white")
        style.map('TCombobox', 
                 fieldbackground=[('readonly', '#34495e')],
                 selectbackground=[('readonly', '#2980b9')],
                 selectforeground=[('readonly', 'white')])
        
    def create_ui(self):
        main_frame = tk.Frame(self.root, bg="#1e272e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        control_frame = tk.Frame(main_frame, bg="#1e272e")
        control_frame.pack(fill=tk.X, pady=(0, 20))
        
        disk_label = tk.Label(control_frame, text="Number of Disks:", bg="#1e272e", fg="white", font=("Helvetica", 12))
        disk_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.disk_var = tk.StringVar(value=str(self.disk_count))
        disk_combobox = ttk.Combobox(control_frame, textvariable=self.disk_var, values=[str(i) for i in range(1, 11)], width=5, style='TCombobox')
        disk_combobox.pack(side=tk.LEFT, padx=(0, 20))
        disk_combobox.bind("<<ComboboxSelected>>", self.change_disk_count)
        
        speed_label = tk.Label(control_frame, text="Animation Speed:", bg="#1e272e", fg="white", font=("Helvetica", 12))
        speed_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.speed_scale = ttk.Scale(control_frame, from_=0.1, to=2.0, orient=tk.HORIZONTAL, length=150, value=self.animation_speed, style='TScale')
        self.speed_scale.pack(side=tk.LEFT)
        self.speed_scale.bind("<ButtonRelease-1>", self.change_speed)
        
        self.speed_value = tk.Label(control_frame, text=f"{self.animation_speed:.1f}s", bg="#1e272e", fg="white", width=4, font=("Helvetica", 10))
        self.speed_value.pack(side=tk.LEFT, padx=(5, 20))
        
        def update_speed_label(val):
            self.animation_speed = round(float(self.speed_scale.get()), 1)
            self.speed_value.config(text=f"{self.animation_speed:.1f}s")
        
        self.speed_scale.config(command=update_speed_label)
        
        button_frame = tk.Frame(control_frame, bg="#1e272e")
        button_frame.pack(side=tk.RIGHT)
        
        self.start_button = tk.Button(button_frame, text="Start", bg="#2ecc71", fg="white", 
                                     font=("Helvetica", 12, "bold"), command=self.start_solver,
                                     relief=tk.FLAT, padx=15, pady=5)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.pause_button = tk.Button(button_frame, text="Pause", bg="#f39c12", fg="white", 
                                     font=("Helvetica", 12, "bold"), command=self.toggle_pause,
                                     relief=tk.FLAT, padx=15, pady=5, state=tk.DISABLED)
        self.pause_button.pack(side=tk.LEFT, padx=5)
        
        self.reset_button = tk.Button(button_frame, text="Reset", bg="#e74c3c", fg="white", 
                                     font=("Helvetica", 12, "bold"), command=self.reset,
                                     relief=tk.FLAT, padx=15, pady=5)
        self.reset_button.pack(side=tk.LEFT, padx=5)
        
        status_frame = tk.Frame(main_frame, bg="#1e272e")
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.move_label = tk.Label(status_frame, text="Moves: 0/0", bg="#1e272e", fg="white", font=("Helvetica", 12))
        self.move_label.pack(side=tk.LEFT)
        
        self.status_label = tk.Label(status_frame, text="Ready", bg="#1e272e", fg="white", font=("Helvetica", 12))
        self.status_label.pack(side=tk.RIGHT)
        
        self.canvas_frame = tk.Frame(main_frame, bg="#1e272e")
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg="#1e272e", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        info_frame = tk.Frame(main_frame, bg="#2c3e50", padx=15, pady=15, relief=tk.FLAT)
        info_frame.pack(fill=tk.X, pady=(15, 0))
        
        info_title = tk.Label(info_frame, text="Tower of Hanoi - Recursive AI Solver", 
                             bg="#2c3e50", fg="white", font=("Helvetica", 14, "bold"))
        info_title.pack(anchor=tk.W)
        
        info_text = tk.Label(info_frame, text="The Tower of Hanoi is a mathematical puzzle where the objective is to move a stack of disks from one tower to another, following specific rules.",
                            bg="#2c3e50", fg="white", font=("Helvetica", 10), wraplength=1150, justify=tk.LEFT)
        info_text.pack(anchor=tk.W, pady=(5, 0))
        
        rules_text = tk.Label(info_frame, text="Rules: 1) Only one disk can be moved at a time. 2) Each move consists of taking the upper disk from one of the stacks and placing it on top of another stack. 3) No disk may be placed on top of a smaller disk.",
                             bg="#2c3e50", fg="white", font=("Helvetica", 10), wraplength=1150, justify=tk.LEFT)
        rules_text.pack(anchor=tk.W, pady=(5, 0))
        
        ai_text = tk.Label(info_frame, text="This solver uses a recursive algorithm to find the optimal solution with the minimum number of moves (2ⁿ-1 moves for n disks).",
                          bg="#2c3e50", fg="white", font=("Helvetica", 10), wraplength=1150, justify=tk.LEFT)
        ai_text.pack(anchor=tk.W, pady=(5, 0))
        
        self.root.bind("<Configure>", self.on_resize)
        
    def on_resize(self, event):
        if event.widget == self.root:
            self.draw_towers()
        
    def initialize_towers(self):
        self.towers = [[], [], []]
        
        for i in range(self.disk_count, 0, -1):
            self.towers[0].append(i)
            
        self.total_moves = (2 ** self.disk_count) - 1
        self.move_label.config(text=f"Moves: 0/{self.total_moves}")
        self.current_move = 0
        self.move_history = []
        
    def draw_towers(self):
        self.canvas.delete("all")
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width < 50 or canvas_height < 50:
            return
            
        tower_width = 20
        tower_height = canvas_height * 0.7
        tower_spacing = canvas_width / 4
        tower_bottom = canvas_height * 0.8
        tower_top = tower_bottom - tower_height
        
        self.draw_background(canvas_width, canvas_height)
        
        base_width = tower_spacing * 3
        base_height = 30
        base_left = tower_spacing - base_width/2
        base_top = tower_bottom
        
        self.draw_3d_base(base_left, base_top, base_width, base_height)
        
        for i in range(3):
            tower_x = tower_spacing * (i + 1)
            
            self.draw_3d_tower(tower_x, tower_top, tower_bottom, tower_width)
            
            tower_name = ["Source", "Auxiliary", "Target"][i]
            self.canvas.create_text(
                tower_x, tower_bottom + base_height + 20,
                text=tower_name, fill="white", font=("Helvetica", 12, "bold")
            )
            
            max_disk_width = tower_spacing * 0.8
            disk_height = min(30, tower_height / (self.disk_count + 2))
            
            for j, disk in enumerate(self.towers[i]):
                disk_width = max_disk_width * (disk / self.disk_count)
                disk_top = tower_bottom - (j + 1) * disk_height
                
                self.draw_3d_disk(tower_x, disk_top, disk_width, disk_height, disk)
        
        if self.disk_in_motion is not None and self.disk_motion_path and self.disk_motion_frame < len(self.disk_motion_path):
            disk = self.disk_in_motion
            pos = self.disk_motion_path[self.disk_motion_frame]
            max_disk_width = tower_spacing * 0.8
            disk_width = max_disk_width * (disk / self.disk_count)
            disk_height = min(30, tower_height / (self.disk_count + 2))
            
            self.draw_3d_disk(pos[0], pos[1], disk_width, disk_height, disk)
    
    def draw_background(self, width, height):
        for i in range(height):
            r = int(30 + (i / height) * 10)
            g = int(39 + (i / height) * 15)
            b = int(46 + (i / height) * 20)
            color = f"#{r:02x}{g:02x}{b:02x}"
            
            self.canvas.create_line(0, i, width, i, fill=color)
    
    def draw_3d_base(self, x, y, width, height):
        self.canvas.create_rectangle(
            x, y, x + width, y + height,
            fill=self.base_color, outline=""
        )
        
        self.canvas.create_polygon(
            x, y, x + width, y, x + width - 10, y + 5, x + 10, y + 5,
            fill="#3c5979", outline=""
        )
        
        self.canvas.create_polygon(
            x + width, y, x + width, y + height, x + width - 10, y + height - 5, x + width - 10, y + 5,
            fill="#2c3e50", outline=""
        )
        
        for i in range(int(x) + 20, int(x + width), 40):
            self.canvas.create_line(
                i, y + 5, i, y + height - 5,
                fill="#2c3e50", width=2
            )
    
    def draw_3d_tower(self, x, top, bottom, width):
        self.canvas.create_rectangle(
            x - width/2, top, x + width/2, bottom,
            fill=self.tower_color, outline=""
        )
        
        self.canvas.create_rectangle(
            x - width/2, top, x - width/2 + 3, bottom,
            fill="#95a5a6", outline=""
        )
        
        self.canvas.create_rectangle(
            x + width/2 - 3, top, x + width/2, bottom,
            fill="#5d6d7e", outline=""
        )
        
        self.canvas.create_oval(
            x - width/2 - 5, top - 10, x + width/2 + 5, top + 10,
            fill="#95a5a6", outline=""
        )
    
    def draw_3d_disk(self, x, y, width, height, disk):
        base_color = self.disk_colors[disk % len(self.disk_colors)]
        
        r = int(base_color[1:3], 16)
        g = int(base_color[3:5], 16)
        b = int(base_color[5:7], 16)
        
        highlight = f"#{min(r+30, 255):02x}{min(g+30, 255):02x}{min(b+30, 255):02x}"
        shadow = f"#{max(r-30, 0):02x}{max(g-30, 0):02x}{max(b-30, 0):02x}"
        
        self.canvas.create_rectangle(
            x - width/2, y, x + width/2, y + height,
            fill=base_color, outline=""
        )
        
        self.canvas.create_rectangle(
            x - width/2, y, x + width/2, y + height/4,
            fill=highlight, outline=""
        )
        
        self.canvas.create_rectangle(
            x - width/2, y + 3*height/4, x + width/2, y + height,
            fill=shadow, outline=""
        )
        
        self.canvas.create_oval(
            x - width/2 - height/4, y, x - width/2 + height/4, y + height,
            fill=highlight, outline=""
        )
        
        self.canvas.create_oval(
            x + width/2 - height/4, y, x + width/2 + height/4, y + height,
            fill=shadow, outline=""
        )
        
        self.canvas.create_text(
            x, y + height/2,
            text=str(disk), fill="white", font=("Helvetica", 10, "bold")
        )
    
    def change_disk_count(self, event=None):
        try:
            new_count = int(self.disk_var.get())
            if 1 <= new_count <= 10:
                self.disk_count = new_count
                self.reset()
            else:
                messagebox.showwarning("Invalid Input", "Please enter a number between 1 and 10.")
                self.disk_var.set(str(self.disk_count))
        except ValueError:
            messagebox.showwarning("Invalid Input", "Please enter a valid number.")
            self.disk_var.set(str(self.disk_count))
    
    def change_speed(self, event=None):
        self.animation_speed = round(float(self.speed_scale.get()), 1)
        self.speed_value.config(text=f"{self.animation_speed:.1f}s")
    
    def start_solver(self):
        if not self.is_running:
            self.is_running = True
            self.pause_execution = False
            self.start_button.config(state=tk.DISABLED)
            self.pause_button.config(state=tk.NORMAL, text="Pause")
            self.reset_button.config(state=tk.DISABLED)
            self.status_label.config(text="Running...")
            
            self.move_history = []
            self.hanoi_recursive(self.disk_count, 0, 2, 1)
            
            threading.Thread(target=self.animate_solution, daemon=True).start()
    
    def toggle_pause(self):
        self.pause_execution = not self.pause_execution
        if self.pause_execution:
            self.pause_button.config(text="Resume")
            self.status_label.config(text="Paused")
        else:
            self.pause_button.config(text="Resume")
            self.status_label.config(text="Running...")
    
    def reset(self):
        if self.is_running:
            self.is_running = False
            self.pause_execution = False
        
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)
        self.reset_button.config(state=tk.NORMAL)
        self.status_label.config(text="Ready")
        
        self.initialize_towers()
        self.draw_towers()
    
    def hanoi_recursive(self, n, source, target, auxiliary):
        if n > 0:
            self.hanoi_recursive(n-1, source, auxiliary, target)
            
            self.move_history.append((source, target))
            
            self.hanoi_recursive(n-1, auxiliary, target, source)
    
    def calculate_motion_path(self, source_tower, target_tower, disk):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        tower_spacing = canvas_width / 4
        tower_bottom = canvas_height * 0.8
        source_x = tower_spacing * (source_tower + 1)
        target_x = tower_spacing * (target_tower + 1)
        
        max_disk_width = tower_spacing * 0.8
        disk_height = min(30, canvas_height * 0.7 / (self.disk_count + 2))
        
        source_y = tower_bottom - len(self.towers[source_tower]) * disk_height
        
        target_y = tower_bottom - len(self.towers[target_tower]) * disk_height
        
        control_y = min(source_y, target_y) - 100
        
        path = []
        steps = self.animation_frames
        
        for i in range(steps + 1):
            t = i / steps
            x = (1-t)*2 * source_x + 2*(1-t)*t * ((source_x + target_x)/2) + t*2 * target_x
            y = (1-t)*2 * source_y + 2*(1-t)*t * control_y + t*2 * target_y
            path.append((x, y))
            
        return path
    
    def animate_solution(self):
        self.current_move = 0
        self.towers = [[], [], []]
        
        for i in range(self.disk_count, 0, -1):
            self.towers[0].append(i)
        
        self.root.after(0, self.draw_towers)
        
        for source, target in self.move_history:
            while self.pause_execution and self.is_running:
                time.sleep(0.1)
                
            if not self.is_running:
                break
                
            self.current_move += 1
            self.root.after(0, lambda m=self.current_move: self.move_label.config(text=f"Moves: {m}/{self.total_moves}"))
            
            disk = self.towers[source].pop()
            
            self.disk_in_motion = disk
            self.disk_motion_path = self.calculate_motion_path(source, target, disk)
            self.disk_motion_frame = 0
            
            start_time = time.time()
            for frame in range(len(self.disk_motion_path)):
                while self.pause_execution and self.is_running:
                    time.sleep(0.1)
                
                if not self.is_running:
                    break
                
                self.disk_motion_frame = frame
                
                self.root.after(0, self.draw_towers)
                
                frame_end_time = start_time + (frame + 1) * (self.animation_speed / len(self.disk_motion_path))
                current_time = time.time()
                
                if current_time < frame_end_time:
                    time.sleep(frame_end_time - current_time)
            
            self.towers[target].append(disk)
            self.disk_in_motion = None
            
            self.root.after(0, self.draw_towers)
        
        if self.is_running:
            self.is_running = False
            self.root.after(0, lambda: self.status_label.config(text="Completed!"))
            self.root.after(0, lambda: self.start_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.pause_button.config(state=tk.DISABLED))
            self.root.after(0, lambda: self.reset_button.config(state=tk.NORMAL))
            
            self.celebration_effect()
    
    def celebration_effect(self):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        particles = []
        for _ in range(50):
            x = random.randint(0, canvas_width)
            y = random.randint(0, canvas_height)
            color = random.choice(self.disk_colors)
            size = random.randint(5, 15)
            speed_x = random.uniform(-2, 2)
            speed_y = random.uniform(-3, -1)
            particles.append([x, y, color, size, speed_x, speed_y])
        
        def animate_particles(step=0):
            if step >= 100:
                return
            
            self.canvas.delete("particle")
            
            for p in particles:
                p[0] += p[4]
                p[1] += p[5]
                p[5] += 0.1
                
                self.canvas.create_oval(
                    p[0] - p[3]/2, p[1] - p[3]/2,
                    p[0] + p[3]/2, p[1] + p[3]/2,
                    fill=p[2], outline="", tags="particle"
                )
            
            self.root.after(16, lambda: animate_particles(step + 1))
        
        animate_particles()

def main():
    root = tk.Tk()
    app = TowerOfHanoi(root)
    root.mainloop()

if __name__ == "__main__":
    main()
