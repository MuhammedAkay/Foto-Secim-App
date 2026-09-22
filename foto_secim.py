# -*- coding: utf-8 -*-
"""FotoSecim - Windows düğün fotoğrafı seçim uygulaması."""
import os
import sys
import shutil
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
try:
    from PIL import Image, ImageTk, ImageDraw, ImageFont
except ImportError:
    raise SystemExit("Pillow eksik. 'pip install -r requirements.txt' çalıştırın.")

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".tif", ".tiff"}

# Referans gorsele birebir koyu tema paleti
BG = "#0b1014"
OUTER = "#10161c"
PANEL = "#161e26"
PANEL2 = "#1b2530"
LINE = "#2d3a45"
GOLD = "#d3b48c"
GOLD_HOVER = "#e0c29a"
GOLD_DIM = "#8a755a"
TEXT = "#eef1f3"
MUTED = "#8b959d"
FIELD = "#1f2933"
BORDER = "#2e3c47"
THUMB = (178, 132)

class PhotoCard(tk.Frame):
    def __init__(self, master, path, on_click, on_double):
        super().__init__(master, bg=PANEL2, highlightbackground=LINE, highlightthickness=1, cursor="hand2")
        self.path = Path(path); self.on_click = on_click; self.on_double = on_double; self.selected = False; self.img_ref = None
        self.canvas = tk.Canvas(self, width=178, height=132, bg="#1a222a", highlightthickness=0)
        self.canvas.pack(padx=5, pady=5)
        self.canvas.bind("<Button-1>", self._click); self.canvas.bind("<Double-Button-1>", self._double)
        self.name = tk.Label(self, text=self.path.name, bg=PANEL2, fg="#dce1e4", font=("Segoe UI", 8), anchor="w")
        self.name.pack(fill="x", padx=7)
        self.name.bind("<Button-1>", self._click); self.name.bind("<Double-Button-1>", self._double)
        self.status = tk.Label(self, text="", bg=PANEL2, fg=GOLD, font=("Segoe UI", 8, "bold"))
        self.status.pack(fill="x", pady=(2, 5))
        for w in (self.status,): w.bind("<Button-1>", self._click)
        self.load(); self.refresh()

    def _click(self, e=None): self.on_click(self.path)
    def _double(self, e=None): self.on_double(self.path)

    def load(self):
        try:
            with Image.open(self.path) as im:
                im = im.convert("RGB"); im.thumbnail(THUMB, Image.Resampling.LANCZOS)
                bg = Image.new("RGB", THUMB, "#1a222a")
                bg.paste(im, ((THUMB[0] - im.width) // 2, (THUMB[1] - im.height) // 2))
                self.img_ref = ImageTk.PhotoImage(bg)
                self.canvas.create_image(THUMB[0] // 2, THUMB[1] // 2, image=self.img_ref)
        except Exception:
            self.canvas.create_text(89, 66, text="Önizleme\naçılamadı", fill="#aaa")

    def refresh(self):
        if self.selected:
            self.configure(bg="#20372a", highlightbackground=GOLD, highlightthickness=2)
            self.status.configure(text="✓ SEÇİLDİ", bg="#20372a", fg="#8be1a9")
        else:
            self.configure(bg=PANEL2, highlightbackground=LINE, highlightthickness=1)
            self.status.configure(text="", bg=PANEL2)

def draw_rr(cv, x0, y0, x1, y1, r, fill=None, outline=None, width=1, tags=()):
    r = max(1, min(r, (x1 - x0) / 2, (y1 - y0) / 2))
    if fill is not None:
        cv.create_rectangle(x0 + r, y0, x1 - r, y1, fill=fill, outline="", tags=tags)
        cv.create_rectangle(x0, y0 + r, x1, y1 - r, fill=fill, outline="", tags=tags)
        for ax, ay in ((x0, y0), (x1 - 2 * r, y0), (x0, y1 - 2 * r), (x1 - 2 * r, y1 - 2 * r)):
            cv.create_oval(ax, ay, ax + 2 * r, ay + 2 * r, fill=fill, outline="", tags=tags)
    if outline is not None:
        cv.create_line(x0 + r, y0, x1 - r, y0, fill=outline, width=width, tags=tags)
        cv.create_line(x0 + r, y1, x1 - r, y1, fill=outline, width=width, tags=tags)
        cv.create_line(x0, y0 + r, x0, y1 - r, fill=outline, width=width, tags=tags)
        cv.create_line(x1, y0 + r, x1, y1 - r, fill=outline, width=width, tags=tags)
        cv.create_arc(x0, y0, x0 + 2 * r, y0 + 2 * r, start=90, extent=90, style="arc", outline=outline, width=width, tags=tags)
        cv.create_arc(x1 - 2 * r, y0, x1, y0 + 2 * r, start=0, extent=90, style="arc", outline=outline, width=width, tags=tags)
        cv.create_arc(x0, y1 - 2 * r, x0 + 2 * r, y1, start=180, extent=90, style="arc", outline=outline, width=width, tags=tags)
        cv.create_arc(x1 - 2 * r, y1 - 2 * r, x1, y1, start=270, extent=90, style="arc", outline=outline, width=width, tags=tags)

class RoundedFrame(tk.Frame):
    def __init__(self, master, radius=10, fill=PANEL, outline=BORDER, border=1, **kw):
        super().__init__(master, bg=outline, **kw)
        self.body = tk.Frame(self, bg=fill)
        self.body.pack(fill="both", expand=True, padx=border, pady=border)

class GoldButton(tk.Canvas):
    def __init__(self, master, text, command, parent_bg, height=48, radius=8, font=("Segoe UI", 11, "bold"), width=None):
        super().__init__(master, bg=parent_bg, highlightthickness=0, bd=0, cursor="hand2", height=height)
        if width is not None:
            self.configure(width=width)
        self._gb_text = text
        self._gb_cmd = command
        self._gb_r = radius
        self._gb_font = font
        self._gb_hover = False
        self.bind("<Configure>", lambda e: self._gb_draw())
        self.bind("<Button-1>", lambda e: self._gb_cmd())
        self.bind("<Enter>", lambda e: self._gb_set(True))
        self.bind("<Leave>", lambda e: self._gb_set(False))
        self.after(10, self._gb_draw)

    def _gb_set(self, hover):
        self._gb_hover = hover
        self._gb_draw()

    def _gb_draw(self):
        try:
            w = self.winfo_width()
            h = self.winfo_height()
            if w < 10 or h < 10: return
            self.delete("gb")
            fill = GOLD_HOVER if self._gb_hover else GOLD
            draw_rr(self, 1, 1, w - 1, h - 1, self._gb_r, fill=fill, tags="gb")
            self.create_text(w / 2, h / 2, text=self._gb_text, fill="#12181f", font=self._gb_font, tags="gb")
        except Exception:
            pass

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FotoSecim • Düğün Fotoğraf Seçim Uygulaması")
        self.geometry("1280x800")
        self.minsize(1080, 700)
        self.configure(bg=BG)

        self.folder = None; self.photos = []; self.cards = {}; self.selected = set()
        self.normal_selection = set(); self.cover = None; self.table = None; self.mode = "normal"
        self.normal_count = 50; self.cover_required = True; self.table_required = True; self.output_dir = None

        self.folder_var = tk.StringVar(value="Klasör seçin...")
        self.output_name_var = tk.StringVar(value="")
        self.count_var = tk.IntVar(value=50)
        self.cover_var = tk.BooleanVar(value=True)
        self.table_var = tk.BooleanVar(value=True)
        self.cover_count_var = tk.IntVar(value=1)
        self.table_count_var = tk.IntVar(value=1)

        self._is_painting = False
        self._build_setup()
        self.bind("<Escape>", lambda e: self.go_setup())

    def clear(self):
        for w in self.winfo_children(): w.destroy()

    def gold_button(self, p, text, cmd, big=False):
        return tk.Button(p, text=text, command=cmd, bg=GOLD, fg="#11161a", activebackground=GOLD_HOVER, activeforeground="#11161a", relief="flat", bd=0, cursor="hand2", font=("Segoe UI", 12 if big else 10, "bold"), padx=18, pady=12 if big else 9)

    def dark_button(self, p, text, cmd):
        return tk.Button(p, text=text, command=cmd, bg=PANEL2, fg=TEXT, activebackground="#26343d", activeforeground="#fff", relief="flat", bd=0, cursor="hand2", font=("Segoe UI", 10, "bold"), padx=12, pady=9)

    def _topbar(self, parent):
        bar = tk.Frame(parent, bg="#0b1014", height=48)
        bar.pack(fill="x"); bar.pack_propagate(False)
        tk.Label(bar, text="📷  FotoSecim", bg="#0b1014", fg="#f0e0c4", font=("Segoe UI", 14, "bold")).pack(side="left", padx=22)
        tk.Label(bar, text="Düğün Fotoğraf Seçim Uygulaması", bg="#0b1014", fg="#7f8990", font=("Segoe UI", 9)).pack(side="left")

    def _resource(self, *parts):
        base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent)) if "__file__" in globals() else Path.cwd()
        return base.joinpath(*parts)

    def _build_setup(self):
        try:
            self._gallery_unbind()
        except Exception:
            pass
        self.clear()
        try:
            from PIL import Image as _PILImage
            bg_path = self._resource("assets", "bg_setup.jpg")
            if bg_path.exists():
                self._bg_src = _PILImage.open(str(bg_path)).convert("RGB")
            else:
                self._bg_src = None
        except Exception:
            self._bg_src = None

        self._bg_ref = None
        self._dim_ref = None
        self._setup_job = None

        root = tk.Frame(self, bg=BG)
        root.pack(fill="both", expand=True)

        cv = tk.Canvas(root, bg=BG, highlightthickness=0)
        cv.pack(fill="both", expand=True)
        self.setup_canvas = cv

        shell = tk.Frame(cv, bg=OUTER, highlightbackground="#26333e", highlightthickness=1, bd=0)
        self._setup_shell = shell

        inner = tk.Frame(shell, bg=OUTER)
        inner.pack(fill="both", expand=True, padx=14, pady=14)

        upper = tk.Frame(inner, bg=OUTER)
        upper.pack(fill="x")
        upper.grid_columnconfigure(0, weight=1)
        upper.grid_columnconfigure(1, weight=1)

        # 1. Album Bilgileri
        info = RoundedFrame(upper, radius=10, fill=PANEL, outline=BORDER)
        info.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        ibody = info.body

        h1 = tk.Frame(ibody, bg=PANEL)
        h1.pack(fill="x", padx=16, pady=(14, 10))
        tk.Label(h1, text="\U0001F4C1", bg=PANEL, fg=GOLD, font=("Segoe UI", 13)).pack(side="left", padx=(0, 8))
        tk.Label(h1, text="Albüm Bilgileri", bg=PANEL, fg=TEXT, font=("Segoe UI", 11, "bold")).pack(side="left")

        tk.Label(ibody, text="Albüm Klasörü", bg=PANEL, fg=TEXT, font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=16, pady=(0, 5))
        fr = tk.Frame(ibody, bg=PANEL)
        fr.pack(fill="x", padx=16, pady=(0, 12))
        fbox = RoundedFrame(fr, radius=6, fill=FIELD, outline=BORDER)
        fbox.pack(side="left", fill="x", expand=True, padx=(0, 8))
        folder_entry = tk.Entry(fbox.body, textvariable=self.folder_var, state="readonly", bg=FIELD, fg="#aeb7bd", readonlybackground=FIELD, relief="flat", bd=0, font=("Segoe UI", 9))
        folder_entry.pack(fill="x", padx=10, pady=9)

        fbtn_wrap = RoundedFrame(fr, radius=6, fill=GOLD, outline=GOLD, border=0)
        fbtn_wrap.pack(side="right")
        btn_folder = tk.Button(fbtn_wrap.body, text="\U0001F4C1", command=self.choose_folder, bg=GOLD, fg="#141a20", activebackground=GOLD_HOVER, activeforeground="#141a20", relief="flat", bd=0, font=("Segoe UI", 11), width=4, cursor="hand2")
        btn_folder.pack(padx=1, pady=1)

        tk.Label(ibody, text="Albüm Adı (Klasör Adı)", bg=PANEL, fg=TEXT, font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=16, pady=(0, 5))
        abox = RoundedFrame(ibody, radius=6, fill=FIELD, outline=BORDER)
        abox.pack(fill="x", padx=16, pady=(0, 16))
        self.album_entry = tk.Entry(abox.body, textvariable=self.output_name_var, bg=FIELD, fg=TEXT, insertbackground=TEXT, relief="flat", bd=0, font=("Segoe UI", 9))
        self.album_entry.pack(fill="x", padx=10, pady=9)

        self._album_placeholder = "Örn: Ayşe & Mehmet"
        def _album_focus_in(e=None):
            if self.output_name_var.get() == self._album_placeholder:
                self.output_name_var.set("")
                self.album_entry.configure(fg=TEXT)
        def _album_focus_out(e=None):
            if not self.output_name_var.get().strip():
                self.output_name_var.set(self._album_placeholder)
                self.album_entry.configure(fg="#7d888f")
        if not self.output_name_var.get().strip():
            self.output_name_var.set(self._album_placeholder)
            self.album_entry.configure(fg="#7d888f")
        self.album_entry.bind("<FocusIn>", _album_focus_in)
        self.album_entry.bind("<FocusOut>", _album_focus_out)

        # 2. Secim Sayilari
        counts = RoundedFrame(upper, radius=10, fill=PANEL, outline=BORDER)
        counts.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        cbody = counts.body

        h2 = tk.Frame(cbody, bg=PANEL)
        h2.pack(fill="x", padx=16, pady=(14, 10))
        tk.Label(h2, text="\U0001F5BC", bg=PANEL, fg=GOLD, font=("Segoe UI", 13)).pack(side="left", padx=(0, 8))
        tk.Label(h2, text="Seçim Sayıları", bg=PANEL, fg=TEXT, font=("Segoe UI", 11, "bold")).pack(side="left")

        self.count_spins = {}; self.count_badges = {}; self.count_labels = {}
        def count_row(label, var):
            row = tk.Frame(cbody, bg=PANEL)
            row.pack(fill="x", padx=16, pady=5)
            tk.Label(row, text="\U0001F5BC", bg=PANEL, fg="#9aa5ae", font=("Segoe UI", 12)).pack(side="left", padx=(0, 9))
            lb = tk.Label(row, text=label, bg=PANEL, fg=TEXT, font=("Segoe UI", 9))
            lb.pack(side="left")
            badge = tk.Label(row, text="(Zorunlu)", bg=PANEL, fg=MUTED, font=("Segoe UI", 8))
            badge.pack(side="right", padx=(6, 0))
            sbox = RoundedFrame(row, radius=6, fill=FIELD, outline=BORDER)
            sbox.pack(side="right")
            srow = tk.Frame(sbox.body, bg=FIELD)
            srow.pack(padx=2, pady=2)
            tk.Label(srow, text="\U0001F5BC", bg=FIELD, fg="#8b959d", font=("Segoe UI", 9)).pack(side="left", padx=(6, 2))
            tk.Frame(srow, bg=BORDER, width=1, height=18).pack(side="left", padx=4)
            spin = tk.Spinbox(srow, from_=1, to=500, textvariable=var, width=5, bg=FIELD, fg="#f0f2f4", buttonbackground=FIELD, relief="flat", bd=0, font=("Segoe UI", 10, "bold"), justify="center", disabledbackground=FIELD, disabledforeground="#5a656d", insertbackground=TEXT)
            spin.pack(side="left", padx=(0, 2))
            self.count_spins[label] = spin; self.count_badges[label] = badge; self.count_labels[label] = lb

        count_row("Normal Fotoğraf Sayısı", self.count_var)
        count_row("Albüm Kapağı", self.cover_count_var)
        count_row("Tablo Fotoğrafı", self.table_count_var)

        # 3. Ekstra Secenekler - tam genislik (Gorunum Ayarlari yok)
        extra = RoundedFrame(inner, radius=10, fill=PANEL, outline=BORDER)
        extra.pack(fill="x", pady=(12, 0))
        ebody = extra.body

        eh = tk.Frame(ebody, bg=PANEL)
        eh.pack(fill="x", padx=16, pady=(13, 1))
        tk.Label(eh, text="⚙", bg=PANEL, fg=GOLD, font=("Segoe UI", 13, "bold")).pack(side="left", padx=(0, 8))
        tk.Label(eh, text="Ekstra Seçenekler", bg=PANEL, fg=GOLD, font=("Segoe UI", 11, "bold")).pack(side="left")
        tk.Label(ebody, text="İhtiyacınıza göre ek seçimleri aktif edebilirsiniz.", bg=PANEL, fg=MUTED, font=("Segoe UI", 8)).pack(anchor="w", padx=16, pady=(0, 10))

        opts = tk.Frame(ebody, bg=PANEL)
        opts.pack(fill="x", padx=16, pady=(0, 14))
        opts.grid_columnconfigure(0, weight=1)
        opts.grid_columnconfigure(1, weight=1)

        def make_toggle(parent, var):
            cvs = tk.Canvas(parent, width=40, height=22, bg=PANEL2, highlightthickness=0, bd=0, cursor="hand2")
            def draw():
                on = bool(var.get())
                cvs.delete("all")
                draw_rr(cvs, 1, 1, 39, 21, 10, fill=(GOLD if on else "#39454f"), outline=(GOLD if on else "#4a565f"), width=1, tags="tg")
                x = 28 if on else 12
                cvs.create_oval(x - 7, 4, x + 7, 18, fill="#ffffff", outline="")
            draw()
            def flip(e=None):
                var.set(not var.get())
                draw()
                self._sync_optional_count_states()
            cvs.bind("<Button-1>", flip)
            var._toggle_draw = draw
            return cvs

        def option(icon, text, sub, var, column):
            box = RoundedFrame(opts, radius=8, fill=PANEL2, outline=BORDER)
            box.grid(row=0, column=column, sticky="ew", padx=4)
            top = tk.Frame(box.body, bg=PANEL2)
            top.pack(fill="x", padx=12, pady=10)
            tk.Label(top, text=icon, bg=PANEL2, fg=GOLD, font=("Segoe UI", 12)).pack(side="left", padx=(0, 10))
            tx = tk.Frame(top, bg=PANEL2)
            tx.pack(side="left", fill="x", expand=True)
            tk.Label(tx, text=text, bg=PANEL2, fg=TEXT, font=("Segoe UI", 9, "bold")).pack(anchor="w")
            tk.Label(tx, text=sub, bg=PANEL2, fg=MUTED, font=("Segoe UI", 8)).pack(anchor="w", pady=(2, 0))
            sw = make_toggle(top, var)
            sw.pack(side="right", padx=(6, 0))

        option("\U0001F5BC", "Albüm Kapağı Seç", "Kapak fotoğrafı seçimi yapılacak.", self.cover_var, 0)
        option("\U0001F5BC", "Tablo Fotoğrafı Seç", "Tablo fotoğrafı seçimi yapılacak.", self.table_var, 1)

        # 4. Basla - tam genislik gold
        GoldButton(inner, "▶      Başla", self.start, OUTER, height=48, radius=10, font=("Segoe UI", 12, "bold")).pack(fill="x", pady=(12, 0))

        self._setup_win = cv.create_window((0, 0), window=shell, anchor="n", width=860)
        self._sync_optional_count_states()

        def _on_cfg(e=None):
            if self._setup_job is not None:
                try: self.after_cancel(self._setup_job)
                except Exception: pass
            self._setup_job = self.after(150, self._setup_paint)
        cv.bind("<Configure>", _on_cfg)
        self.after(50, self._setup_paint)

    def _setup_paint(self):
        if getattr(self, "_is_painting", False): return
        self._is_painting = True
        self._setup_job = None
        cv = getattr(self, "setup_canvas", None)
        try:
            if cv is None or not cv.winfo_exists(): return
            w = cv.winfo_width(); h = cv.winfo_height()
            if w < 60 or h < 60: return

            cv.delete("bg", "dim", "hero", "foot")
            src = getattr(self, "_bg_src", None)
            if src is not None:
                from PIL import ImageEnhance
                s = max(w / src.width, h / src.height)
                nw, nh = max(1, int(src.width * s)), max(1, int(src.height * s))
                img = src.resize((nw, nh), Image.Resampling.BILINEAR)
                left, top = (nw - w) // 2, (nh - h) // 2
                img = img.crop((left, top, left + w, top + h))
                img = ImageEnhance.Brightness(img).enhance(0.48)
                self._bg_ref = ImageTk.PhotoImage(img)
                cv.create_image(0, 0, image=self._bg_ref, anchor="nw", tags="bg")

            cx = w // 2
            iy = 42

            # Kamera ikonu - gold kontur
            cv.create_rectangle(cx - 30, iy - 8, cx + 30, iy + 22, outline=GOLD, width=3, tags="hero")
            cv.create_oval(cx - 12, iy - 1, cx + 12, iy + 21, outline=GOLD, width=3, tags="hero")
            cv.create_oval(cx - 5, iy + 6, cx + 5, iy + 14, outline=GOLD, width=2, tags="hero")
            cv.create_rectangle(cx - 14, iy - 17, cx + 5, iy - 8, outline=GOLD, width=3, tags="hero")
            cv.create_oval(cx + 22, iy - 4, cx + 26, iy + 0, outline=GOLD, width=2, tags="hero")

            cv.create_text(cx - 6, iy + 52, text="Foto", anchor="e", fill="#f2f3f4", font=("Segoe UI", 30, "bold"), tags="hero")
            cv.create_text(cx - 2, iy + 52, text="Secim", anchor="w", fill=GOLD, font=("Segoe UI", 30, "bold"), tags="hero")

            cv.create_text(cx, iy + 88, text="Düğün Fotoğraflarınız İçin Hızlı ve Kolay Seçim", fill="#e8ebed", font=("Segoe UI", 12, "bold"), tags="hero")
            cv.create_rectangle(cx - 32, iy + 100, cx + 32, iy + 102, fill=GOLD, outline="", tags="hero")

            cv.create_text(cx, iy + 118, text="Müşterilerinizin fotoğraf seçimlerini kolaylaştırın.", fill="#a7b0b7", font=("Segoe UI", 9), tags="hero")
            cv.create_text(cx, iy + 135, text="Siz sadece en güzel anlara odaklanın.", fill="#a7b0b7", font=("Segoe UI", 9), tags="hero")

            try: cv.coords(self._setup_win, cx, iy + 158)
            except Exception: pass

            cv.create_rectangle(0, h - 34, w, h, fill="#090d10", outline="", tags="foot")
            cv.create_text(16, h - 17, text="ⓘ   FotoSecim v1.0    |    Düğün Fotoğraf Seçim Uygulaması", anchor="w", fill="#707a82", font=("Segoe UI", 8), tags="foot")
            cv.create_text(w - 16, h - 17, text="♡   Fotoğraf, en güzel hikayedir...", anchor="e", fill="#707a82", font=("Segoe UI", 8), tags="foot")
            cv.tag_lower("bg")
        finally:
            self._is_painting = False

    def _sync_optional_count_states(self):
        if not hasattr(self, "count_spins"): return
        for label, var in [("Alb\u00fcm Kapa\u011f\u0131", self.cover_var), ("Tablo Foto\u011fraf\u0131", self.table_var)]:
            on = bool(var.get())
            spin = self.count_spins.get(label)
            if spin is not None:
                try: spin.configure(state=("normal" if on else "disabled"))
                except Exception: pass
            badge = self.count_badges.get(label)
            if badge is not None:
                try: badge.configure(text="(Zorunlu)" if on else "(Kapal\u0131)", fg=MUTED if on else "#525b61")
                except Exception: pass

    def choose_folder(self):
        f = filedialog.askdirectory(title="Fotoğrafların bulunduğu klasörü seçin")
        if f: self.folder = Path(f); self.folder_var.set(str(self.folder))

    def start(self):
        if not self.folder: messagebox.showwarning("Klasör gerekli", "Önce fotoğrafların bulunduğu klasörü seçin."); return
        try: count = int(self.count_var.get())
        except: messagebox.showwarning("Geçersiz sayı", "Normal fotoğraf sayısını doğru girin."); return
        album_name = self.output_name_var.get().strip()
        if getattr(self, "_album_placeholder", None) and album_name == self._album_placeholder: album_name = ""
        if count < 1 or not album_name: messagebox.showwarning("Eksik bilgi", "Fotoğraf sayısı ve albüm adı boş olamaz."); return
        photos = sorted([p for p in self.folder.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS], key=lambda p: p.name.lower())
        
        try:
            cover_count = int(self.cover_count_var.get()) if self.cover_var.get() else 0
            table_count = int(self.table_count_var.get()) if self.table_var.get() else 0
        except Exception:
            messagebox.showwarning("Geçersiz sayı", "Kapak ve tablo adetlerini doğru girin."); return

        needed = count + cover_count + table_count
        if not photos: messagebox.showerror("Fotoğraf bulunamadı", "Klasörde desteklenen fotoğraf bulunamadı."); return
        if len(photos) < needed: messagebox.showwarning("Fotoğraf sayısı yetersiz", f"Klasörde {len(photos)} fotoğraf var; en az {needed} fotoğraf gerekiyor."); return
        
        self.photos = photos; self.normal_count = count; self.cover_required = self.cover_var.get(); self.table_required = self.table_var.get()
        self.output_dir = self.folder / album_name; self.selected.clear(); self.normal_selection.clear(); self.cover = None; self.table = None; self.mode = "normal"
        self.view_index = 0
        self._selection_page()

    def _selection_page(self):
        try:
            self.unbind_all("<MouseWheel>")
        except Exception:
            pass
        self.clear()
        if not getattr(self, "photos", None):
            self._build_setup()
            return
        if not hasattr(self, "view_index") or self.view_index is None:
            self.view_index = 0
        self.view_index = max(0, min(self.view_index, len(self.photos) - 1))
        self._thumb_refs = {}
        self._thumb_labels = {}
        self._viewer_ref = None
        self._viewer_job = None

        root = tk.Frame(self, bg=BG)
        root.pack(fill="both", expand=True)
        self._gal_root = root
        self._topbar(root)

        head = tk.Frame(root, bg=BG)
        head.pack(fill="x", padx=22, pady=(12, 6))
        left = tk.Frame(head, bg=BG)
        left.pack(side="left")
        self.step = tk.Label(left, text="", bg=BG, fg=GOLD, font=("Segoe UI", 15, "bold"))
        self.step.pack(anchor="w")
        self.sub = tk.Label(left, text="", bg=BG, fg=MUTED, font=("Segoe UI", 9))
        self.sub.pack(anchor="w", pady=(2, 0))

        right = tk.Frame(head, bg=BG)
        right.pack(side="right")
        self.counter = tk.Label(right, text="", bg=BG, fg=TEXT, font=("Segoe UI", 12, "bold"))
        self.counter.pack(anchor="e")
        self.progress = tk.Canvas(right, width=220, height=6, bg=BG, highlightthickness=0)
        self.progress.pack(anchor="e", pady=(6, 0))

        controls = tk.Frame(root, bg=BG)
        controls.pack(fill="x", padx=22, pady=(0, 8))
        self.dark_button(controls, "\u2190 Ayarlar", self.go_setup).pack(side="left")
        self.dark_button(controls, "\u21bb Temizle", self.clear_current).pack(side="left", padx=7)
        self.gold_button(controls, "\u0130LER\u0130  \u2192", self.next_step).pack(side="right")

        viewer_wrap = tk.Frame(root, bg=PANEL, highlightbackground=LINE, highlightthickness=1)
        viewer_wrap.pack(fill="both", expand=True, padx=22, pady=(0, 8))
        viewer_wrap.rowconfigure(0, weight=1)
        viewer_wrap.columnconfigure(1, weight=1)

        self.nav_prev = tk.Button(viewer_wrap, text="\u2039", command=self.gallery_prev, bg=PANEL, fg=GOLD, activebackground="#223039", activeforeground=GOLD, relief="flat", bd=0, cursor="hand2", font=("Segoe UI", 34, "bold"), width=2)
        self.nav_prev.grid(row=0, column=0, sticky="ns", padx=(4, 0), pady=4)
        self.nav_next = tk.Button(viewer_wrap, text="\u203a", command=self.gallery_next, bg=PANEL, fg=GOLD, activebackground="#223039", activeforeground=GOLD, relief="flat", bd=0, cursor="hand2", font=("Segoe UI", 34, "bold"), width=2)
        self.nav_next.grid(row=0, column=2, sticky="ns", padx=(0, 4), pady=4)

        center = tk.Frame(viewer_wrap, bg="#0c1116")
        center.grid(row=0, column=1, sticky="nsew", padx=4, pady=8)
        center.rowconfigure(0, weight=1)
        center.columnconfigure(0, weight=1)
        self.viewer_label = tk.Label(center, text="Y\u00fckleniyor...", bg="#0c1116", fg=MUTED, font=("Segoe UI", 11))
        self.viewer_label.grid(row=0, column=0, sticky="nsew")
        self.viewer_label.bind("<Configure>", self._viewer_cfg)
        self.viewer_label.bind("<Double-Button-1>", lambda e: self.open_photo(self.photos[self.view_index]))

        self.caption = tk.Label(center, text="", bg="#0c1116", fg="#c9d1d7", font=("Segoe UI", 9))
        self.caption.grid(row=1, column=0, sticky="ew", pady=(4, 2))
        self.badge = tk.Label(center, text="", bg="#0c1116", fg="#8be1a9", font=("Segoe UI", 10, "bold"))
        self.badge.grid(row=2, column=0, sticky="ew", pady=(0, 4))

        toolbar = tk.Frame(root, bg=PANEL, highlightbackground=LINE, highlightthickness=1)
        toolbar.pack(fill="x", padx=22, pady=(0, 8))
        bar = tk.Frame(toolbar, bg=PANEL)
        bar.pack(pady=8)
        self.tb_select = tk.Button(bar, text="\u2665  Se\u00e7", command=self.gallery_toggle_current, bg=GOLD, fg="#141a20", activebackground=GOLD_HOVER, relief="flat", bd=0, cursor="hand2", font=("Segoe UI", 11, "bold"), padx=22, pady=8)
        self.tb_select.pack(side="left", padx=5)
        self.tb_prev = tk.Button(bar, text="\u25c0 \u00d6nceki", command=self.gallery_prev, bg=PANEL2, fg=TEXT, activebackground="#26343d", relief="flat", bd=0, cursor="hand2", font=("Segoe UI", 10, "bold"), padx=14, pady=8)
        self.tb_prev.pack(side="left", padx=5)
        self.tb_next = tk.Button(bar, text="Sonraki \u25b6", command=self.gallery_next, bg=PANEL2, fg=TEXT, activebackground="#26343d", relief="flat", bd=0, cursor="hand2", font=("Segoe UI", 10, "bold"), padx=14, pady=8)
        self.tb_next.pack(side="left", padx=5)
        self.tb_compare = tk.Button(bar, text="\u25a6 Kar\u015f\u0131la\u015ft\u0131r", command=self.gallery_compare, bg=PANEL2, fg=TEXT, activebackground="#26343d", relief="flat", bd=0, cursor="hand2", font=("Segoe UI", 10, "bold"), padx=14, pady=8)
        self.tb_compare.pack(side="left", padx=5)
        self.tb_zoom = tk.Button(bar, text="\u26f6 B\u00fcy\u00fct", command=lambda: self.open_photo(self.photos[self.view_index]), bg=PANEL2, fg=TEXT, activebackground="#26343d", relief="flat", bd=0, cursor="hand2", font=("Segoe UI", 10, "bold"), padx=14, pady=8)
        self.tb_zoom.pack(side="left", padx=5)
        tk.Label(bar, text="\u2190 \u2192 gez \u2022 Space se\u00e7 \u2022 F b\u00fcy\u00fct", bg=PANEL, fg=MUTED, font=("Segoe UI", 8)).pack(side="left", padx=(12, 0))

        strip_wrap = tk.Frame(root, bg=PANEL, highlightbackground=LINE, highlightthickness=1)
        strip_wrap.pack(fill="x", padx=22, pady=(0, 14))
        self.strip_canvas = tk.Canvas(strip_wrap, bg=PANEL, highlightthickness=0, height=86)
        self.strip_canvas.pack(side="left", fill="x", expand=True, padx=(8, 0), pady=8)
        strip_sb = ttk.Scrollbar(strip_wrap, orient="horizontal", command=self.strip_canvas.xview)
        strip_sb.pack(side="bottom", fill="x", padx=8, pady=(0, 6))
        self.strip_canvas.configure(xscrollcommand=strip_sb.set)
        self.strip_inner = tk.Frame(self.strip_canvas, bg=PANEL)
        self._strip_win = self.strip_canvas.create_window((0, 0), window=self.strip_inner, anchor="nw")
        self.strip_inner.bind("<Configure>", lambda e: self.strip_canvas.configure(scrollregion=self.strip_canvas.bbox("all")))
        self.strip_canvas.bind("<MouseWheel>", self._strip_wheel)
        self.strip_canvas.bind("<Button-4>", lambda e: self.strip_canvas.xview_scroll(-1, "units"))
        self.strip_canvas.bind("<Button-5>", lambda e: self.strip_canvas.xview_scroll(1, "units"))

        self.bind("<Left>", lambda e: self.gallery_prev())
        self.bind("<Right>", lambda e: self.gallery_next())
        self.bind("<Up>", lambda e: self.gallery_prev())
        self.bind("<Down>", lambda e: self.gallery_next())
        self.bind("<space>", lambda e: self.gallery_toggle_current())
        self.bind("<Return>", lambda e: self.gallery_toggle_current())
        self.bind("<f>", lambda e: self.open_photo(self.photos[self.view_index]))
        self.bind("<F>", lambda e: self.open_photo(self.photos[self.view_index]))

        self._build_strip()
        self.gallery_show(self.view_index)
        self._update()

    def _strip_wheel(self, e=None):
        try:
            if e is not None and getattr(e, "delta", 0):
                self.strip_canvas.xview_scroll(int(-e.delta / 120), "units")
            else:
                self.strip_canvas.xview_scroll(1, "units")
        except Exception:
            pass

    def _viewer_cfg(self, e=None):
        if self._viewer_job is not None:
            try:
                self.after_cancel(self._viewer_job)
            except Exception:
                pass
        self._viewer_job = self.after(120, self._viewer_draw)

    def _viewer_draw(self):
        self._viewer_job = None
        if not hasattr(self, "viewer_label") or not self.viewer_label.winfo_exists():
            return
        if not getattr(self, "photos", None):
            return
        try:
            w = self.viewer_label.winfo_width()
            h = self.viewer_label.winfo_height()
            if w < 50 or h < 50:
                return
            path = self.photos[self.view_index]
            with Image.open(path) as im:
                im = im.convert("RGB")
                im.thumbnail((max(100, w - 20), max(100, h - 10)), Image.Resampling.LANCZOS)
                self._viewer_ref = ImageTk.PhotoImage(im.copy())
                self.viewer_label.configure(image=self._viewer_ref, text="")
        except Exception:
            try:
                self.viewer_label.configure(text="\u00d6nizleme a\u00e7\u0131lamad\u0131", image="")
            except Exception:
                pass

    def _build_strip(self):
        for w in self.strip_inner.winfo_children():
            w.destroy()
        self._thumb_refs = {}
        self._thumb_labels = {}
        for i, path in enumerate(self.photos):
            cell = tk.Frame(self.strip_inner, bg="#0c1116", highlightbackground=LINE, highlightthickness=1, cursor="hand2")
            cell.pack(side="left", padx=4)
            lab = tk.Label(cell, bg="#0c1116", fg=MUTED, font=("Segoe UI", 7), cursor="hand2")
            lab.pack(padx=3, pady=3)
            lab.bind("<Button-1>", lambda e, idx=i: self.gallery_show(idx))
            cell.bind("<Button-1>", lambda e, idx=i: self.gallery_show(idx))
            self._thumb_labels[path] = (cell, lab)
            try:
                with Image.open(path) as im:
                    im = im.convert("RGB")
                    im.thumbnail((104, 62), Image.Resampling.LANCZOS)
                    bg = Image.new("RGB", (104, 62), "#0c1116")
                    bg.paste(im, ((104 - im.width) // 2, (62 - im.height) // 2))
                    ref = ImageTk.PhotoImage(bg)
                    self._thumb_refs[path] = ref
                    lab.configure(image=ref)
            except Exception:
                lab.configure(text="...")
        self.after(50, self._strip_refresh)

    def _strip_refresh(self):
        try:
            for i, path in enumerate(self.photos):
                pair = self._thumb_labels.get(path)
                if not pair:
                    continue
                cell, lab = pair
                if i == getattr(self, "view_index", -1):
                    cell.configure(highlightbackground=GOLD, highlightthickness=2)
                elif path in self.selected:
                    cell.configure(highlightbackground="#3fae6a", highlightthickness=2)
                else:
                    cell.configure(highlightbackground=LINE, highlightthickness=1)
            try:
                cells = list(self.strip_inner.winfo_children())
                if 0 <= self.view_index < len(cells):
                    x = cells[self.view_index].winfo_x()
                    self.strip_canvas.xview_moveto(max(0, (x - 200) / max(1, self.strip_canvas.bbox("all")[2])))
            except Exception:
                pass
        except Exception:
            pass

    def gallery_show(self, idx):
        if not getattr(self, "photos", None):
            return
        self.view_index = max(0, min(idx, len(self.photos) - 1))
        self._viewer_draw()
        self._strip_refresh()
        self._update()

    def gallery_next(self, e=None):
        if not getattr(self, "photos", None):
            return
        if self.view_index < len(self.photos) - 1:
            self.gallery_show(self.view_index + 1)

    def gallery_prev(self, e=None):
        if not getattr(self, "photos", None):
            return
        if self.view_index > 0:
            self.gallery_show(self.view_index - 1)

    def gallery_toggle_current(self, e=None):
        if not getattr(self, "photos", None):
            return
        self.toggle(self.photos[self.view_index])

    def gallery_compare(self):
        messagebox.showinfo("Kar\u015f\u0131la\u015ft\u0131r", "Kar\u015f\u0131la\u015ft\u0131rma ekran\u0131 sonraki ad\u0131mda eklenecek. \u015eimdilik galeriden se\u00e7ime devam edebilirsiniz.")

    def reflow(self, width):
        return

    def _render(self):
        return

    def toggle(self, path):
        if self.mode == "normal":
            if path in self.selected:
                self.selected.remove(path)
            elif len(self.selected) < self.normal_count:
                self.selected.add(path)
            else:
                messagebox.showinfo("Limit doldu", f"En fazla {self.normal_count} normal foto\u011fraf se\u00e7ebilirsiniz.")
                return
        else:
            self.selected = {path}
        self.refresh()
        self._update()

    def refresh(self):
        if hasattr(self, "_thumb_labels"):
            self._strip_refresh()
        if hasattr(self, "viewer_label"):
            self._viewer_draw()

    def preview_photo(self, path):
        try:
            idx = self.photos.index(path)
            self.gallery_show(idx)
        except Exception:
            pass

    def _update(self):
        if not hasattr(self, "step") or not self.step.winfo_exists():
            return
        try:
            total = len(getattr(self, "photos", []))
            idx = getattr(self, "view_index", 0)
            cur = self.photos[idx] if total else None
            if self.mode == "normal":
                self.step.configure(text="1  \u2022  NORMAL FOTO\u011eRAFLAR")
                self.counter.configure(text=f"Se\u00e7ilen  {len(self.selected)} / {self.normal_count}")
                frac = (len(self.selected) / max(1, self.normal_count))
            elif self.mode == "cover":
                self.step.configure(text="2  \u2022  ALB\u00dcM KAPA\u011eI")
                self.counter.configure(text=f"Kapak  {1 if self.selected else 0} / 1")
                frac = (1 if self.selected else 0)
            else:
                self.step.configure(text="3  \u2022  TABLO FOTO\u011eRAFI")
                self.counter.configure(text=f"Tablo  {1 if self.selected else 0} / 1")
                frac = (1 if self.selected else 0)
            try:
                self.sub.configure(text=f"{total} foto\u011fraf  \u2022  {self.folder.name}  \u2022  {idx + 1} / {total}")
            except Exception:
                pass
            if cur is not None:
                try:
                    self.caption.configure(text=f"{idx + 1} / {total}  \u2022  {cur.name}")
                    if cur in self.selected:
                        self.badge.configure(text="\u2665 SE\u00c7\u0130LD\u0130  \u2713", fg="#8be1a9")
                    else:
                        self.badge.configure(text="", fg="#8be1a9")
                except Exception:
                    pass
                try:
                    if cur in self.selected:
                        self.tb_select.configure(bg="#3fae6a", activebackground="#4cc47e", text="\u2713  Se\u00e7ildi")
                    else:
                        self.tb_select.configure(bg=GOLD, activebackground=GOLD_HOVER, text="\u2665  Se\u00e7")
                except Exception:
                    pass
            try:
                self.progress.delete("all")
                w = 220
                self.progress.create_rectangle(0, 1, w, 5, fill="#222c35", outline="")
                self.progress.create_rectangle(0, 1, int(w * max(0, min(1, frac))), 5, fill=GOLD, outline="")
            except Exception:
                pass
        except Exception:
            pass

    def clear_current(self): self.selected.clear(); self.refresh(); self._update()

    def next_step(self):
        if self.mode == "normal":
            if len(self.selected) != self.normal_count: messagebox.showwarning("Seçim tamamlanmadı", f"Tam olarak {self.normal_count} normal fotoğraf seçmelisiniz."); return
            self.normal_selection = set(self.selected)
            if self.cover_required: self.mode = "cover"; self.selected.clear(); self.view_index = 0; self.show_cover_mode()
            elif self.table_required: self.mode = "table"; self.selected.clear(); self.view_index = 0; self._selection_refresh()
            else: self.finish()
        elif self.mode == "cover":
            if len(self.selected) != 1: messagebox.showwarning("Kapak seçilmedi", "Lütfen 1 adet kapak fotoğrafı seçin."); return
            self.cover = next(iter(self.selected))
            if self.table_required: self.mode = "table"; self.selected.clear(); self.view_index = 0; self._selection_refresh()
            else: self.finish()
        elif self.mode == "table":
            if len(self.selected) != 1: messagebox.showwarning("Tablo seçilmedi", "Lütfen 1 adet tablo fotoğrafı seçin."); return
            self.table = next(iter(self.selected)); self.finish()

    def _selection_refresh(self):
        self.view_index = 0
        self._selection_page()
    def show_cover_mode(self):
        self.view_index = 0
        self._selection_page()

    def open_photo(self, path):
        try:
            im = Image.open(path).convert("RGB"); im.thumbnail((1050, 700), Image.Resampling.LANCZOS); ref = ImageTk.PhotoImage(im.copy()); w = tk.Toplevel(self); w.title(path.name); w.configure(bg="#000"); tk.Label(w, image=ref, bg="#000").pack(padx=10, pady=10); w.image = ref
        except Exception as e: messagebox.showerror("Fotoğraf açılamadı", str(e))

    def _gallery_unbind(self):
        for seq in ("<Left>", "<Right>", "<Up>", "<Down>", "<space>", "<Return>", "<f>", "<F>"):
            try:
                self.unbind(seq)
            except Exception:
                pass

    def go_setup(self):
        self._gallery_unbind()
        if self.mode != "normal" and (self.normal_selection or self.selected):
            if not messagebox.askyesno("Ayarlar", "Ayarlar ekranına dönerseniz mevcut seçimler silinecek. Devam edilsin mi?"): return
        self._build_setup()

    def finish(self):
        if not self.normal_selection: messagebox.showerror("Hata", "Normal fotoğraf seçimi bulunamadı."); return
        out = self.output_dir
        if out.exists() and not messagebox.askyesno("Klasör zaten var", f"'{out.name}' klasörü zaten var. İçine kopyalansın mı?"): return
        try:
            out.mkdir(parents=True, exist_ok=True)
            for i, src in enumerate(sorted(self.normal_selection, key=lambda p: p.name.lower()), 1):
                shutil.copy2(src, out / f"{i:03d}{src.suffix.lower()}")
            if self.cover: shutil.copy2(self.cover, out / f"ALBUM_KAPAK{self.cover.suffix.lower()}")
            if self.table: shutil.copy2(self.table, out / f"TABLO{self.table.suffix.lower()}")
        except Exception as e: messagebox.showerror("Kopyalama hatası", str(e)); return
        messagebox.showinfo("Tamamlandı", f"Seçim tamamlandı!\n\nNormal: {len(self.normal_selection)}\nKapak: {'Evet' if self.cover else 'Hayır'}\nTablo: {'Evet' if self.table else 'Hayır'}\n\n{out}"); self._build_setup()

if __name__ == "__main__": App().mainloop()
