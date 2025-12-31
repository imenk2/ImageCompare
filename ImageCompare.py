import cv2
import numpy as np
import tkinter as tk
import os
import sys
from tkinter import filedialog, colorchooser
from PIL import Image, ImageTk, ImageDraw, ImageFont

# 自定义 UI 组件
class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command=None, width=150, height=40, corner_radius=10, 
                 bg_color="#db6300", hover_color="#ff8c00", text_color="white", font=('Microsoft YaHei UI', 10, 'bold')):
        super().__init__(parent, width=width, height=height, bg=parent['bg'], highlightthickness=0)
        self.command = command
        self.text = text
        self.radius = corner_radius
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = font
        
        self.normal_shape = self._draw_rounded_rect(0, 0, width, height, self.radius, self.bg_color)
        self.text_item = self.create_text(width/2, height/2, text=self.text, fill=self.text_color, font=self.font)
        
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _draw_rounded_rect(self, x, y, w, h, r, color):
        points = [x+r, y, x+w-r, y, x+w, y, x+w, y+r, x+w, y+h-r, x+w, y+h, x+w-r, y+h, x+r, y+h, x, y+h, x, y+h-r, x, y+r, x, y]
        return self.create_polygon(points, smooth=True, fill=color)

    def _on_click(self, event):
        if self.command:
            self.command()

    def _on_enter(self, event):
        self.itemconfig(self.normal_shape, fill=self.hover_color)

    def _on_leave(self, event):
        self.itemconfig(self.normal_shape, fill=self.bg_color)

class ModernSlider(tk.Canvas):
    """
    自定义圆形滑块的滑动条
    """
    def __init__(self, parent, from_=0, to=100, initial=0, command=None, width=200, height=30, 
                 bg_color="#2d2d2d", track_color="#404040", accent_color="#db6300"):
        super().__init__(parent, width=width, height=height, bg=bg_color, highlightthickness=0)
        self.command = command
        self.min_val = from_
        self.max_val = to
        self.cur_val = initial
        self.width = width
        self.height = height
        
        self.track_color = track_color
        self.accent_color = accent_color
        
        # 布局参数
        self.padding = 10  # 左右内边距，给圆形按钮留空间
        self.track_h = 4   # 轨道高度
        self.knob_r = 8    # 按钮半径
        
        # 绘制轨道背景
        cy = self.height / 2
        self.track_bg = self.create_line(self.padding, cy, self.width - self.padding, cy, 
                                         fill=self.track_color, width=self.track_h, capstyle=tk.ROUND)
        
        # 绘制进度高亮 (可选)
        self.track_fill = self.create_line(self.padding, cy, self.padding, cy, 
                                           fill=self.accent_color, width=self.track_h, capstyle=tk.ROUND)
        
        # 绘制圆形按钮 (Knob)
        self.knob = self.create_oval(0, 0, 0, 0, fill=self.accent_color, outline="white", width=1)
        
        self.update_graphics()
        
        self.bind("<Button-1>", self._on_click)
        self.bind("<B1-Motion>", self._on_drag)
        self.bind("<Configure>", self._on_resize)

    def _val_to_x(self, val):
        safe_val = max(self.min_val, min(val, self.max_val))
        ratio = (safe_val - self.min_val) / (self.max_val - self.min_val) if self.max_val > self.min_val else 0
        track_len = self.winfo_width() - 2 * self.padding
        return self.padding + ratio * track_len

    def _x_to_val(self, x):
        track_len = self.winfo_width() - 2 * self.padding
        if track_len <= 0: return self.min_val
        ratio = (x - self.padding) / track_len
        ratio = max(0.0, min(1.0, ratio))
        return self.min_val + ratio * (self.max_val - self.min_val)

    def update_graphics(self):
        # 此时 self.winfo_width() 可能还未更新，使用 self.width 兜底
        w = self.winfo_width() if self.winfo_width() > 1 else self.width
        
        cy = self.height / 2
        
        # 更新轨道长度
        self.coords(self.track_bg, self.padding, cy, w - self.padding, cy)
        
        # 更新按钮位置
        x = self._val_to_x(self.cur_val)
        
        # 更新进度条
        self.coords(self.track_fill, self.padding, cy, x, cy)
        
        # 更新圆钮
        r = self.knob_r
        self.coords(self.knob, x - r, cy - r, x + r, cy + r)

    def _on_click(self, event):
        val = self._x_to_val(event.x)
        self.set(val)
        if self.command:
            self.command(val)

    def _on_drag(self, event):
        val = self._x_to_val(event.x)
        self.set(val)
        if self.command:
            self.command(val)

    def _on_resize(self, event):
        self.width = event.width
        self.update_graphics()

    def set(self, value):
        self.cur_val = max(self.min_val, min(value, self.max_val))
        self.update_graphics()
        
    def get(self):
        return self.cur_val

    def set_range(self, from_, to):
        self.min_val = from_
        self.max_val = to
        # 范围改变后，重新确保当前值在范围内
        self.set(self.cur_val)

