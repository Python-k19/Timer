import tkinter as tk
from tkinter import ttk, filedialog
import time
import webbrowser
import subprocess
import os
import sys
import ctypes
import psutil
import winsound
from datetime import datetime, timedelta
import threading

# ===== СКРЫТИЕ КОНСОЛИ =====
def hide_console():
    """Скрывает консольное окно при запуске"""
    try:
        console_window = ctypes.windll.kernel32.GetConsoleWindow()
        if console_window:
            ctypes.windll.user32.ShowWindow(console_window, 0)
    except:
        pass

hide_console()

# ===== ПРАВА АДМИНИСТРАТОРА =====
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if not is_admin():
        try:
            # Пробуем запустить через pythonw (без консоли)
            pythonw_path = sys.executable.replace("python.exe", "pythonw.exe")
            if os.path.exists(pythonw_path):
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", pythonw_path, " ".join(sys.argv), None, 1
                )
            else:
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", sys.executable, " ".join(sys.argv), None, 1
                )
            sys.exit(0)
        except Exception as e:
            print(f"Ошибка: {e}")

if not is_admin():
    run_as_admin()

# ===== КАСТОМНЫЕ АНИМИРОВАННЫЕ КНОПКИ =====
class AnimatedButton(tk.Canvas):
    """Кнопка с анимацией и подсветкой"""
    
    def __init__(self, parent, text, command=None, bg_color="#2a2a2a", 
                 hover_color="#4a9eff", text_color="white", width=120, height=40,
                 font=("Arial", 11, "bold"), **kwargs):
        super().__init__(parent, width=width, height=height, 
                        bg=parent.cget("bg"), highlightthickness=0, **kwargs)
        
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.text = text
        self.width = width
        self.height = height
        self.font = font
        self.is_hovered = False
        self.current_color = bg_color
        
        self.draw_button()
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        self.bind("<ButtonRelease-1>", self.on_release)
    
    def draw_button(self):
        self.delete("all")
        self.create_rectangle(0, 0, self.width, self.height,
                            fill=self.current_color, outline="", width=0)
        self.create_text(self.width/2, self.height/2, text=self.text,
                        fill=self.text_color, font=self.font)
    
    def animate_color(self, target_color, steps=10):
        """Плавная анимация цвета"""
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        def rgb_to_hex(rgb):
            return '#{:02x}{:02x}{:02x}'.format(*rgb)
        
        current_rgb = hex_to_rgb(self.current_color)
        target_rgb = hex_to_rgb(target_color)
        
        for i in range(steps + 1):
            ratio = i / steps
            new_rgb = tuple(int(current_rgb[j] + (target_rgb[j] - current_rgb[j]) * ratio)
                          for j in range(3))
            self.current_color = rgb_to_hex(new_rgb)
            self.draw_button()
            self.update()
            time.sleep(0.02)
    
    def on_enter(self, event):
        self.is_hovered = True
        threading.Thread(target=self.animate_color, 
                        args=(self.hover_color,), daemon=True).start()
    
    def on_leave(self, event):
        self.is_hovered = False
        threading.Thread(target=self.animate_color, 
                        args=(self.bg_color,), daemon=True).start()
    
    def on_click(self, event):
        self.animate_color("#ffffff", steps=5)
    
    def on_release(self, event):
        if self.is_hovered:
            self.animate_color(self.hover_color, steps=5)
        else:
            self.animate_color(self.bg_color, steps=5)
        
        if self.command:
            self.command()


