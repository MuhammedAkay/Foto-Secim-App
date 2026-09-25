# -*- coding: utf-8 -*-
"""FotoSecim - Windows düğün fotoğrafı seçim uygulaması."""
import hashlib
import os
import sys
import shutil
import tempfile
from collections import OrderedDict
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog
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
        self.title("FotoSecim v2.0 • Düğün Fotoğraf Seçim Uygulaması")
        self.geometry("1280x800")
        self.minsize(1080, 700)
        self.configure(bg=BG)
        self._logo_cache = {}
        self._apply_windows_dark_titlebar()
        self._set_window_icon()

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
        self._modal = None
        self._toast = None
        self._toast_job = None
        self._viewer_cache = OrderedDict()
        self._build_setup()
        self.bind("<Escape>", lambda e: self.go_setup())

    def _load_logo(self, size):
        try:
            if size not in self._logo_cache:
                logo_path = self._resource("assets", "logo.png")
                if not logo_path.exists():
                    return None
                with Image.open(str(logo_path)) as im:
                    im = im.convert("RGBA")
                    im.thumbnail((size, size), Image.Resampling.LANCZOS)
                    canv = Image.new("RGBA", (size, size), (0, 0, 0, 0))
                    canv.paste(im, ((size - im.width) // 2, (size - im.height) // 2), im)
                    self._logo_cache[size] = ImageTk.PhotoImage(canv)
            return self._logo_cache[size]
        except Exception:
            return None

    def _set_window_icon(self):
        try:
            logo = self._load_logo(64)
            if logo is not None:
                self._win_icon = logo
                self.iconphoto(True, logo)
        except Exception:
            pass

    def _apply_windows_dark_titlebar(self):
        if sys.platform != "win32":
            return
        try:
            import ctypes
            self.update_idletasks()
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
            if not hwnd:
                return

            def _dwm_attr(attr, val):
                try:
                    v = ctypes.c_int(val)
                    ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, attr, ctypes.byref(v), ctypes.sizeof(v))
                except Exception:
                    pass

            _dwm_attr(20, 1)          # DWMWA_USE_IMMERSIVE_DARK_MODE (Win10 2004+ / Win11)
            _dwm_attr(19, 1)          # eski Win10 icin geri donus
            _dwm_attr(35, 0x0014100b) # DWMWA_CAPTION_COLOR ~ BG (#0b1014)
            _dwm_attr(34, 0x00453a2d) # DWMWA_BORDER_COLOR ~ LINE (#2d3a45)
            _dwm_attr(36, 0x00f3f1ee) # DWMWA_TEXT_COLOR ~ TEXT (#eef1f3)
        except Exception:
            pass

    def clear(self):
        for w in self.winfo_children(): w.destroy()
        self._modal = None
        self._toast = None

    def toast(self, msg, kind="info"):
        try:
            acc = {"info": GOLD, "warn": "#e0a34e", "error": "#e06c5e", "success": "#3fae6a"}.get(kind, GOLD)
            if getattr(self, "_toast", None) is not None:
                try:
                    if self._toast.winfo_exists():
                        self._toast.destroy()
                except Exception:
                    pass
                self._toast = None
            if getattr(self, "_toast_job", None) is not None:
                try:
                    self.after_cancel(self._toast_job)
                except Exception:
                    pass
                self._toast_job = None
            t = tk.Frame(self, bg="#0d141b", highlightbackground=acc, highlightthickness=1)
            tk.Label(t, text=msg, bg="#0d141b", fg=TEXT, font=("Segoe UI", 10, "bold"), wraplength=520, justify="center").pack(padx=20, pady=11)
            t.place(relx=0.5, rely=0.9, anchor="center")
            t.lift()
            self._toast = t
            self._toast_job = self.after(2600, self._toast_hide)
        except Exception:
            pass

    def _toast_hide(self):
        self._toast_job = None
        try:
            if getattr(self, "_toast", None) is not None and self._toast.winfo_exists():
                self._toast.destroy()
        except Exception:
            pass
        self._toast = None

    def _modal_card(self, title, msg, kind):
        try:
            self._modal_close(silent=True)
        except Exception:
            pass
        ov = tk.Frame(self, bg="#04070a")
        ov.place(relx=0, rely=0, relwidth=1, relheight=1)
        ov.lift()
        self._modal = ov
        card = tk.Frame(ov, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        card.place(relx=0.5, rely=0.42, anchor="center")
        icons = {"info": ("\u2139", GOLD), "warn": ("\u26a0", "#e0a34e"), "error": ("\u2715", "#e06c5e"), "success": ("\u2713", "#3fae6a")}
        glyph, col = icons.get(kind, icons["info"])
        h = tk.Frame(card, bg=PANEL)
        h.pack(fill="x", padx=20, pady=(18, 6))
        tk.Label(h, text=glyph, bg=PANEL, fg=col, font=("Segoe UI", 16, "bold")).pack(side="left", padx=(0, 10))
        tk.Label(h, text=title, bg=PANEL, fg=TEXT, font=("Segoe UI", 12, "bold"), wraplength=360, justify="left").pack(side="left")
        tk.Label(card, text=msg, bg=PANEL, fg=MUTED, font=("Segoe UI", 10), wraplength=400, justify="left").pack(fill="x", padx=20, pady=(0, 14))
        btns = tk.Frame(card, bg=PANEL)
        btns.pack(fill="x", padx=20, pady=(0, 18))
        return ov, card, btns

    def alert_modal(self, title, msg, kind="info", ok_text="Tamam", on_ok=None):
        try:
            ov, card, btns = self._modal_card(title, msg, kind)
            def _ok(e=None):
                cb = on_ok
                self._modal_close()
                if callable(cb):
                    cb()
            b = tk.Button(btns, text=ok_text, command=_ok, bg=GOLD, fg="#141a20", activebackground=GOLD_HOVER, relief="flat", bd=0, cursor="hand2", font=("Segoe UI", 10, "bold"), padx=24, pady=9)
            b.pack(side="right")
            b.focus_set()
            self.bind("<Escape>", lambda e: self._modal_close())
            self.bind("<Return>", lambda e: _ok())
        except Exception:
            pass

    def confirm_modal(self, title, msg, yes_text="Evet", no_text="Vazge\u00e7", on_yes=None):
        try:
            ov, card, btns = self._modal_card(title, msg, "warn")
            def _yes(e=None):
                cb = on_yes
                self._modal_close()
                if callable(cb):
                    cb()
            def _no(e=None):
                self._modal_close()
            tk.Button(btns, text=yes_text, command=_yes, bg=GOLD, fg="#141a20", activebackground=GOLD_HOVER, relief="flat", bd=0, cursor="hand2", font=("Segoe UI", 10, "bold"), padx=24, pady=9).pack(side="right")
            tk.Button(btns, text=no_text, command=_no, bg=PANEL2, fg=TEXT, activebackground="#26343d", relief="flat", bd=0, cursor="hand2", font=("Segoe UI", 10, "bold"), padx=18, pady=9).pack(side="right", padx=(0, 8))
            self.bind("<Escape>", lambda e: _no())
        except Exception:
            pass

    def _modal_close(self, silent=False):
        try:
            if getattr(self, "_modal", None) is not None:
                try:
                    if self._modal.winfo_exists():
                        self._modal.destroy()
                except Exception:
                    pass
            self._modal = None
            if not silent:
                try:
                    for seq in ("<Return>",):
                        try:
                            self.unbind(seq)
                        except Exception:
                            pass
                except Exception:
                    pass
                self._restore_escape()
        except Exception:
            pass

    def _restore_escape(self):
        try:
            lb = getattr(self, "_lb_overlay", None)
            if lb is not None and lb.winfo_exists():
                self.bind("<Escape>", lambda e: self._lightbox_close())
                return
        except Exception:
            pass
        try:
            cmp = getattr(self, "_cmp_overlay", None)
            if cmp is not None and cmp.winfo_exists():
                self.bind("<Escape>", lambda e: self._compare_close())
                return
        except Exception:
            pass
        try:
            self.bind("<Escape>", lambda e: self.go_setup())
        except Exception:
            pass

    def gold_button(self, p, text, cmd, big=False):
        return tk.Button(p, text=text, command=cmd, bg=GOLD, fg="#11161a", activebackground=GOLD_HOVER, activeforeground="#11161a", relief="flat", bd=0, cursor="hand2", font=("Segoe UI", 12 if big else 10, "bold"), padx=18, pady=12 if big else 9)

    def dark_button(self, p, text, cmd):
        return tk.Button(p, text=text, command=cmd, bg=PANEL2, fg=TEXT, activebackground="#26343d", activeforeground="#fff", relief="flat", bd=0, cursor="hand2", font=("Segoe UI", 10, "bold"), padx=12, pady=9)

    def _topbar(self, parent):
        bar = tk.Frame(parent, bg="#0b1014", height=48)
        bar.pack(fill="x"); bar.pack_propagate(False)
        logo = self._load_logo(32)
        if logo is not None:
            tk.Label(bar, image=logo, bg="#0b1014").pack(side="left", padx=(22, 10))
            title = "FotoSecim"
            title_padx = 0
        else:
            title = "📷  FotoSecim"
            title_padx = 22
        tk.Label(bar, text=title, bg="#0b1014", fg="#f0e0c4", font=("Segoe UI", 14, "bold")).pack(side="left", padx=(title_padx, 0))
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

            hero_logo = self._load_logo(64)
            if hero_logo is not None:
                cv.create_image(cx, iy + 2, image=hero_logo, tags="hero")
            else:
                # Kamera ikonu - gold kontur (logo yoksa geri donus)
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
            cv.create_text(16, h - 17, text="ⓘ   FotoSecim v2.0    |    Düğün Fotoğraf Seçim Uygulaması", anchor="w", fill="#707a82", font=("Segoe UI", 8), tags="foot")
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
        if not self.folder: self.alert_modal("Klasör gerekli", "Önce fotoğrafların bulunduğu klasörü seçin.", kind="warn"); return
        try: count = int(self.count_var.get())
        except: self.alert_modal("Geçersiz sayı", "Normal fotoğraf sayısını doğru girin.", kind="warn"); return
        album_name = self.output_name_var.get().strip()
        if getattr(self, "_album_placeholder", None) and album_name == self._album_placeholder: album_name = ""
        if count < 1 or not album_name: self.alert_modal("Eksik bilgi", "Fotoğraf sayısı ve albüm adı boş olamaz.", kind="warn"); return
        photos = sorted([p for p in self.folder.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS], key=lambda p: p.name.lower())
        
        try:
            cover_count = int(self.cover_count_var.get()) if self.cover_var.get() else 0
            table_count = int(self.table_count_var.get()) if self.table_var.get() else 0
        except Exception:
            self.alert_modal("Geçersiz sayı", "Kapak ve tablo adetlerini doğru girin.", kind="warn"); return

        needed = count + cover_count + table_count
        if not photos: self.alert_modal("Fotoğraf bulunamadı", "Klasörde desteklenen fotoğraf bulunamadı.", kind="error"); return
        if len(photos) < needed: self.alert_modal("Fotoğraf sayısı yetersiz", f"Klasörde {len(photos)} fotoğraf var; en az {needed} fotoğraf gerekiyor.", kind="warn"); return
        
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
        self.tb_compare = tk.Button(bar, text="\u25a6 2\u2019li", command=lambda: self.gallery_compare(2), bg=PANEL2, fg=TEXT, activebackground="#26343d", relief="flat", bd=0, cursor="hand2", font=("Segoe UI", 10, "bold"), padx=14, pady=8)
        self.tb_compare.pack(side="left", padx=5)
        self.tb_compare3 = tk.Button(bar, text="\u25a6 3\u2019l\u00fc", command=lambda: self.gallery_compare(3), bg=PANEL2, fg=TEXT, activebackground="#26343d", relief="flat", bd=0, cursor="hand2", font=("Segoe UI", 10, "bold"), padx=14, pady=8)
        self.tb_compare3.pack(side="left", padx=5)
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

    # ---- Hizli resim motoru: bellek LRU + disk onbellek + tembel yukleme ----
    _SRC_MAX = 560
    _SRC_MEM = 32
    _VIEW_MEM = 10

    def _thumb_dir(self):
        try:
            d = Path(tempfile.gettempdir()) / "fotosecim_thumbs"
            d.mkdir(parents=True, exist_ok=True)
            return d
        except Exception:
            return None

    def _src_image(self, path):
        try:
            mem = self._src_mem
        except AttributeError:
            mem = self._src_mem = OrderedDict()
        key = str(path)
        hit = mem.get(key)
        if hit is not None:
            try:
                mem.move_to_end(key)
                return hit.copy()
            except Exception:
                pass
        img = None
        try:
            d = self._thumb_dir()
            cf = None
            if d is not None:
                try:
                    st = Path(path).stat()
                    ck = hashlib.md5(f"{path}|{st.st_size}|{int(st.st_mtime)}".encode("utf-8", "ignore")).hexdigest()
                except Exception:
                    ck = hashlib.md5(str(path).encode("utf-8", "ignore")).hexdigest()
                cf = d / (ck + ".jpg")
                if cf.exists():
                    try:
                        tmp = Image.open(cf)
                        tmp.load()
                        img = tmp.convert("RGB")
                        tmp.close()
                    except Exception:
                        try:
                            cf.unlink()
                        except Exception:
                            pass
                        img = None
            if img is None:
                with Image.open(path) as im:
                    im.load()
                    img = im.convert("RGB")
                    img.thumbnail((self._SRC_MAX, self._SRC_MAX), Image.Resampling.BILINEAR)
                    if cf is not None:
                        try:
                            img.save(cf, "JPEG", quality=80)
                        except Exception:
                            pass
        except Exception:
            img = None
        if img is None:
            return None
        try:
            mem[key] = img.copy()
            while len(mem) > self._SRC_MEM:
                mem.popitem(last=False)
        except Exception:
            pass
        return img

    def _decode_fit(self, path, box):
        try:
            with Image.open(path) as im:
                try:
                    im.draft("RGB", (max(1, box[0]), max(1, box[1])))
                except Exception:
                    pass
                im.load()
                pic = im.convert("RGB")
                pic.thumbnail((max(1, box[0]), max(1, box[1])), Image.Resampling.BILINEAR)
                return pic
        except Exception:
            return None

    def _photo_ref(self, path, box):
        try:
            mem = self._view_mem
        except AttributeError:
            mem = self._view_mem = OrderedDict()
        key = (str(path), max(1, box[0] // 16), max(1, box[1] // 16))
        hit = mem.get(key)
        if hit is not None:
            try:
                mem.move_to_end(key)
                return hit
            except Exception:
                pass
        pic = None
        if max(box) <= self._SRC_MAX + 64:
            pic = self._src_image(path)
            if pic is not None:
                pic.thumbnail((max(1, box[0]), max(1, box[1])), Image.Resampling.BILINEAR)
        if pic is None:
            pic = self._decode_fit(path, box)
        if pic is None:
            return None
        try:
            ref = ImageTk.PhotoImage(pic)
        except Exception:
            return None
        try:
            mem[key] = ref
            while len(mem) > self._VIEW_MEM:
                mem.popitem(last=False)
        except Exception:
            pass
        return ref

    def _preload_neighbors(self):
        try:
            total = len(getattr(self, "photos", []))
            cur = getattr(self, "view_index", 0)
            for step in (1, -1, 2, -2):
                j = cur + step
                if 0 <= j < total:
                    self._src_image(self.photos[j])
        except Exception:
            pass

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
            ref = self._photo_ref(path, (max(100, w - 20), max(100, h - 10)))
            if ref is None:
                raise RuntimeError("decode")
            self._viewer_ref = ref
            self.viewer_label.configure(image=self._viewer_ref, text="")
            self.after_idle(self._preload_neighbors)
        except Exception:
            try:
                self.viewer_label.configure(text="Önizleme açılamadı", image="")
            except Exception:
                pass

    def _build_strip(self):
        try:
            if getattr(self, "_strip_job", None) is not None:
                try:
                    self.after_cancel(self._strip_job)
                except Exception:
                    pass
                self._strip_job = None
        except Exception:
            pass
        try:
            self._strip_gen = getattr(self, "_strip_gen", 0) + 1
        except Exception:
            self._strip_gen = 1
        for w in self.strip_inner.winfo_children():
            w.destroy()
        self._thumb_refs = {}
        self._thumb_labels = {}
        total = len(getattr(self, "photos", []))
        cur = max(0, min(getattr(self, "view_index", 0), max(0, total - 1)))
        order = []
        if total:
            order.append(cur)
            k = 1
            while len(order) < total:
                a, b = cur - k, cur + k
                if a >= 0:
                    order.append(a)
                if b < total:
                    order.append(b)
                k += 1
        self._strip_queue = order
        for i, path in enumerate(self.photos):
            cell = tk.Frame(self.strip_inner, bg="#0c1116", highlightbackground=LINE, highlightthickness=1, cursor="hand2")
            cell.pack(side="left", padx=4)
            lab = tk.Label(cell, text="...", bg="#0c1116", fg=MUTED, font=("Segoe UI", 7), width=14, height=5, cursor="hand2")
            lab.pack(padx=3, pady=3)
            lab.bind("<Button-1>", lambda e, idx=i: self.gallery_show(idx))
            cell.bind("<Button-1>", lambda e, idx=i: self.gallery_show(idx))
            self._thumb_labels[path] = (cell, lab)
        self.after(50, self._strip_refresh)
        self._strip_job = self.after(30, lambda g=self._strip_gen: self._strip_pump(g))

    def _strip_pump(self, gen):
        self._strip_job = None
        try:
            if gen != getattr(self, "_strip_gen", -1):
                return
            if not hasattr(self, "strip_inner") or not self.strip_inner.winfo_exists():
                return
            q = getattr(self, "_strip_queue", [])
            for _ in range(6):
                if not q:
                    break
                i = q.pop(0)
                try:
                    path = self.photos[i]
                except Exception:
                    continue
                pair = self._thumb_labels.get(path)
                if not pair:
                    continue
                cell, lab = pair
                try:
                    if not lab.winfo_exists():
                        continue
                except Exception:
                    continue
                try:
                    base = self._src_image(path)
                    if base is None:
                        continue
                    base.thumbnail((104, 62), Image.Resampling.BILINEAR)
                    bg = Image.new("RGB", (104, 62), "#0c1116")
                    bg.paste(base, ((104 - base.width) // 2, (62 - base.height) // 2))
                    ref = ImageTk.PhotoImage(bg)
                    self._thumb_refs[path] = ref
                    lab.configure(image=ref, text="", width=104, height=62)
                except Exception:
                    pass
            try:
                self._strip_refresh()
            except Exception:
                pass
            if q:
                self._strip_job = self.after(15, lambda: self._strip_pump(gen))
        except Exception:
            pass

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

    def gallery_compare(self, n=2):
        try:
            if len(getattr(self, "photos", [])) < 2:
                self.toast("Karşılaştırma için en az 2 fotoğraf gerek", kind="warn")
                return
        except Exception:
            pass
        self._compare_open(n)

    def _compare_open(self, n=2):
        if not getattr(self, "photos", None):
            return
        try:
            if hasattr(self, "_cmp_overlay") and self._cmp_overlay is not None and self._cmp_overlay.winfo_exists():
                self._compare_close()
        except Exception:
            pass
        try:
            if hasattr(self, "_lb_overlay") and self._lb_overlay is not None and self._lb_overlay.winfo_exists():
                self._lightbox_close()
        except Exception:
            pass
        n = 3 if int(n) == 3 else 2
        total = len(self.photos)
        base = getattr(self, "view_index", 0)
        idxs = []
        for k in range(n):
            idxs.append(max(0, min(base + k, total - 1)))
        if n == 2 and total > 1 and idxs[0] == idxs[1]:
            idxs[1] = min(total - 1, idxs[0] + 1) if idxs[0] == 0 else idxs[0] - 1
        if n == 3:
            seen = set()
            fixed = []
            for i in idxs:
                while i in seen and len(seen) < total:
                    i = (i + 1) % total
                seen.add(i)
                fixed.append(i)
            idxs = fixed
        self._cmp_n = n
        self._cmp_idxs = idxs
        self._cmp_refs = {}
        self._cmp_job = None

        ov = tk.Frame(self, bg="#05080b", highlightbackground=GOLD, highlightthickness=1)
        ov.place(relx=0, rely=0, relwidth=1, relheight=1)
        ov.lift()
        self._cmp_overlay = ov

        top = tk.Frame(ov, bg="#0b1014")
        top.pack(fill="x", padx=14, pady=(12, 6))
        tk.Label(top, text="Kar\u015f\u0131la\u015ft\u0131r", bg="#0b1014", fg=GOLD, font=("Segoe UI", 14, "bold")).pack(side="left")
        tk.Label(top, text="yan yana incele, be\u011fendiklerini se\u00e7", bg="#0b1014", fg=MUTED, font=("Segoe UI", 9)).pack(side="left", padx=(10, 0))
        tk.Button(top, text="\u2715 Kapat  (Esc)", command=self._compare_close, bg=PANEL2, fg=TEXT, activebackground="#26343d", relief="flat", bd=0, cursor="hand2", font=("Segoe UI", 10, "bold"), padx=14, pady=7).pack(side="right")
        self._cmp_btn3 = tk.Button(top, text="3\u2019l\u00fc", command=lambda: self._compare_set_n(3), relief="flat", bd=0, cursor="hand2", font=("Segoe UI", 10, "bold"), padx=16, pady=7)
        self._cmp_btn3.pack(side="right", padx=6)
        self._cmp_btn2 = tk.Button(top, text="2\u2019li", command=lambda: self._compare_set_n(2), relief="flat", bd=0, cursor="hand2", font=("Segoe UI", 10, "bold"), padx=16, pady=7)
        self._cmp_btn2.pack(side="right", padx=6)

        body = tk.Frame(ov, bg="#05080b")
        body.pack(fill="both", expand=True, padx=14, pady=6)
        self._cmp_body = body
        self._cmp_cols = []
        for c in range(3):
            col = tk.Frame(body, bg=PANEL, highlightbackground=LINE, highlightthickness=1)
            img = tk.Label(col, bg="#0c1116", fg=MUTED, font=("Segoe UI", 10))
            img.pack(fill="both", expand=True, padx=8, pady=(8, 4))
            img.bind("<Configure>", lambda e: self._compare_schedule())
            img.bind("<Double-Button-1>", lambda e, cc=c: self._lightbox_open(self.photos[self._cmp_idxs[cc]]))
            nav = tk.Frame(col, bg=PANEL)
            nav.pack(fill="x", padx=8, pady=2)
            bp = tk.Button(nav, text="\u2039", font=("Segoe UI", 16, "bold"), bg=PANEL2, fg=GOLD, activebackground="#26343d", relief="flat", bd=0, cursor="hand2", width=3, command=lambda cc=c: self._compare_nav(cc, -1))
            bp.pack(side="left")
            bn = tk.Button(nav, text="\u203a", font=("Segoe UI", 16, "bold"), bg=PANEL2, fg=GOLD, activebackground="#26343d", relief="flat", bd=0, cursor="hand2", width=3, command=lambda cc=c: self._compare_nav(cc, 1))
            bn.pack(side="right")
            cap = tk.Label(nav, text="", bg=PANEL, fg="#c9d1d7", font=("Segoe UI", 8))
            cap.pack(side="left", expand=True)
            sel = tk.Button(col, text="", font=("Segoe UI", 10, "bold"), relief="flat", bd=0, cursor="hand2", padx=10, pady=7, command=lambda cc=c: self._compare_toggle(cc))
            sel.pack(fill="x", padx=8, pady=(2, 8))
            self._cmp_cols.append({"frame": col, "img": img, "cap": cap, "sel": sel})
        for c in range(3):
            body.grid_columnconfigure(c, weight=1, uniform="cmp")
        body.rowconfigure(0, weight=1)

        hint = tk.Label(ov, text="Her kare ba\u011f\u0131ms\u0131z gezilir  \u2022  \u2039 \u203a ile de\u011fi\u015ftir  \u2022  1 / 2 / 3 ile se\u00e7  \u2022  \u00c7ift t\u0131k b\u00fcy\u00fct\u00fcr", bg="#05080b", fg=MUTED, font=("Segoe UI", 8))
        hint.pack(pady=(0, 12))

        ov.bind("<Configure>", lambda e: self._compare_schedule())
        ov.focus_set()
        self.bind("<Escape>", lambda e: self._compare_close())
        for key, col in (("1", 0), ("2", 1), ("3", 2)):
            self.bind(key, lambda e, cc=col: self._compare_toggle(cc))
        self._compare_layout()
        self._compare_schedule()

    def _compare_set_n(self, n):
        n = 3 if int(n) == 3 else 2
        if n == getattr(self, "_cmp_n", 2):
            return
        try:
            self._cmp_refs = {}
            mem = getattr(self, "_view_mem", None)
            if mem is not None:
                mem.clear()
        except Exception:
            pass
        total = len(self.photos)
        n = max(2, min(n, total))
        base = self._cmp_idxs[0] if getattr(self, "_cmp_idxs", None) else getattr(self, "view_index", 0)
        idxs = []
        k = 0
        while len(idxs) < n and k < total * 2:
            cand = (base + k) % total
            if cand not in idxs:
                idxs.append(cand)
            k += 1
        while len(idxs) < n:
            idxs.append(base)
        self._cmp_n = n
        self._cmp_idxs = idxs
        self._compare_layout()
        try:
            self._cmp_overlay.update_idletasks()
        except Exception:
            pass
        self._compare_draw()
        self._compare_schedule()
        self.after(250, self._compare_schedule)

    def _compare_layout(self):
        try:
            n = getattr(self, "_cmp_n", 2)
            for c, col in enumerate(self._cmp_cols):
                if c < n:
                    col["frame"].grid(row=0, column=c, sticky="nsew", padx=6)
                else:
                    col["frame"].grid_forget()
            for b, val in ((self._cmp_btn2, 2), (self._cmp_btn3, 3)):
                on = (val == n)
                b.configure(bg=(GOLD if on else PANEL2), fg=("#141a20" if on else TEXT), activebackground=(GOLD_HOVER if on else "#26343d"))
        except Exception:
            pass

    def _compare_schedule(self):
        try:
            if getattr(self, "_cmp_job", None) is not None:
                try:
                    self.after_cancel(self._cmp_job)
                except Exception:
                    pass
            self._cmp_job = self.after(100, self._compare_draw)
        except Exception:
            pass

    def _compare_draw(self):
        self._cmp_job = None
        try:
            if not hasattr(self, "_cmp_overlay") or not self._cmp_overlay.winfo_exists():
                return
            n = getattr(self, "_cmp_n", 2)
            for c in range(n):
                col = self._cmp_cols[c]
                idx = max(0, min(self._cmp_idxs[c], len(self.photos) - 1))
                self._cmp_idxs[c] = idx
                path = self.photos[idx]
                w = col["img"].winfo_width()
                h = col["img"].winfo_height()
                if w < 60 or h < 60:
                    self._compare_schedule()
                    continue
                try:
                    ref = self._photo_ref(path, (max(10, w - 10), max(10, h - 10)))
                    if ref is None:
                        raise RuntimeError("decode")
                    self._cmp_refs[c] = ref
                    col["img"].configure(image=ref, text="")
                except Exception:
                    col["img"].configure(text="Açılamadı", image="")
                try:
                    col["cap"].configure(text=f"{idx + 1} / {len(self.photos)}  •  {path.name}")
                    if path in self.selected:
                        col["sel"].configure(text="✓  Seçildi", bg="#3fae6a", fg="#0c1116", activebackground="#4cc47e")
                        col["frame"].configure(highlightbackground="#3fae6a", highlightthickness=2)
                    else:
                        col["sel"].configure(text="♥  Seç", bg=GOLD, fg="#141a20", activebackground=GOLD_HOVER)
                        if idx == getattr(self, "view_index", -1):
                            col["frame"].configure(highlightbackground=GOLD, highlightthickness=2)
                        else:
                            col["frame"].configure(highlightbackground=LINE, highlightthickness=1)
                except Exception:
                    pass
        except Exception:
            pass

    def _compare_nav(self, col, step):
        try:
            total = len(self.photos)
            self._cmp_idxs[col] = max(0, min(self._cmp_idxs[col] + step, total - 1))
            self._compare_draw()
        except Exception:
            pass

    def _compare_toggle(self, col):
        try:
            if col >= getattr(self, "_cmp_n", 2):
                return
            path = self.photos[self._cmp_idxs[col]]
            self.toggle(path)
            self._compare_draw()
        except Exception:
            pass

    def _compare_close(self):
        try:
            if getattr(self, "_cmp_job", None) is not None:
                try:
                    self.after_cancel(self._cmp_job)
                except Exception:
                    pass
                self._cmp_job = None
        except Exception:
            pass
        try:
            if hasattr(self, "_cmp_overlay") and self._cmp_overlay is not None and self._cmp_overlay.winfo_exists():
                self._cmp_overlay.destroy()
        except Exception:
            pass
        self._cmp_overlay = None
        try:
            for key in ("1", "2", "3"):
                try:
                    self.unbind(key)
                except Exception:
                    pass
            self.bind("<Escape>", lambda e: self.go_setup())
        except Exception:
            pass

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
                self.toast(f"En fazla {self.normal_count} fotoğraf seçebilirsin", kind="warn")
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
            if len(self.selected) != self.normal_count: self.toast(f"Tam olarak {self.normal_count} fotoğraf seçmelisin", kind="warn"); return
            self.normal_selection = set(self.selected)
            if self.cover_required: self.mode = "cover"; self.selected.clear(); self.view_index = 0; self.show_cover_mode()
            elif self.table_required: self.mode = "table"; self.selected.clear(); self.view_index = 0; self._selection_refresh()
            else: self.finish()
        elif self.mode == "cover":
            if len(self.selected) != 1: self.toast("Kapak için 1 fotoğraf seç", kind="warn"); return
            self.cover = next(iter(self.selected))
            if self.table_required: self.mode = "table"; self.selected.clear(); self.view_index = 0; self._selection_refresh()
            else: self.finish()
        elif self.mode == "table":
            if len(self.selected) != 1: self.toast("Tablo için 1 fotoğraf seç", kind="warn"); return
            self.table = next(iter(self.selected)); self.finish()

    def _selection_refresh(self):
        self.view_index = 0
        self._selection_page()
    def show_cover_mode(self):
        self.view_index = 0
        self._selection_page()

    def open_photo(self, path):
        self._lightbox_open(path)

    def _lightbox_open(self, path):
        if not getattr(self, "photos", None):
            return
        try:
            if path in self.photos:
                self.view_index = self.photos.index(path)
        except Exception:
            pass
        try:
            if hasattr(self, "_lb_overlay") and self._lb_overlay is not None and self._lb_overlay.winfo_exists():
                self._lightbox_close()
        except Exception:
            pass
        try:
            if hasattr(self, "_cmp_overlay") and self._cmp_overlay is not None and self._cmp_overlay.winfo_exists():
                pass
        except Exception:
            pass
        self._lb_zoom = 1.0
        self._lb_job = None
        self._lb_img_ref = None
        self._lb_ox = 0.0
        self._lb_oy = 0.0
        self._lb_drag = None
        self._lb_item = None

        ov = tk.Frame(self, bg="#04070a")
        ov.place(relx=0, rely=0, relwidth=1, relheight=1)
        ov.lift()
        self._lb_overlay = ov

        top = tk.Frame(ov, bg="#0b1014")
        top.pack(fill="x", padx=14, pady=(12, 6))
        self._lb_title = tk.Label(top, text="", bg="#0b1014", fg=TEXT, font=("Segoe UI", 11, "bold"))
        self._lb_title.pack(side="left")
        tk.Button(top, text="\u2715 Kapat  (Esc)", command=self._lightbox_close, bg=PANEL2, fg=TEXT, activebackground="#26343d", relief="flat", bd=0, cursor="hand2", takefocus=0, font=("Segoe UI", 10, "bold"), padx=14, pady=7).pack(side="right")
        self._lb_sel = tk.Button(top, text="", command=self._lightbox_toggle, relief="flat", bd=0, cursor="hand2", takefocus=0, font=("Segoe UI", 10, "bold"), padx=16, pady=7)
        self._lb_sel.pack(side="right", padx=6)
        tk.Button(top, text="S\u0131\u011fd\u0131r", command=self._lightbox_fit, bg=PANEL2, fg=TEXT, activebackground="#26343d", relief="flat", bd=0, cursor="hand2", takefocus=0, font=("Segoe UI", 10, "bold"), padx=14, pady=7).pack(side="right", padx=6)
        tk.Button(top, text="\u2212", command=lambda: self._lightbox_zoom(0.8, True), bg=PANEL2, fg=TEXT, activebackground="#26343d", relief="flat", bd=0, cursor="hand2", takefocus=0, font=("Segoe UI", 12, "bold"), width=3).pack(side="right", padx=2)
        tk.Button(top, text="+", command=lambda: self._lightbox_zoom(1.25, True), bg=PANEL2, fg=TEXT, activebackground="#26343d", relief="flat", bd=0, cursor="hand2", takefocus=0, font=("Segoe UI", 12, "bold"), width=3).pack(side="right", padx=2)

        mid = tk.Frame(ov, bg="#04070a")
        mid.pack(fill="both", expand=True, padx=14)
        mid.columnconfigure(1, weight=1)
        mid.rowconfigure(0, weight=1)
        tk.Button(mid, text="\u2039", command=lambda: self._lightbox_nav(-1), bg="#0d141b", fg=GOLD, activebackground="#1a2530", relief="flat", bd=0, cursor="hand2", takefocus=0, font=("Segoe UI", 30, "bold"), width=2).grid(row=0, column=0, sticky="ns", padx=(0, 8))
        tk.Button(mid, text="\u203a", command=lambda: self._lightbox_nav(1), bg="#0d141b", fg=GOLD, activebackground="#1a2530", relief="flat", bd=0, cursor="hand2", takefocus=0, font=("Segoe UI", 30, "bold"), width=2).grid(row=0, column=2, sticky="ns", padx=(8, 0))

        cvwrap = tk.Frame(mid, bg="#04070a")
        cvwrap.grid(row=0, column=1, sticky="nsew")
        cvwrap.rowconfigure(0, weight=1)
        cvwrap.columnconfigure(0, weight=1)
        cv = tk.Canvas(cvwrap, bg="#04070a", highlightthickness=0)
        cv.grid(row=0, column=0, sticky="nsew")
        self._lb_canvas = cv
        cv.bind("<Configure>", lambda e: self._lightbox_schedule())
        cv.bind("<Button-1>", self._lightbox_drag_start)
        cv.bind("<B1-Motion>", self._lightbox_drag_move)
        cv.bind("<ButtonRelease-1>", self._lightbox_drag_end)
        cv.bind("<MouseWheel>", self._lightbox_wheel)
        cv.bind("<Button-4>", lambda e: self._lightbox_zoom(1.15))
        cv.bind("<Button-5>", lambda e: self._lightbox_zoom(0.87))

        hint = tk.Label(ov, text="S\u00fcr\u00fckle: kayd\u0131r  \u2022  Tekerlek / + / \u2212: zum  \u2022  \u2190 \u2192: gez  \u2022  Space: se\u00e7  \u2022  \u00c7ift t\u0131k: kapat", bg="#04070a", fg=MUTED, font=("Segoe UI", 8))
        hint.pack(pady=(6, 12))
        cv.bind("<Double-Button-1>", lambda e: self._lightbox_close())

        ov.focus_set()
        self.bind("<Escape>", lambda e: self._lightbox_close())
        self.bind("<Left>", lambda e: self._lightbox_nav(-1))
        self.bind("<Right>", lambda e: self._lightbox_nav(1))
        self.bind("<space>", lambda e: self._lightbox_toggle())
        self.bind("<plus>", lambda e: self._lightbox_zoom(1.25))
        self.bind("<minus>", lambda e: self._lightbox_zoom(0.8))
        self.bind("<f>", lambda e: self._lightbox_close())
        self.bind("<F>", lambda e: self._lightbox_close())
        self._lightbox_schedule()

    def _lightbox_path(self):
        try:
            return self.photos[getattr(self, "view_index", 0)]
        except Exception:
            return None

    def _lightbox_schedule(self):
        try:
            if getattr(self, "_lb_job", None) is not None:
                try:
                    self.after_cancel(self._lb_job)
                except Exception:
                    pass
            self._lb_job = self.after(40, self._lightbox_draw)
        except Exception:
            pass

    def _lightbox_draw(self):
        self._lb_job = None
        try:
            if not hasattr(self, "_lb_canvas") or not self._lb_canvas.winfo_exists():
                return
            path = self._lightbox_path()
            if path is None:
                return
            cv = self._lb_canvas
            w = max(100, cv.winfo_width())
            h = max(100, cv.winfo_height())
            zoom = max(self._LB_MIN, min(self._LB_MAX, getattr(self, "_lb_zoom", 1.0)))
            self._lb_zoom = zoom
            try:
                try:
                    lbmem = self._lb_mem
                except AttributeError:
                    lbmem = self._lb_mem = OrderedDict()
                bkey = str(path)
                entry = lbmem.get(bkey)
                small = big = None
                if entry is not None:
                    try:
                        lbmem.move_to_end(bkey)
                        small, big = entry
                        small = small.copy()
                        big = big.copy()
                    except Exception:
                        small = big = None
                if small is None or big is None:
                    with Image.open(path) as im:
                        try:
                            im.draft("RGB", (3600, 3600))
                        except Exception:
                            pass
                        im.load()
                        full = im.convert("RGB")
                        big = full.copy()
                        big.thumbnail((3600, 3600), Image.Resampling.BILINEAR)
                        small = big.copy()
                        small.thumbnail((1600, 1600), Image.Resampling.BILINEAR)
                    try:
                        lbmem[bkey] = (small.copy(), big.copy())
                        while len(lbmem) > 3:
                            lbmem.popitem(last=False)
                    except Exception:
                        pass
                base = big if zoom > 1.25 else small
                bw, bh = base.size
                s = min(w / bw, h / bh) * zoom
                nw, nh = max(1, int(bw * s)), max(1, int(bh * s))
                if max(nw, nh) > 4096:
                    k = 4096 / max(nw, nh)
                    nw, nh = max(1, int(nw * k)), max(1, int(nh * k))
                fit = base.resize((nw, nh), Image.Resampling.BILINEAR)
                ref = ImageTk.PhotoImage(fit)
                self._lb_img_ref = ref
                self._lb_iw, self._lb_ih = fit.width, fit.height
                self._lightbox_clamp_offset()
                cv.delete("lb")
                self._lb_item = cv.create_image(w / 2 + self._lb_ox, h / 2 + self._lb_oy,
                                                image=ref, anchor="center", tags="lb")
            except Exception:
                cv.delete("lb")
                self._lb_item = None
                cv.create_text(max(100, cv.winfo_width()) / 2, max(100, cv.winfo_height()) / 2,
                               text="Açılamadı", fill="#889198", tags="lb")
            try:
                total = len(self.photos)
                idx = getattr(self, "view_index", 0)
                self._lb_title.configure(text=f"{idx + 1} / {total}  •  {path.name}  •  %{int(zoom * 100)}")
                if path in self.selected:
                    self._lb_sel.configure(text="✓  Seçildi", bg="#3fae6a", fg="#0c1116", activebackground="#4cc47e")
                else:
                    self._lb_sel.configure(text="♥  Seç", bg=GOLD, fg="#141a20", activebackground=GOLD_HOVER)
            except Exception:
                pass
        except Exception:
            pass

    def _lightbox_nav(self, step):
        try:
            total = len(self.photos)
            self.view_index = max(0, min(getattr(self, "view_index", 0) + step, total - 1))
            self.viewer_label.configure(text="Yükleniyor...")
            self._viewer_draw()
            self._strip_refresh()
            self._update()
            self._lb_ox = 0.0
            self._lb_oy = 0.0
            self._lightbox_schedule()
        except Exception:
            pass

    def _lightbox_toggle(self):
        try:
            path = self._lightbox_path()
            if path is None:
                return
            self.toggle(path)
            try:
                self._lightbox_schedule()
            except Exception:
                pass
        except Exception:
            pass

    _LB_MIN = 0.5
    _LB_MAX = 8.0

    def _lightbox_zoom(self, factor, now=False):
        try:
            self._lb_zoom = max(self._LB_MIN, min(self._LB_MAX, getattr(self, "_lb_zoom", 1.0) * float(factor)))
            self._lightbox_clamp_offset()
            if now:
                try:
                    if getattr(self, "_lb_job", None) is not None:
                        try:
                            self.after_cancel(self._lb_job)
                        except Exception:
                            pass
                        self._lb_job = None
                except Exception:
                    pass
                self._lightbox_draw()
            else:
                self._lightbox_schedule()
        except Exception:
            pass

    def _lightbox_fit(self):
        try:
            self._lb_zoom = 1.0
            self._lb_ox = 0.0
            self._lb_oy = 0.0
            self._lightbox_schedule()
        except Exception:
            pass

    def _lightbox_center(self):
        try:
            cv = self._lb_canvas
            if not cv.winfo_exists():
                return
            self._lb_ox = 0.0
            self._lb_oy = 0.0
            if getattr(self, "_lb_item", None) is not None:
                cv.coords(self._lb_item, cv.winfo_width() / 2, cv.winfo_height() / 2)
        except Exception:
            pass

    def _lightbox_clamp_offset(self):
        try:
            cv = getattr(self, "_lb_canvas", None)
            if cv is None or not cv.winfo_exists():
                return
            iw = float(getattr(self, "_lb_iw", 0) or 0)
            ih = float(getattr(self, "_lb_ih", 0) or 0)
            w = max(1, cv.winfo_width())
            h = max(1, cv.winfo_height())
            if iw <= w:
                self._lb_ox = 0.0
            else:
                lim = (iw - w) / 2
                self._lb_ox = max(-lim, min(lim, getattr(self, "_lb_ox", 0.0)))
            if ih <= h:
                self._lb_oy = 0.0
            else:
                lim = (ih - h) / 2
                self._lb_oy = max(-lim, min(lim, getattr(self, "_lb_oy", 0.0)))
        except Exception:
            pass

    def _lightbox_drag_start(self, e=None):
        try:
            self._lb_drag = (e.x, e.y, getattr(self, "_lb_ox", 0.0), getattr(self, "_lb_oy", 0.0))
        except Exception:
            self._lb_drag = None

    def _lightbox_drag_move(self, e=None):
        try:
            d = getattr(self, "_lb_drag", None)
            if not d:
                return
            cv = self._lb_canvas
            if not cv.winfo_exists():
                return
            self._lb_ox = d[2] + (e.x - d[0])
            self._lb_oy = d[3] + (e.y - d[1])
            self._lightbox_clamp_offset()
            if getattr(self, "_lb_item", None) is not None:
                cv.coords(self._lb_item, cv.winfo_width() / 2 + self._lb_ox,
                          cv.winfo_height() / 2 + self._lb_oy)
        except Exception:
            pass

    def _lightbox_drag_end(self, e=None):
        try:
            self._lb_drag = None
            self._lightbox_clamp()
        except Exception:
            pass

    def _lightbox_clamp(self):
        try:
            self._lightbox_clamp_offset()
            cv = getattr(self, "_lb_canvas", None)
            if cv is None or not cv.winfo_exists():
                return
            if getattr(self, "_lb_item", None) is not None:
                cv.coords(self._lb_item, cv.winfo_width() / 2 + self._lb_ox,
                          cv.winfo_height() / 2 + self._lb_oy)
        except Exception:
            pass

    def _lightbox_wheel(self, e=None):
        try:
            d = getattr(e, "delta", 0)
            if d > 0:
                self._lightbox_zoom(1.12)
            elif d < 0:
                self._lightbox_zoom(0.89)
            else:
                self._lightbox_zoom(1.12)
        except Exception:
            pass

    def _lightbox_close(self):
        try:
            if getattr(self, "_lb_job", None) is not None:
                try:
                    self.after_cancel(self._lb_job)
                except Exception:
                    pass
                self._lb_job = None
        except Exception:
            pass
        try:
            if hasattr(self, "_lb_overlay") and self._lb_overlay is not None and self._lb_overlay.winfo_exists():
                self._lb_overlay.destroy()
        except Exception:
            pass
        self._lb_overlay = None
        try:
            for seq in ("<plus>", "<minus>"):
                try:
                    self.unbind(seq)
                except Exception:
                    pass
            self.bind("<Left>", lambda e: self.gallery_prev())
            self.bind("<Right>", lambda e: self.gallery_next())
            self.bind("<Up>", lambda e: self.gallery_prev())
            self.bind("<Down>", lambda e: self.gallery_next())
            self.bind("<space>", lambda e: self.gallery_toggle_current())
            self.bind("<Return>", lambda e: self.gallery_toggle_current())
            self.bind("<f>", lambda e: self.open_photo(self.photos[self.view_index]))
            self.bind("<F>", lambda e: self.open_photo(self.photos[self.view_index]))
            self.bind("<Escape>", lambda e: self.go_setup())
        except Exception:
            pass
    def _gallery_unbind(self):
        for seq in ("<Left>", "<Right>", "<Up>", "<Down>", "<space>", "<Return>", "<f>", "<F>"):
            try:
                self.unbind(seq)
            except Exception:
                pass

    def go_setup(self):
        self._gallery_unbind()
        if self.mode != "normal" and (self.normal_selection or self.selected):
            self.confirm_modal("Ayarlara dönülsün mü?", "Mevcut seçimler silinecek. Devam edilsin mi?",
                               yes_text="Devam Et", no_text="Vazgeç", on_yes=self._build_setup)
            return
        self._build_setup()

    def finish(self):
        if not self.normal_selection:
            self.alert_modal("Hata", "Normal fotoğraf seçimi bulunamadı.", kind="error")
            return
        out = self.output_dir
        if out.exists():
            self.confirm_modal("Klasör zaten var", f"'{out.name}' klasörü zaten var. İçine kopyalansın mı?",
                               yes_text="Kopyala", no_text="Vazgeç", on_yes=self._do_finish)
            return
        self._do_finish()

    def _do_finish(self):
        out = self.output_dir
        try:
            total = len(self.normal_selection)
            try:
                self.toast(f"{total} fotoğraf kopyalanıyor...", kind="info")
            except Exception:
                pass
            self.update_idletasks()
            out.mkdir(parents=True, exist_ok=True)
            for i, src in enumerate(sorted(self.normal_selection, key=lambda p: p.name.lower()), 1):
                shutil.copy2(src, out / f"{i:03d}{src.suffix.lower()}")
            if self.cover: shutil.copy2(self.cover, out / f"ALBUM_KAPAK{self.cover.suffix.lower()}")
            if self.table: shutil.copy2(self.table, out / f"TABLO{self.table.suffix.lower()}")
        except Exception as e:
            self.alert_modal("Kopyalama hatası", str(e), kind="error")
            return
        self.alert_modal("Tamamlandı", f"Seçim tamamlandı!\n\nNormal: {len(self.normal_selection)}\nKapak: {'Evet' if self.cover else 'Hayır'}\nTablo: {'Evet' if self.table else 'Hayır'}\n\n{out}",
                         kind="success", ok_text="Tamam", on_ok=self._build_setup)

if __name__ == "__main__": App().mainloop()
    