class ModernPopup(tk.Toplevel):
    def __init__(self, parent, title, message, is_error=False):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x250")
        self.resizable(False, False)
        
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - 200
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - 125
        self.geometry(f"+{x}+{y}")

        bg_color = '#1e1e1e'
        fg_color = '#e0e0e0'
        accent_color = '#db6300'
        
        self.configure(bg=bg_color)
        self.transient(parent)
        self.grab_set()

        frame = tk.Frame(self, bg=bg_color, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        icon_text = "❌ 错误" if is_error else "ℹ️ 提示"
        tk.Label(frame, text=icon_text, bg=bg_color, fg=accent_color, 
                 font=('Microsoft YaHei UI', 16, 'bold')).pack(pady=(0, 15))

        msg_label = tk.Label(frame, text=message, bg=bg_color, fg=fg_color, 
                             font=('Microsoft YaHei UI', 10), wraplength=350, justify=tk.LEFT)
        msg_label.pack(expand=True, fill=tk.BOTH)

        btn = RoundedButton(frame, text="确 定", command=self.destroy, width=100, height=35)
        btn.pack(side=tk.BOTTOM, pady=10)
        
        self.bind('<Return>', lambda e: self.destroy())
        self.bind('<Escape>', lambda e: self.destroy())

# 主程序
class ImageComparer:
    def __init__(self, root_window):
        self.root = root_window
        self.root.title("图片比较 - 专业版")
        self.root.geometry("1000x700")
        self.root.minsize(900, 600)

        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
        
        icon_path = os.path.join(base_path, "app.ico")
        try:
            self.root.iconbitmap(icon_path)
        except:
            pass

        self.colors = {
            'bg': '#1e1e1e',
            'toolbar': '#2d2d2d',
            'toolbar_hover': '#3d3d3d',
            'text': '#e0e0e0',
            'text_secondary': '#a0a0a0',
            'accent': "#db6300",
            'accent_hover': '#ff8c00',
            'border': '#404040',
            'input': '#3c3c3c',
            'canvas': '#252526'
        }
        
        self.root.configure(bg=self.colors['bg'])

        self.img_a_cv = None
        self.img_b_cv = None
        self.img_a_final = None
        self.img_b_final = None
        self.img_combined_bgr = None
        self.combined_image_pil = None
        self.diff_mask = None
        self.diff_overlay = None

        self.line_color = "#ff0000"
        self.line_thickness = 2
        self.line_style = "solid"
        self.show_line = True
        self.show_diff = False
        self.diff_threshold = 30
        self.split_x = 0
        self.is_dragging = False

        self.ctrl_pressed = False
        self.magnifier_zoom = 4.0
        self.magnifier_size = 150
        self.mouse_x = 0
        self.mouse_y = 0
        self.last_mouse_x = 0
        self.last_mouse_y = 0

        self.create_ui()
        self.show_initial_message()
        
        self.root.bind('<KeyPress-a>', self.fine_tune_left)
        self.root.bind('<KeyPress-d>', self.fine_tune_right)
        self.root.bind('<KeyPress-l>', self.toggle_line_display)
        self.root.bind('<KeyPress-k>', self.toggle_diff_display)
        self.root.bind('<Control_L>', self.on_ctrl_press)
        self.root.bind('<Control_R>', self.on_ctrl_press)
        self.root.bind('<KeyRelease-Control_L>', self.on_ctrl_release)
        self.root.bind('<KeyRelease-Control_R>', self.on_ctrl_release)
        self.root.bind('<MouseWheel>', self.on_mouse_wheel)

    def create_ui(self):
        self.main_container = tk.Frame(self.root, bg=self.colors['bg'])
        self.main_container.pack(fill=tk.BOTH, expand=True)

        self.create_toolbar()
        self.create_import_buttons()
        self.create_canvas()
        self.create_slider()

    def create_import_buttons(self):
        import_frame = tk.Frame(self.main_container, bg=self.colors['bg'], height=60)
        import_frame.pack(side=tk.TOP, fill=tk.X, padx=0, pady=10)
        import_frame.pack_propagate(False)

        btn_a = RoundedButton(import_frame, text="📁 导入图片A", command=self.load_image_a, 
                              width=140, height=40, bg_color=self.colors['accent'], hover_color=self.colors['accent_hover'])
        btn_a.pack(side=tk.LEFT, padx=20)

        btn_b = RoundedButton(import_frame, text="📁 导入图片B", command=self.load_image_b, 
                              width=140, height=40, bg_color=self.colors['accent'], hover_color=self.colors['accent_hover'])
        btn_b.pack(side=tk.RIGHT, padx=20)

    def create_toolbar(self):
        toolbar = tk.Frame(self.main_container, bg=self.colors['toolbar'], height=50)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=0, pady=0)
        toolbar.pack_propagate(False)

        btn_style = {
            'bg': self.colors['toolbar'], 'fg': self.colors['text'],
            'activebackground': self.colors['toolbar_hover'], 'activeforeground': self.colors['text'],
            'relief': tk.FLAT, 'bd': 0, 'padx': 10, 'pady': 5, 'font': ('Microsoft YaHei UI', 9)
        }
        label_style = {'bg': self.colors['toolbar'], 'fg': self.colors['text_secondary'], 'font': ('Microsoft YaHei UI', 8)}

        def add_sep():
            tk.Frame(toolbar, bg=self.colors['border'], width=1).pack(side=tk.LEFT, fill=tk.Y, padx=8, pady=10)

        # 中线设置
        tk.Label(toolbar, text="中线:", **label_style).pack(side=tk.LEFT, padx=5)
        self.show_line_var = tk.BooleanVar(value=True)
        tk.Checkbutton(toolbar, text="显示", variable=self.show_line_var, command=self.on_checkbutton_toggle,
                      bg=self.colors['toolbar'], fg=self.colors['text'], selectcolor=self.colors['input'], 
                      activebackground=self.colors['toolbar'], bd=0).pack(side=tk.LEFT)

        self.btn_color = tk.Button(toolbar, text="   ", bg=self.line_color, relief=tk.FLAT, command=self.choose_line_color)
        self.btn_color.pack(side=tk.LEFT, padx=5, ipady=2)

        # 使用 ModernSlider  自定义组件
        self.thickness_scale = ModernSlider(toolbar, from_=1, to=10, initial=self.line_thickness, 
                                           command=self.on_thickness_change, width=80, height=24, bg_color=self.colors['toolbar'])
        self.thickness_scale.pack(side=tk.LEFT, padx=5)

        self.line_style_var = tk.StringVar(value="solid")
        om = tk.OptionMenu(toolbar, self.line_style_var, "dashed", "solid", "dotted", command=self.on_style_change)
        om.config(bg=self.colors['toolbar'], fg=self.colors['text'], highlightthickness=0, bd=0, relief=tk.FLAT)
        om["menu"].config(bg=self.colors['toolbar'], fg=self.colors['text'])
        om.pack(side=tk.LEFT)

        add_sep()

        # 差异设置
        tk.Label(toolbar, text="差异:", **label_style).pack(side=tk.LEFT, padx=5)
        self.show_diff_var = tk.BooleanVar(value=False)
        tk.Checkbutton(toolbar, text="高亮", variable=self.show_diff_var, command=self.on_diff_toggle,
                      bg=self.colors['toolbar'], fg=self.colors['text'], selectcolor=self.colors['input'], 
                      activebackground=self.colors['toolbar'], bd=0).pack(side=tk.LEFT)
        
        tk.Label(toolbar, text="阈值", **label_style).pack(side=tk.LEFT)
        
        # 使用 ModernSlider 自定义组件
        self.threshold_scale = ModernSlider(toolbar, from_=0, to=100, initial=self.diff_threshold,
                                           command=self.on_threshold_change, width=100, height=24, bg_color=self.colors['toolbar'])
        self.threshold_scale.pack(side=tk.LEFT, padx=5)

        self.diff_info_label = tk.Label(toolbar, text="0%", **label_style)
        self.diff_info_label.pack(side=tk.LEFT, padx=5)

        add_sep()
        
        tk.Button(toolbar, text="💾 保存GIF", command=self.save_gif_animation, **btn_style).pack(side=tk.LEFT)
        add_sep()
        tk.Button(toolbar, text="❓ 帮助", command=self.show_shortcuts_help, **btn_style).pack(side=tk.LEFT)

    def create_canvas(self):
        canvas_container = tk.Frame(self.main_container, bg=self.colors['canvas'])
        canvas_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(canvas_container, bg=self.colors['canvas'], highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<Motion>", self.on_mouse_move)

    def create_slider(self):
        self.slider_frame = tk.Frame(self.main_container, bg=self.colors['toolbar'])
        tk.Label(self.slider_frame, text="拖动滑块或按 A/D 微调", 
                bg=self.colors['toolbar'], fg=self.colors['text_secondary'],
                font=('Microsoft YaHei UI', 8)).pack(side=tk.LEFT, padx=10)
        
        # 使用 ModernSlider 替换 主 Scale
        self.slider = ModernSlider(self.slider_frame, from_=0, to=100, command=self.redraw, 
                                  width=500, height=30, bg_color=self.colors['toolbar'])
        self.slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        self.slider_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

    # 逻辑代码
    def apply_magnifier_overlay(self, display_img_bgr):
        if not self.ctrl_pressed or self.img_combined_bgr is None:
            return display_img_bgr
            
        h_disp, w_disp = display_img_bgr.shape[:2]
        h_src, w_src = self.img_combined_bgr.shape[:2]
        
        mx_canvas, my_canvas = self.mouse_x, self.mouse_y
        rel_x = mx_canvas - self.display_offset_x
        rel_y = my_canvas - self.display_offset_y
        
        if not (0 <= rel_x < w_disp and 0 <= rel_y < h_disp):
            return display_img_bgr

        src_cx = int(rel_x / self.display_scale)
        src_cy = int(rel_y / self.display_scale)
        
        zoom = self.magnifier_zoom
        box_size = self.magnifier_size
        
        crop_radius = int(box_size / zoom / 2)
        x1 = max(0, src_cx - crop_radius)
        y1 = max(0, src_cy - crop_radius)
        x2 = min(w_src, src_cx + crop_radius)
        y2 = min(h_src, src_cy + crop_radius)
        
        if x2 <= x1 or y2 <= y1: return display_img_bgr
        
        src_patch = self.img_combined_bgr[y1:y2, x1:x2]
        zoomed_patch = cv2.resize(src_patch, (box_size, box_size), interpolation=cv2.INTER_NEAREST)

        offset = 20
        pos_x = rel_x + offset
        pos_y = rel_y + offset
        
        if pos_x + box_size > w_disp:
            pos_x = rel_x - offset - box_size
        if pos_y + box_size > h_disp:
            pos_y = rel_y - offset - box_size

        pos_x = max(0, min(pos_x, w_disp - box_size))
        pos_y = max(0, min(pos_y, h_disp - box_size))
        
        dx1, dy1 = int(pos_x), int(pos_y)
        dx2, dy2 = dx1 + box_size, dy1 + box_size

        cv2.rectangle(display_img_bgr, (dx1-1, dy1-1), (dx2+1, dy2+1), (255, 255, 255), 1)
        cv2.rectangle(display_img_bgr, (dx1-2, dy1-2), (dx2+2, dy2+2), (0, 0, 0), 2)
        
        try:
            display_img_bgr[dy1:dy2, dx1:dx2] = zoomed_patch
        except ValueError:
            pass
        
        cx, cy = dx1 + box_size // 2, dy1 + box_size // 2
        cv2.line(display_img_bgr, (cx, dy1), (cx, dy2), (0, 255, 0), 1)
        cv2.line(display_img_bgr, (dx1, cy), (dx2, cy), (0, 255, 0), 1)

        try:
            b, g, r_val = self.img_combined_bgr[src_cy, src_cx]
            info_text = f"RGB: {r_val},{g},{b}"
            
            text_bg_h = 24
            text_y1 = dy2 - text_bg_h
            text_y2 = dy2
            
            if text_y1 >= 0 and text_y2 <= h_disp:
                cv2.rectangle(display_img_bgr, (dx1, text_y1), (dx2, text_y2), (20, 20, 20), -1)
                swatch_size = 12
                sx1 = dx1 + 8
                sy1 = text_y1 + (text_bg_h - swatch_size) // 2
                cv2.rectangle(display_img_bgr, (sx1, sy1), (sx1+swatch_size, sy1+swatch_size), 
                             (int(b), int(g), int(r_val)), -1)
                cv2.rectangle(display_img_bgr, (sx1, sy1), (sx1+swatch_size, sy1+swatch_size), 
                             (200, 200, 200), 1)
                cv2.putText(display_img_bgr, info_text, (sx1 + swatch_size + 8, text_y2 - 6), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.45, (230, 230, 230), 1, cv2.LINE_AA)
        except:
            pass

        return display_img_bgr

    def update_image_display(self):
        if self.combined_image_pil is None: return
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1: return
        
        img_width, img_height = self.combined_image_pil.size
        scale_x = canvas_width / img_width
        scale_y = canvas_height / img_height
        self.display_scale = min(scale_x, scale_y)
        
        new_width = int(img_width * self.display_scale)
        new_height = int(img_height * self.display_scale)
        
        resized_pil = self.combined_image_pil.resize((new_width, new_height), Image.Resampling.LANCZOS)
        display_img = np.array(resized_pil)
        display_img = cv2.cvtColor(display_img, cv2.COLOR_RGB2BGR)
        
        self.display_offset_x = (canvas_width - new_width) // 2
        self.display_offset_y = (canvas_height - new_height) // 2
        
        if self.ctrl_pressed:
            display_img = self.apply_magnifier_overlay(display_img)

        display_img = cv2.cvtColor(display_img, cv2.COLOR_BGR2RGB)
        final_pil = Image.fromarray(display_img)
        self.combined_photo = ImageTk.PhotoImage(image=final_pil)
        
        self.canvas.delete("all")
        self.canvas.create_image(self.display_offset_x, self.display_offset_y, anchor="nw", image=self.combined_photo)
        self.canvas.image = self.combined_photo

    def on_mouse_move(self, event):
        if self.img_a_final is None: return
        self.mouse_x = event.x
        self.mouse_y = event.y
        if self.ctrl_pressed:
            if abs(self.mouse_x - self.last_mouse_x) > 1 or abs(self.mouse_y - self.last_mouse_y) > 1:
                self.update_image_display()
                self.last_mouse_x = self.mouse_x
                self.last_mouse_y = self.mouse_y

    def on_mouse_wheel(self, event):
        if self.ctrl_pressed:
            delta = 1.0 if event.delta > 0 else -1.0
            self.magnifier_zoom = max(1.0, min(16.0, self.magnifier_zoom + delta))
            self.update_image_display()

    def show_initial_message(self):
        canvas_width = 800
        canvas_height = 500
        canvas = Image.new('RGB', (canvas_width, canvas_height), color=(30, 30, 30))
        draw = ImageDraw.Draw(canvas)
        
        try:
            font_large = ImageFont.truetype("msyh.ttc", 32)
            font_small = ImageFont.truetype("msyh.ttc", 20)
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        w, h = canvas_width, canvas_height
        msg1 = "请导入图片 A 与 图片 B"
        msg2 = "按住 Ctrl 移动鼠标可使用放大镜"
        
        draw.text((w//2 - 150, h//2 - 50), msg1, fill=(200, 200, 200), font=font_large)
        draw.text((w//2 - 140, h//2 + 10), msg2, fill=(150, 150, 150), font=font_small)
        
        self.combined_image_pil = canvas
        self.img_combined_bgr = cv2.cvtColor(np.array(canvas), cv2.COLOR_RGB2BGR)
        self.root.after(100, self.update_image_display)

    def load_image(self, side):
        path = filedialog.askopenfilename(title=f'请选择图片 {side}', filetypes=[('Images', '*.jpg *.jpeg *.png *.bmp *.tiff *.tif')])
        if not path: return

        try:
            image = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)
            if image is None: raise ValueError("Image decode failed")
        except Exception as e:
            ModernPopup(self.root, "错误", f"无法读取图片 {side}！\n{e}", is_error=True)
            return
            
        if side == 'A':
            self.img_a_cv = image
            if self.img_b_cv is not None: self.prepare_images()
        else:
            self.img_b_cv = image
            if self.img_a_cv is not None: self.prepare_images()

    def load_image_a(self): self.load_image('A')
    def load_image_b(self): self.load_image('B')

    def prepare_images(self):
        if self.img_a_cv is None or self.img_b_cv is None: return

        target_h, target_w, _ = self.img_a_cv.shape
        self.img_a_final = self.img_a_cv.copy()
        
        if self.img_b_cv.shape[:2] != (target_h, target_w):
            self.img_b_final = cv2.resize(self.img_b_cv, (target_w, target_h))
        else:
            self.img_b_final = self.img_b_cv.copy()

        self.calculate_diff()
        
        # 更新 ModernSlider 的范围
        self.slider.set_range(0, target_w)
        self.split_x = target_w // 2
        self.slider.set(self.split_x)
        self.redraw(self.split_x)

    def calculate_diff(self):
        if self.img_a_final is None or self.img_b_final is None: return
        diff = cv2.absdiff(self.img_a_final, self.img_b_final)
        gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        _, thresholded = cv2.threshold(gray_diff, self.diff_threshold, 255, cv2.THRESH_BINARY)
        self.diff_mask = thresholded
        
        diff_pixels = np.count_nonzero(thresholded)
        total_pixels = thresholded.size
        diff_percent = (diff_pixels / total_pixels) * 100
        self.diff_info_label.config(text=f"差异: {diff_percent:.2f}%")

        self.diff_overlay = np.zeros_like(self.img_a_final)
        self.diff_overlay[thresholded > 0] = [0, 0, 255]

    def redraw(self, value):
        if self.img_a_final is None or self.img_b_final is None: return

        split_x = int(value)
        h, w, _ = self.img_a_final.shape
        
        canvas = np.zeros((h, w, 3), dtype=np.uint8)
        
        if split_x > 0:
            canvas[:, 0:split_x] = self.img_a_final[:, 0:split_x]
        if split_x < w:
            canvas[:, split_x:w] = self.img_b_final[:, split_x:w]
        
        if self.show_diff and self.diff_overlay is not None:
            canvas = cv2.addWeighted(canvas, 1, self.diff_overlay, 0.5, 0)
        
        if self.show_line:
            bgr_color = self.hex_to_bgr(self.line_color)
            self.draw_line(canvas, (split_x, 0), (split_x, h), bgr_color, 
                          self.line_thickness, self.line_style)

        self.img_combined_bgr = canvas
        img_rgb = cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB)
        self.combined_image_pil = Image.fromarray(img_rgb)
        
        self.update_image_display()

    def on_canvas_click(self, event):
        if self.img_a_final is None: return
        if not hasattr(self, 'display_scale') or self.display_scale == 0: return
        
        offset_x = self.display_offset_x
        click_x = event.x - offset_x
        img_width = self.img_a_final.shape[1]
        display_width = img_width * self.display_scale
        
        if 0 <= click_x <= display_width:
            self.split_x = int(click_x / self.display_scale)
            self.split_x = max(0, min(self.split_x, img_width))
            self.slider.set(self.split_x)
            self.redraw(self.split_x) # 显式调用 redraw，因为 set() 只是更新 UI
            self.is_dragging = True

    def on_canvas_drag(self, event):
        if not self.is_dragging or self.img_a_final is None: return
        offset_x = self.display_offset_x
        drag_x = event.x - offset_x
        img_width = self.img_a_final.shape[1]
        self.split_x = max(0, min(int(drag_x / self.display_scale), img_width))
        self.slider.set(self.split_x)
        self.redraw(self.split_x)

    def on_canvas_release(self, event): self.is_dragging = False

    def on_canvas_configure(self, event):
        if self.combined_image_pil:
            self.update_image_display()

    def choose_line_color(self):
        color = colorchooser.askcolor(title="选择中线颜色", initialcolor=self.line_color)
        if color[1]:
            self.line_color = color[1]
            self.btn_color.config(bg=self.line_color)
            if self.img_a_final is not None: self.redraw(self.slider.get())

    def on_thickness_change(self, value):
        self.line_thickness = int(value)
        if self.img_a_final is not None: self.redraw(self.slider.get())

    def on_style_change(self, value):
        self.line_style = value
        if self.img_a_final is not None: self.redraw(self.slider.get())

    def on_checkbutton_toggle(self):
        self.show_line = self.show_line_var.get()
        if self.img_a_final is not None: self.redraw(self.slider.get())

    def on_diff_toggle(self):
        self.show_diff = self.show_diff_var.get()
        if self.img_a_final is not None: self.redraw(self.slider.get())

    def on_threshold_change(self, value):
        self.diff_threshold = int(value)
        if self.img_a_final is not None:
            self.calculate_diff()
            self.redraw(self.slider.get())

    def draw_line(self, img, start_pos, end_pos, color, thickness, style):
        if style == "solid":
            cv2.line(img, start_pos, end_pos, color, thickness)
        elif style == "dashed":
            self.draw_dashed_line(img, start_pos, end_pos, color, thickness, 10, 7)
        elif style == "dotted":
            self.draw_dashed_line(img, start_pos, end_pos, color, thickness, 2, 4)

    def draw_dashed_line(self, img, start_pos, end_pos, color, thickness, dash_len, gap_len):
        x0, y0 = start_pos
        x1, y1 = end_pos
        dist = ((x1-x0)**2 + (y1-y0)**2)**0.5
        if dist == 0: return
        vx, vy = (x1-x0)/dist, (y1-y0)/dist
        curr = 0
        while curr < dist:
            p1 = (int(x0 + vx*curr), int(y0 + vy*curr))
            p2 = (int(x0 + vx*min(curr+dash_len, dist)), int(y0 + vy*min(curr+dash_len, dist)))
            cv2.line(img, p1, p2, color, thickness)
            curr += dash_len + gap_len

    def hex_to_bgr(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (4, 2, 0))

    def on_ctrl_press(self, event):
        self.ctrl_pressed = True
        self.canvas.config(cursor="plus")
        if self.img_a_final is not None: self.update_image_display()

    def on_ctrl_release(self, event):
        self.ctrl_pressed = False
        self.canvas.config(cursor="")
        if self.img_a_final is not None: self.update_image_display()

    def save_gif_animation(self):
        if self.img_a_final is None: return
        path = filedialog.asksaveasfilename(defaultextension='.gif', filetypes=[('GIF', '*.gif')])
        if not path: return
        
        try:
            frames = []
            h, w, _ = self.img_a_final.shape
            bgr_color = self.hex_to_bgr(self.line_color)
            
            for i in range(0, 101, 5):
                split_x = int(w * i / 100)
                canvas = np.zeros((h, w, 3), dtype=np.uint8)
                canvas[:, 0:split_x] = self.img_a_final[:, 0:split_x]
                canvas[:, split_x:w] = self.img_b_final[:, split_x:w]
                
                if self.show_line:
                    cv2.line(canvas, (split_x, 0), (split_x, h), bgr_color, 2)

                img_rgb = cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB)
                frames.append(Image.fromarray(img_rgb).resize((w//2, h//2)))

            frames[0].save(path, save_all=True, append_images=frames[1:], duration=100, loop=0)
            ModernPopup(self.root, "成功", "GIF 动画已保存！")
        except Exception as e:
            ModernPopup(self.root, "错误", str(e), is_error=True)

    def show_shortcuts_help(self):
        msg = ("• 按住 Ctrl + 移动鼠标：开启像素放大镜\n"
               "• 鼠标滚轮：调整放大镜倍率\n"
               "• 键盘 A / D：微调中线位置\n"
               "• 键盘 L：快速显示/隐藏中线\n"
               "• 键盘 K：快速显示/隐藏差异高亮")
        ModernPopup(self.root, "操作指南", msg)
    
    def fine_tune_left(self, event): 
        if self.img_a_final is not None: 
            val = self.slider.get() - 1
            self.slider.set(val)
            self.redraw(val)

    def fine_tune_right(self, event): 
        if self.img_a_final is not None: 
            val = self.slider.get() + 1
            self.slider.set(val)
            self.redraw(val)

    def toggle_line_display(self, event):
        self.show_line_var.set(not self.show_line_var.get())
        self.on_checkbutton_toggle()
    def toggle_diff_display(self, event):
        self.show_diff_var.set(not self.show_diff_var.get())
        self.on_diff_toggle()

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageComparer(root)
    root.mainloop()