class AnimatedRadioButton(tk.Frame):
    """Радиокнопка с анимацией"""
    
    def __init__(self, parent, text, variable, value, font=("Arial", 11),
                 bg_color="#2a2a2a", hover_color="#3a3a3a", active_color="#4a9eff",
                 text_color="white", width=250, height=45, **kwargs):
        super().__init__(parent, bg=parent.cget("bg"), **kwargs)
        
        self.variable = variable
        self.value = value
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.active_color = active_color
        self.text_color = text_color
        self.text = text
        self.width = width
        self.height = height
        
        self.canvas = tk.Canvas(self, width=width, height=height,
                               bg=parent.cget("bg"), highlightthickness=0)
        self.canvas.pack()
        
        self.canvas.bind("<Enter>", self.on_enter)
        self.canvas.bind("<Leave>", self.on_leave)
        self.canvas.bind("<Button-1>", self.on_click)
        
        self.variable.trace_add("write", self.update_visual)
        
        self.is_hovered = False
        self.current_bg = bg_color
        
        self.draw()
    
    def draw(self):
        self.canvas.delete("all")
        
        if self.variable.get() == self.value:
            fill_color = self.active_color
            text_color = "black"
        else:
            fill_color = self.current_bg
            text_color = self.text_color
        
        self.canvas.create_rectangle(0, 0, self.width, self.height,
                                    fill=fill_color, outline="", width=0)
        
        self.canvas.create_text(20, self.height/2, text=self.text,
                               fill=text_color, font=("Arial", 11), anchor="w")
        
        if self.variable.get() == self.value:
            self.canvas.create_oval(self.width-30, self.height/2-8,
                                   self.width-14, self.height/2+8,
                                   fill="black", outline="")
    
    def update_visual(self, *args):
        self.draw()
    
    def on_enter(self, event):
        self.is_hovered = True
        if self.variable.get() != self.value:
            self.current_bg = self.hover_color
            self.draw()
    
    def on_leave(self, event):
        self.is_hovered = False
        if self.variable.get() != self.value:
            self.current_bg = self.bg_color
            self.draw()
    
    def on_click(self, event):
        self.variable.set(self.value)


# ===== ОСНОВНОЙ КЛАСС =====
class BeautifulTimer:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("⏱️ Красивый Таймер")
        self.window.geometry("950x720")
        self.window.configure(bg="#1a1a1a")
        self.window.minsize(900, 680)
        
        # ПРОЗРАЧНОСТЬ
        self.window.attributes('-alpha', 0.95)
        
        self.time_left = 0
        self.total_time = 0
        self.is_running = False
        self.target_time = None
        self.alarm_playing = False
        
        # ===== ШАПКА =====
        header = tk.Frame(self.window, bg="#1a1a1a", height=60)
        header.pack(fill="x", padx=20, pady=10)
        
        tk.Label(header, text="⏱️ ТАЙМЕР", font=("Arial", 22, "bold"), 
                bg="#1a1a1a", fg="white").pack(side="left")
        
        badge_text = "🛡️ Admin" if is_admin() else "⚠️ User"
        badge_color = "#4a9eff" if is_admin() else "#ffaa4a"
        tk.Label(header, text=badge_text, font=("Arial", 10, "bold"),
                bg=badge_color, fg="white", padx=10, pady=3).pack(side="right")
        
        # ===== ОСНОВНОЙ КОНТЕЙНЕР =====
        main_container = tk.Frame(self.window, bg="#1a1a1a")
        main_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # ===== ЛЕВАЯ КОЛОНКА =====
        left_panel = tk.Frame(main_container, bg="#1a1a1a", width=550)
        left_panel.pack(side="left", fill="both", padx=(0,20))
        left_panel.pack_propagate(False)
        
        # Режим
        mode_frame = tk.Frame(left_panel, bg="#1a1a1a")
        mode_frame.pack(pady=10, fill="x")
        
        tk.Label(mode_frame, text="Режим:", font=("Arial", 11, "bold"), 
                bg="#1a1a1a", fg="white").pack(side="left", padx=(0,10))
        
        self.mode_var = tk.StringVar(value="countdown")
        self.mode_var.trace_add("write", self.on_mode_changed)
        
        AnimatedRadioButton(mode_frame, "⏳ Обратный отсчёт", self.mode_var, "countdown",
                           width=170, height=35).pack(side="left", padx=3)
        
        AnimatedRadioButton(mode_frame, "🕐 Точное время", self.mode_var, "exact_time",
                           width=170, height=35).pack(side="left", padx=3)
        
        # Поля для обратного отсчёта
        self.countdown_frame = tk.Frame(left_panel, bg="#1a1a1a")
        self.countdown_frame.pack(pady=10)
        
        entry_style = {
            "width": 4, "font": ("Arial", 26), 
            "bg": "#2a2a2a", "fg": "white", 
            "justify": "center", "insertbackground": "white",
            "relief": "flat", "bd": 2
        }
        
        self.hours = tk.Entry(self.countdown_frame, **entry_style)
        self.hours.insert(0, "0")
        self.hours.pack(side="left", padx=3)
        
        tk.Label(self.countdown_frame, text=":", font=("Arial", 26, "bold"), 
                bg="#1a1a1a", fg="white").pack(side="left")
        
        self.minutes = tk.Entry(self.countdown_frame, **entry_style)
        self.minutes.insert(0, "5")
        self.minutes.pack(side="left", padx=3)
        
        tk.Label(self.countdown_frame, text=":", font=("Arial", 26, "bold"), 
                bg="#1a1a1a", fg="white").pack(side="left")
        
        self.seconds = tk.Entry(self.countdown_frame, **entry_style)
        self.seconds.insert(0, "0")
        self.seconds.pack(side="left", padx=3)
        
        # Поля для точного времени
        self.exact_frame = tk.Frame(left_panel, bg="#1a1a1a")
        
        tk.Label(self.exact_frame, text="Запустить в:", font=("Arial", 11, "bold"),
                bg="#1a1a1a", fg="white").pack(anchor="w", pady=(0,5))
        
        exact_input = tk.Frame(self.exact_frame, bg="#1a1a1a")
        exact_input.pack()
        
        self.target_hours = tk.Entry(exact_input, **entry_style)
        self.target_hours.insert(0, "23")
        self.target_hours.pack(side="left", padx=3)
        
        tk.Label(exact_input, text=":", font=("Arial", 26, "bold"), 
                bg="#1a1a1a", fg="white").pack(side="left")
        
        self.target_minutes = tk.Entry(exact_input, **entry_style)
        self.target_minutes.insert(0, "00")
        self.target_minutes.pack(side="left", padx=3)
        
        self.current_time_label = tk.Label(self.exact_frame, 
                                          text="Сейчас: " + datetime.now().strftime("%H:%M:%S"), 
                                          font=("Arial", 9), bg="#1a1a1a", fg="#888888")
        self.current_time_label.pack(pady=(8,0))
        
        # Дисплей таймера
        self.timer_display = tk.Label(left_panel, text="00:00:00", 
                                     font=("Arial", 50, "bold"), 
                                     bg="#1a1a1a", fg="#4a9eff")
        self.timer_display.pack(pady=15)
        
        # Прогресс-бар
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Custom.Horizontal.TProgressbar", 
                       background="#4a9eff", troughcolor="#2a2a2a", borderwidth=0)
        
        self.progress = ttk.Progressbar(left_panel, length=400, mode='determinate',
                                        style="Custom.Horizontal.TProgressbar")
        self.progress.pack(pady=10)
        
        # Кнопки управления
        btn_frame = tk.Frame(left_panel, bg="#1a1a1a")
        btn_frame.pack(pady=15)
        
        start_btn = AnimatedButton(btn_frame, "▶ Старт", 
                                  command=self.start_timer,
                                  bg_color="#4aff4a", hover_color="#2aff2a",
                                  text_color="black", width=140, height=50,
                                  font=("Arial", 13, "bold"))
        start_btn.pack(side="left", padx=8)
        
        stop_btn = AnimatedButton(btn_frame, "⏹ Стоп", 
                                 command=self.stop_timer,
                                 bg_color="#ff4a4a", hover_color="#ff6a6a",
                                 text_color="white", width=140, height=50,
                                 font=("Arial", 13, "bold"))
        stop_btn.pack(side="left", padx=8)
        
        # Статус
        self.status = tk.Label(left_panel, text="🛡️ Готов к запуску", 
                              font=("Arial", 10), bg="#1a1a1a", fg="#888888")
        self.status.pack(side="bottom", pady=5)
        
        # ===== ПРАВАЯ КОЛОНКА =====
        right_panel = tk.Frame(main_container, bg="#1a1a1a", width=350)
        right_panel.pack(side="right", fill="both")
        right_panel.pack_propagate(False)
        
        tk.Label(right_panel, text="📋 ДЕЙСТВИЯ", font=("Arial", 13, "bold"), 
                bg="#1a1a1a", fg="white").pack(pady=(0,10))
        
        # Список действий
        self.action_var = tk.StringVar(value="alarm")
        self.action_var.trace_add("write", self.on_action_changed)
        
        self.actions = [
            ("🔔", "alarm",         "Будильник (звук)"),
            ("🔗", "open_url",      "Открыть ссылку"),
            ("📂", "open_program",  "Открыть программу"),
            ("❌", "close_program", "Закрыть программу"),
            ("💻", "shutdown",      "Выключить ПК"),
            ("🔄", "restart",       "Перезагрузить ПК"),
            ("💤", "sleep",         "Спящий режим"),
        ]
        
        self.action_buttons = {}
        actions_frame = tk.Frame(right_panel, bg="#1a1a1a")
        actions_frame.pack(fill="x", padx=5)
        
        for icon, value, text in self.actions:
            btn = AnimatedRadioButton(
                actions_frame, 
                text=f"{icon}  {text}",
                variable=self.action_var,
                value=value,
                width=330, height=42,
                bg_color="#2a2a2a",
                hover_color="#3a3a3a",
                active_color="#4a9eff"
            )
            btn.pack(pady=2, fill="x")
            self.action_buttons[value] = btn
        
        # ===== КОНТЕЙНЕР ДЛЯ ДОПОЛНИТЕЛЬНЫХ ПОЛЕЙ =====
        self.extra_frame = tk.Frame(right_panel, bg="#252525", bd=2, relief="groove")
        self.extra_frame.pack(pady=15, fill="x", padx=5)
        
        self.extra_title = tk.Label(self.extra_frame, text="Настройки действия", 
                                    font=("Arial", 10, "bold"),
                                    bg="#252525", fg="#4a9eff")
        self.extra_title.pack(anchor="w", padx=10, pady=(8,0))
        
        # --- Будильник ---
        self.alarm_frame = tk.Frame(self.extra_frame, bg="#252525")
        
        tk.Label(self.alarm_frame, text="🎵 Мелодия:", font=("Arial", 10),
                bg="#252525", fg="white").pack(anchor="w", padx=10, pady=(5,0))
        
        self.alarm_sound_var = tk.StringVar(value="beep")
        sounds = [
            ("🔔 Стандартный сигнал", "beep"),
            ("⚠️ Тревога", "alarm"),
            ("✨ Космический", "space"),
            ("🎹 Мелодия", "melody"),
            ("📁 Свой .wav файл", "custom"),
        ]
        for text, val in sounds:
            tk.Radiobutton(self.alarm_frame, text=text, variable=self.alarm_sound_var,
                          value=val, font=("Arial", 9),
                          bg="#252525", fg="white", selectcolor="#3a3a3a",
                          activebackground="#252525", activeforeground="#4a9eff",
                          anchor="w").pack(anchor="w", padx=15, pady=1)
        
        # Поле для своего файла
        custom_frame = tk.Frame(self.alarm_frame, bg="#252525")
        custom_frame.pack(fill="x", padx=10, pady=(5,5))
        
        self.custom_sound_entry = tk.Entry(custom_frame, font=("Arial", 9),
                                          bg="#3a3a3a", fg="white", 
                                          insertbackground="white", relief="flat", bd=2)
        self.custom_sound_entry.insert(0, "C:\\sound.wav")
        self.custom_sound_entry.pack(side="left", fill="x", expand=True, padx=(0,3))
        
        AnimatedButton(custom_frame, "📁", command=self.browse_sound,
                      bg_color="#4a9eff", hover_color="#6a9eff",
                      width=35, height=25, font=("Arial", 9)).pack(side="left")
        
        # Кнопка "Проверить звук"
        AnimatedButton(self.alarm_frame, "▶ Проверить звук", 
                      command=self.test_alarm_sound,
                      bg_color="#4a9eff", hover_color="#6a9eff",
                      width=200, height=30, font=("Arial", 9, "bold")).pack(pady=5)
        
        # --- Ссылка ---
        self.url_frame = tk.Frame(self.extra_frame, bg="#252525")
        tk.Label(self.url_frame, text="🌐 URL:", font=("Arial", 10),
                bg="#252525", fg="white").pack(anchor="w", padx=10, pady=(5,0))
        
        url_input = tk.Frame(self.url_frame, bg="#252525")
        url_input.pack(fill="x", padx=10, pady=5)
        
        self.url_entry = tk.Entry(url_input, font=("Arial", 10), 
                                 bg="#3a3a3a", fg="white", insertbackground="white",
                                 relief="flat", bd=2)
        self.url_entry.insert(0, "https://youtube.com")
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0,3))
        
        AnimatedButton(url_input, "🔍", command=self.test_url,
                      bg_color="#4a9eff", hover_color="#6a9eff",
                      width=35, height=25, font=("Arial", 10)).pack(side="left")
        
        # --- Открыть программу ---
        self.prog_frame = tk.Frame(self.extra_frame, bg="#252525")
        tk.Label(self.prog_frame, text="📂 Путь к программе:", font=("Arial", 10),
                bg="#252525", fg="white").pack(anchor="w", padx=10, pady=(5,0))
        
        prog_input = tk.Frame(self.prog_frame, bg="#252525")
        prog_input.pack(fill="x", padx=10, pady=5)
        
        self.prog_entry = tk.Entry(prog_input, font=("Arial", 10), 
                                  bg="#3a3a3a", fg="white", insertbackground="white",
                                  relief="flat", bd=2)
        self.prog_entry.insert(0, "C:\\Windows\\System32\\notepad.exe")
        self.prog_entry.pack(side="left", fill="x", expand=True, padx=(0,3))
        
        AnimatedButton(prog_input, "📁", command=self.browse_program,
                      bg_color="#4a9eff", hover_color="#6a9eff",
                      width=35, height=25, font=("Arial", 10)).pack(side="left")
        
        self.admin_launch_var = tk.BooleanVar(value=False)
        tk.Checkbutton(self.prog_frame, text="🛡️ От имени администратора",
                      variable=self.admin_launch_var,
                      bg="#252525", fg="white", selectcolor="#3a3a3a",
                      activebackground="#252525", activeforeground="white",
                      font=("Arial", 9)).pack(anchor="w", padx=10, pady=5)
        
        # --- Закрыть программу ---
        self.close_frame = tk.Frame(self.extra_frame, bg="#252525")
        tk.Label(self.close_frame, text="❌ Имя процесса:", font=("Arial", 10),
                bg="#252525", fg="white").pack(anchor="w", padx=10, pady=(5,0))
        
        close_input = tk.Frame(self.close_frame, bg="#252525")
        close_input.pack(fill="x", padx=10, pady=5)
        
        self.process_entry = tk.Entry(close_input, font=("Arial", 10), 
                                     bg="#3a3a3a", fg="white", insertbackground="white",
                                     relief="flat", bd=2)
        self.process_entry.insert(0, "chrome.exe")
        self.process_entry.pack(side="left", fill="x", expand=True, padx=(0,3))
        
        AnimatedButton(close_input, "📋", command=self.show_processes,
                      bg_color="#4a9eff", hover_color="#6a9eff",
                      width=35, height=25, font=("Arial", 10)).pack(side="left")
        
        # --- Системные ---
        self.system_frame = tk.Frame(self.extra_frame, bg="#252525")
        tk.Label(self.system_frame, text="⚡ Действие выполнится автоматически", 
                font=("Arial", 10), bg="#252525", fg="#888888").pack(padx=10, pady=20)
        
        # Инициализация
        self.on_mode_changed()
        self.on_action_changed()
    
    # ===== ОБРАБОТЧИКИ =====
    def on_mode_changed(self, *args):
        mode = self.mode_var.get()
        if mode == "countdown":
            self.exact_frame.pack_forget()
            self.countdown_frame.pack(pady=10, before=self.timer_display)
        else:
            self.countdown_frame.pack_forget()
            self.exact_frame.pack(pady=10, before=self.timer_display)
    
    def on_action_changed(self, *args):
        self.alarm_frame.pack_forget()
        self.url_frame.pack_forget()
        self.prog_frame.pack_forget()
        self.close_frame.pack_forget()
        self.system_frame.pack_forget()
        
        action = self.action_var.get()
        if action == "alarm":
            self.extra_title.config(text="🔔 Настройки будильника")
            self.alarm_frame.pack(fill="x", pady=5)
        elif action == "open_url":
            self.extra_title.config(text="🔗 Настройки ссылки")
            self.url_frame.pack(fill="x", pady=5)
        elif action == "open_program":
            self.extra_title.config(text="📂 Настройки программы")
            self.prog_frame.pack(fill="x", pady=5)
        elif action == "close_program":
            self.extra_title.config(text="❌ Настройки процесса")
            self.close_frame.pack(fill="x", pady=5)
        else:
            self.extra_title.config(text="⚡ Системное действие")
            self.system_frame.pack(fill="x", pady=5)
    
    # ===== РАБОТА С ФАЙЛАМИ =====
    def test_url(self):
        url = self.url_entry.get()
        if url:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            webbrowser.open(url)
            self.set_status(f"✅ Открыто: {url}", "#4aff4a")
    
    def browse_program(self):
        file_path = filedialog.askopenfilename(
            title="Выберите программу",
            filetypes=[("Программы", "*.exe"), ("Все файлы", "*.*")]
        )
        if file_path:
            self.prog_entry.delete(0, tk.END)
            self.prog_entry.insert(0, file_path)
    
    def browse_sound(self):
        file_path = filedialog.askopenfilename(
            title="Выберите звуковой файл",
            filetypes=[("WAV", "*.wav"), ("Все файлы", "*.*")]
        )
        if file_path:
            self.custom_sound_entry.delete(0, tk.END)
            self.custom_sound_entry.insert(0, file_path)
    
    def show_processes(self):
        proc_window = tk.Toplevel(self.window)
        proc_window.title("📋 Список процессов")
        proc_window.geometry("400x350")
        proc_window.configure(bg="#1a1a1a")
        proc_window.attributes('-alpha', 0.95)
        
        tk.Label(proc_window, text="Клик для выбора процесса:", 
                font=("Arial", 11, "bold"), bg="#1a1a1a", fg="white").pack(pady=10)
        
        list_frame = tk.Frame(proc_window, bg="#1a1a1a")
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        process_list = tk.Listbox(list_frame, font=("Consolas", 10),
                                 bg="#2a2a2a", fg="white", selectbackground="#4a9eff",
                                 yscrollcommand=scrollbar.set)
        process_list.pack(fill="both", expand=True)
        scrollbar.config(command=process_list.yview)
        
        processes = []
        for proc in psutil.process_iter(['name']):
            try:
                processes.append(proc.info['name'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        for p in sorted(set(processes)):
            process_list.insert(tk.END, p)
        
        def on_select(event):
            sel = process_list.curselection()
            if sel:
                self.process_entry.delete(0, tk.END)
                self.process_entry.insert(0, process_list.get(sel[0]))
                proc_window.destroy()
        
        process_list.bind('<<ListboxSelect>>', on_select)
    
    # ===== ЗВУКИ БУДИЛЬНИКА =====
    def play_alarm_sound(self):
        sound_type = self.alarm_sound_var.get()
        
        try:
            if sound_type == "beep":
                for _ in range(5):
                    if not self.alarm_playing:
                        break
                    winsound.Beep(1000, 500)
                    time.sleep(0.3)
            
            elif sound_type == "alarm":
                for _ in range(8):
                    if not self.alarm_playing:
                        break
                    winsound.Beep(800, 200)
                    winsound.Beep(1200, 200)
            
            elif sound_type == "space":
                for freq in [400, 600, 800, 1000, 1200, 1000, 800, 600]:
                    if not self.alarm_playing:
                        break
                    winsound.Beep(freq, 150)
            
            elif sound_type == "melody":
                notes = [523, 587, 659, 698, 784, 698, 659, 587, 523]
                for note in notes:
                    if not self.alarm_playing:
                        break
                    winsound.Beep(note, 250)
            
            elif sound_type == "custom":
                file_path = self.custom_sound_entry.get()
                if os.path.exists(file_path):
                    winsound.PlaySound(file_path, winsound.SND_FILENAME)
                else:
                    winsound.Beep(1000, 1000)
        
        except Exception as e:
            print(f"Ошибка звука: {e}")
            winsound.Beep(1000, 1000)
    
    def test_alarm_sound(self):
        self.alarm_playing = True
        threading.Thread(target=self._test_alarm_thread, daemon=True).start()
    
    def _test_alarm_thread(self):
        self.play_alarm_sound()
        self.alarm_playing = False
    
    def stop_alarm_sound(self):
        self.alarm_playing = False
        try:
            winsound.PlaySound(None, winsound.SND_PURGE)
        except:
            pass
    
    # ===== ЛОГИКА ТАЙМЕРА =====
    def calculate_time_left(self):
        mode = self.mode_var.get()
        if mode == "countdown":
            try:
                h = int(self.hours.get() or 0)
                m = int(self.minutes.get() or 0)
                s = int(self.seconds.get() or 0)
                return h * 3600 + m * 60 + s
            except ValueError:
                return 0
        else:
            try:
                target_h = int(self.target_hours.get() or 0)
                target_m = int(self.target_minutes.get() or 0)
                now = datetime.now()
                target = now.replace(hour=target_h, minute=target_m, second=0, microsecond=0)
                if target <= now:
                    target += timedelta(days=1)
                self.target_time = target
                return int((target - now).total_seconds())
            except ValueError:
                return 0
    
    def countdown(self):
        if self.is_running and self.time_left > 0:
            h = self.time_left // 3600
            m = (self.time_left % 3600) // 60
            s = self.time_left % 60
            self.timer_display.config(text=f"{h:02d}:{m:02d}:{s:02d}")
            
            if self.mode_var.get() == "exact_time":
                self.current_time_label.config(
                    text="Сейчас: " + datetime.now().strftime("%H:%M:%S"))
            
            if self.total_time > 0:
                self.progress['value'] = (self.time_left / self.total_time) * 100
            
            if self.time_left <= 10:
                self.timer_display.config(fg="#ff4a4a")
            elif self.time_left <= 30:
                self.timer_display.config(fg="#ffaa4a")
            
            self.time_left -= 1
            self.window.after(1000, self.countdown)
        elif self.time_left == 0 and self.is_running:
            self.timer_display.config(text="00:00:00", fg="#ff4a4a")
            self.progress['value'] = 0
            self.is_running = False
            self.perform_action()
    
    def start_timer(self):
        self.stop_alarm_sound()
        self.time_left = self.calculate_time_left()
        self.total_time = self.time_left
        
        if self.time_left > 0:
            self.is_running = True
            self.timer_display.config(fg="#4a9eff")
            
            if self.mode_var.get() == "countdown":
                self.set_status("⏳ Таймер запущен...", "#4a9eff")
            else:
                self.set_status(
                    f"🕐 Запуск: {self.target_time.strftime('%d.%m.%Y в %H:%M')}",
                    "#4a9eff")
            self.countdown()
        else:
            self.set_status("⚠️ Установите корректное время", "#ffaa4a")
    
    def stop_timer(self):
        self.is_running = False
        self.stop_alarm_sound()
        self.timer_display.config(text="00:00:00", fg="#4a9eff")
        self.progress['value'] = 0
        self.set_status("⏹ Таймер остановлен", "#888888")
    
    def set_status(self, text, color):
        self.status.config(text=text, fg=color)
    
    def perform_action(self):
        action = self.action_var.get()
        
        if action == "alarm":
            self.set_status("🔔 Будильник!", "#ffaa4a")
            self.alarm_playing = True
            threading.Thread(target=self._alarm_thread, daemon=True).start()
        
        elif action == "shutdown":
            self.set_status("💻 Выключение ПК через 10 сек...", "#ff4a4a")
            self.window.update()
            os.system("shutdown /s /t 10")
        
        elif action == "restart":
            self.set_status("🔄 Перезагрузка через 10 сек...", "#ff4a4a")
            self.window.update()
            os.system("shutdown /r /t 10")
        
        elif action == "sleep":
            self.set_status("💤 Спящий режим...", "#ffaa4a")
            self.window.update()
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        
        elif action == "open_url":
            url = self.url_entry.get()
            if url:
                if not url.startswith(('http://', 'https://')):
                    url = 'https://' + url
                webbrowser.open(url)
                self.set_status(f"✅ Открыто: {url}", "#4aff4a")
            else:
                self.set_status("❌ URL не указан", "#ff4a4a")
        
        elif action == "open_program":
            prog_path = self.prog_entry.get()
            if prog_path and os.path.exists(prog_path):
                try:
                    if self.admin_launch_var.get():
                        ctypes.windll.shell32.ShellExecuteW(
                            None, "runas", prog_path, "", None, 1)
                        self.set_status(f"✅ Запущено (Admin)", "#4aff4a")
                    else:
                        subprocess.Popen([prog_path])
                        self.set_status(f"✅ Запущено: {os.path.basename(prog_path)}", "#4aff4a")
                except Exception as e:
                    self.set_status(f"❌ Ошибка: {e}", "#ff4a4a")
            else:
                self.set_status("❌ Программа не найдена", "#ff4a4a")
        
        elif action == "close_program":
            process_name = self.process_entry.get().strip()
            if process_name:
                count = 0
                for proc in psutil.process_iter(['name']):
                    try:
                        if proc.info['name'].lower() == process_name.lower():
                            proc.kill()
                            count += 1
                    except:
                        pass
                if count > 0:
                    self.set_status(f"✅ Закрыто процессов: {count}", "#4aff4a")
                else:
                    self.set_status(f"⚠️ Процесс '{process_name}' не найден", "#ffaa4a")
            else:
                self.set_status("❌ Имя процесса не указано", "#ff4a4a")
    
    def _alarm_thread(self):
        for _ in range(3):
            if not self.alarm_playing:
                break
            self.play_alarm_sound()
            time.sleep(1)
        self.alarm_playing = False
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = BeautifulTimer()
    app.run()