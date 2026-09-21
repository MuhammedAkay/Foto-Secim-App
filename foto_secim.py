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

IMAGE_EXTENSIONS={".jpg",".jpeg",".png",".webp",".bmp",".gif",".tif",".tiff"}
BG="#0b1014"; PANEL="#121a20"; PANEL2="#182129"; LINE="#29343c"; GOLD="#d9b77d"; GOLD2="#efd09b"; TEXT="#edf0f2"; MUTED="#89949c"; GREEN="#4fba78"
THUMB=(178,132)

class PhotoCard(tk.Frame):
    def __init__(self, master, path, on_click, on_double):
        super().__init__(master,bg=PANEL2,highlightbackground=LINE,highlightthickness=1,cursor="hand2")
        self.path=Path(path); self.on_click=on_click; self.on_double=on_double; self.selected=False; self.img_ref=None
        self.canvas=tk.Canvas(self,width=178,height=132,bg="#20282e",highlightthickness=0)
        self.canvas.pack(padx=5,pady=5); self.canvas.bind("<Button-1>",self._click); self.canvas.bind("<Double-Button-1>",self._double)
        self.name=tk.Label(self,text=self.path.name,bg=PANEL2,fg="#dce1e4",font=("Segoe UI",8),anchor="w")
        self.name.pack(fill="x",padx=7); self.name.bind("<Button-1>",self._click); self.name.bind("<Double-Button-1>",self._double)
        self.status=tk.Label(self,text="",bg=PANEL2,fg=GOLD,font=("Segoe UI",8,"bold")); self.status.pack(fill="x",pady=(2,5))
        for w in (self.status,): w.bind("<Button-1>",self._click)
        self.load(); self.refresh()
    def _click(self,e=None): self.on_click(self.path)
    def _double(self,e=None): self.on_double(self.path)
    def load(self):
        try:
            with Image.open(self.path) as im:
                im=im.convert("RGB"); im.thumbnail(THUMB,Image.Resampling.LANCZOS)
                bg=Image.new("RGB",THUMB,"#20282e"); bg.paste(im,((THUMB[0]-im.width)//2,(THUMB[1]-im.height)//2)); self.img_ref=ImageTk.PhotoImage(bg)
                self.canvas.create_image(THUMB[0]//2,THUMB[1]//2,image=self.img_ref)
        except Exception: self.canvas.create_text(89,66,text="Önizleme\naçılamadı",fill="#aaa")
    def refresh(self):
        if self.selected:
            self.configure(bg="#20372a",highlightbackground=GOLD,highlightthickness=2); self.status.configure(text="✓ SEÇİLDİ",bg="#20372a",fg="#8be1a9")
        else:
            self.configure(bg=PANEL2,highlightbackground=LINE,highlightthickness=1); self.status.configure(text="",bg=PANEL2)


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

def _corner_patches(parent_bg, outline, r, bw):
    size = r + bw + 1
    big = 4
    W = size * big
    disk_box = (size * big - r * big, size * big - r * big,
                size * big + r * big, size * big + r * big)
    base = Image.new("RGBA", (W, W), parent_bg)
    try:
        ImageDraw.Draw(base).arc(disk_box, start=180, end=270, fill=outline, width=max(1, bw * big))
    except Exception:
        pass
    mask = Image.new("L", (W, W), 255)
    ImageDraw.Draw(mask).ellipse(disk_box, fill=0)
    base.putalpha(mask)
    base = base.resize((size, size), Image.Resampling.LANCZOS)
    tl = ImageTk.PhotoImage(base)
    tr = ImageTk.PhotoImage(base.transpose(Image.FLIP_LEFT_RIGHT))
    bl = ImageTk.PhotoImage(base.transpose(Image.FLIP_TOP_BOTTOM))
    br = ImageTk.PhotoImage(base.transpose(Image.ROTATE_180))
    return tl, tr, bl, br

class RoundedFrame(tk.Frame):
    def __init__(self, master, radius=12, fill="#212c37", outline="#3a4750", border=1, parent_bg=None, **kw):
        pbg = parent_bg if parent_bg is not None else master.cget("bg")
        kw.pop("fixed_width", None)
        super().__init__(master, bg=outline, **kw)
        self.body = tk.Frame(self, bg=fill)
        self.body.pack(fill="both", expand=True, padx=border, pady=border)
        try:
            tl, tr, bl, br = _corner_patches(pbg, outline, radius, border)
            self._rf_refs = (tl, tr, bl, br)
            tk.Label(self, image=tl, bg=pbg, bd=0).place(x=0, y=0, anchor="nw")
            tk.Label(self, image=tr, bg=pbg, bd=0).place(relx=1, y=0, anchor="ne")
            tk.Label(self, image=bl, bg=pbg, bd=0).place(x=0, rely=1, anchor="sw")
            tk.Label(self, image=br, bg=pbg, bd=0).place(relx=1, rely=1, anchor="se")
        except Exception:
            self._rf_refs = ()

class GoldButton(tk.Canvas):
    def __init__(self, master, text, command, parent_bg, height=46, radius=11, font=("Segoe UI", 12, "bold"), width=None):
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
            if w < 10 or h < 10:
                return
            self.delete("gb")
            fill = "#e3c795" if self._gb_hover else "#cdb183"
            draw_rr(self, 1, 1, w - 1, h - 1, self._gb_r, fill=fill, tags="gb")
            self.create_text(w / 2, h / 2 + 1, text=self._gb_text, fill="#1a222a", font=self._gb_font, tags="gb")
        except Exception:
            pass

def rounded_photo_corners(cv, base_pil, x0, y0, wdt, hgt, r, tags):
    refs = []
    try:
        if base_pil is None or wdt < 60 or hgt < 60:
            return refs
        bw, bh = base_pil.size
        big = 4
        m0 = Image.new("L", (r * big, r * big), 255)
        ImageDraw.Draw(m0).ellipse((0, 0, r * big * 2, r * big * 2), fill=0)
        m0 = m0.resize((r, r), Image.Resampling.LANCZOS)
        spots = [(x0, y0, False, False), (x0 + wdt - r, y0, True, False),
                 (x0, y0 + hgt - r, False, True), (x0 + wdt - r, y0 + hgt - r, True, True)]
        for (px, py, fx, fy) in spots:
            if px < 0 or py < 0 or px + r > bw or py + r > bh:
                continue
            crop = base_pil.crop((px, py, px + r, py + r)).convert("RGBA")
            m = m0.transpose(Image.FLIP_LEFT_RIGHT) if fx else m0
            m = m.transpose(Image.FLIP_TOP_BOTTOM) if fy else m
            crop.putalpha(m)
            ref = ImageTk.PhotoImage(crop)
            refs.append(ref)
            cv.create_image(px, py, image=ref, anchor="nw", tags=tags)
    except Exception:
        pass
    return refs

class App(tk.Tk):
    def __init__(self):
        super().__init__(); self.title("FotoSecim • Düğün Fotoğraf Seçim Uygulaması"); self.geometry("1280x800"); self.minsize(1080,700); self.configure(bg=BG)
        self.folder=None; self.photos=[]; self.cards={}; self.selected=set(); self.normal_selection=set(); self.cover=None; self.table=None; self.mode="normal"; self.normal_count=50; self.cover_required=True; self.table_required=True; self.output_dir=None
        self.folder_var=tk.StringVar(value="Klasör seçin..."); self.output_name_var=tk.StringVar(value=""); self.count_var=tk.IntVar(value=50); self.cover_var=tk.BooleanVar(value=True); self.table_var=tk.BooleanVar(value=True); self.cover_count_var=tk.IntVar(value=1); self.table_count_var=tk.IntVar(value=1)
        self._is_painting = False
        self._build_setup(); self.bind("<Escape>",lambda e:self.go_setup())
    def clear(self):
        for w in self.winfo_children(): w.destroy()
    def gold_button(self,p,text,cmd,big=False):
        b=tk.Button(p,text=text,command=cmd,bg=GOLD,fg="#11161a",activebackground=GOLD2,activeforeground="#11161a",relief="flat",bd=0,cursor="hand2",font=("Segoe UI",12 if big else 10,"bold"),padx=18,pady=12 if big else 9); return b
    def dark_button(self,p,text,cmd):
        return tk.Button(p,text=text,command=cmd,bg=PANEL2,fg=TEXT,activebackground="#26343d",activeforeground="#fff",relief="flat",bd=0,cursor="hand2",font=("Segoe UI",10,"bold"),padx=12,pady=9)
    def card(self,p,title,subtitle=""):
        c=tk.Frame(p,bg=PANEL,highlightbackground=LINE,highlightthickness=1); h=tk.Frame(c,bg=PANEL); h.pack(fill="x",padx=18,pady=(15,3)); tk.Label(h,text=title,bg=PANEL,fg="#ead1a2",font=("Segoe UI",13,"bold")).pack(side="left")
        if subtitle: tk.Label(c,text=subtitle,bg=PANEL,fg=MUTED,font=("Segoe UI",9)).pack(anchor="w",padx=18,pady=(0,8))
        b=tk.Frame(c,bg=PANEL); b.pack(fill="both",expand=True,padx=18,pady=(2,18)); return c,b
    def _topbar(self,parent):
        bar=tk.Frame(parent,bg="#0f151a",height=48); bar.pack(fill="x"); bar.pack_propagate(False)
        tk.Label(bar,text="📷  FotoSecim",bg="#0f151a",fg="#f0e0c4",font=("Segoe UI",14,"bold")).pack(side="left",padx=22)
        tk.Label(bar,text="Düğün Fotoğraf Seçim Uygulaması",bg="#0f151a",fg="#7f8990",font=("Segoe UI",9)).pack(side="left")
    def _resource(self, *parts):
        base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent)) if "__file__" in globals() else Path.cwd()
        return base.joinpath(*parts)

    def _build_setup(self):
        self.clear()
        CARD = "#212c37"
        CARD2 = "#27333f"
        SHELL = "#161e25"
        FIELD = "#2b3641"
        SOFT = "#3a4750"
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
        self._bg_pil = None
        self._corner_refs = []
        self._setup_job = None
        root = tk.Frame(self, bg=BG)
        root.pack(fill="both", expand=True)
        cv = tk.Canvas(root, bg=BG, highlightthickness=0)
        cv.pack(fill="both", expand=True)
        self.setup_canvas = cv
        shell = tk.Frame(cv, bg=SHELL, bd=0, highlightthickness=0)
        self._setup_shell = shell
        inner = tk.Frame(shell, bg=SHELL)
        inner.pack(fill="both", expand=True, padx=18, pady=14)
        upper = tk.Frame(inner, bg=SHELL)
        upper.pack(fill="x")
        upper.grid_columnconfigure(0, weight=1)
        upper.grid_columnconfigure(1, weight=1)
        info = RoundedFrame(upper, radius=14, fill=CARD, outline=SOFT, parent_bg=SHELL)
        info.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        ibody = info.body
        tk.Label(ibody, text="📁  Albüm Bilgileri", bg=CARD, fg="#ead1a2", font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=14, pady=(10, 1))
        tk.Label(ibody, text="Fotoğrafların bulunduğu klasörü ve albüm adını belirleyin.", bg=CARD, fg=MUTED, font=("Segoe UI", 8), wraplength=330, justify="left").pack(anchor="w", padx=14, pady=(0, 8))
        tk.Label(ibody, text="Albüm Klasörü", bg=CARD, fg="#d7dce0", font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=14)
        fr = tk.Frame(ibody, bg=CARD)
        fr.pack(fill="x", padx=14, pady=(4, 8))
        fbox = RoundedFrame(fr, radius=8, fill=FIELD, outline="#43525c", parent_bg=CARD)
        fbox.pack(side="left", fill="x", expand=True, padx=(0, 6))
        folder_entry = tk.Entry(fbox.body, textvariable=self.folder_var, state="readonly", bg=FIELD, fg="#aeb7bd", readonlybackground=FIELD, relief="flat", bd=0, font=("Segoe UI", 9))
        folder_entry.pack(fill="x", padx=8, pady=6)
        GoldButton(fr, "📁", self.choose_folder, CARD, height=32, radius=8, font=("Segoe UI", 11, "bold"), width=48).pack(side="right")
        tk.Label(ibody, text="Albüm Adı (Klasör Adı)", bg=CARD, fg="#d7dce0", font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=14)
        abox = RoundedFrame(ibody, radius=8, fill=FIELD, outline="#43525c", parent_bg=CARD)
        abox.pack(fill="x", padx=14, pady=(4, 12))
        self.album_entry = tk.Entry(abox.body, textvariable=self.output_name_var, bg=FIELD, fg=TEXT, insertbackground=TEXT, relief="flat", bd=0, font=("Segoe UI", 9))
        self.album_entry.pack(fill="x", padx=8, pady=6)
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
        counts = RoundedFrame(upper, radius=14, fill=CARD, outline=SOFT, parent_bg=SHELL)
        counts.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        cbody = counts.body
        tk.Label(cbody, text="🖼  Seçim Sayıları", bg=CARD, fg="#ead1a2", font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=14, pady=(10, 1))
        tk.Label(cbody, text="Seçilmesi gereken fotoğraf adetlerini belirleyin.", bg=CARD, fg=MUTED, font=("Segoe UI", 8), wraplength=330, justify="left").pack(anchor="w", padx=14, pady=(0, 6))
        self.count_spins = {}
        self.count_badges = {}
        self.count_labels = {}
        def count_row(icon, label, var, enabled_var=None):
            row = tk.Frame(cbody, bg=CARD)
            row.pack(fill="x", padx=14, pady=5)
            ic = tk.Label(row, text=icon, bg=CARD, fg="#b7c0c6", font=("Segoe UI", 11))
            ic.pack(side="left", padx=(0, 8))
            lb = tk.Label(row, text=label, bg=CARD, fg="#d7dce0", font=("Segoe UI", 10))
            lb.pack(side="left")
            badge = tk.Label(row, text="(Zorunlu)", bg=CARD, fg="#7d888f", font=("Segoe UI", 8))
            badge.pack(side="right", padx=(6, 0))
            sbox = RoundedFrame(row, radius=8, fill=FIELD, outline="#43525c", parent_bg=CARD)
            sbox.pack(side="right")
            spin = tk.Spinbox(sbox.body, from_=1, to=99, textvariable=var, width=4, bg=FIELD, fg="#f0f2f4", buttonbackground="#2b3840", relief="flat", bd=0, font=("Segoe UI", 10, "bold"), justify="center", disabledbackground="#10171c", disabledforeground="#59636a", state="normal" if (enabled_var is None or enabled_var.get()) else "disabled")
            spin.pack(padx=6, pady=4)
            self.count_spins[label] = spin
            self.count_badges[label] = badge
            self.count_labels[label] = (lb, ic, row)
        count_row("🖼", "Normal Fotoğraf Sayısı", self.count_var)
        count_row("🖼", "Albüm Kapağı", self.cover_count_var, self.cover_var)
        count_row("🖼", "Tablo Fotoğrafı", self.table_count_var, self.table_var)
        extra = RoundedFrame(inner, radius=14, fill=CARD, outline=SOFT, parent_bg=SHELL)
        extra.pack(fill="x", pady=(10, 0))
        ebody = extra.body
        tk.Label(ebody, text="⚙  Ekstra Seçenekler", bg=CARD, fg="#ead1a2", font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=14, pady=(10, 1))
        tk.Label(ebody, text="İhtiyacınıza göre ek seçimleri aktif edebilirsiniz.", bg=CARD, fg=MUTED, font=("Segoe UI", 8)).pack(anchor="w", padx=14, pady=(0, 6))
        opts = tk.Frame(ebody, bg=CARD)
        opts.pack(fill="x", padx=14, pady=(0, 10))
        opts.grid_columnconfigure(0, weight=1)
        opts.grid_columnconfigure(1, weight=1)
        self.toggles = {}
        def make_toggle(parent, var):
            cvs = tk.Canvas(parent, width=40, height=22, bg=CARD2, highlightthickness=0, bd=0, cursor="hand2")
            def draw():
                on = bool(var.get())
                try:
                    cvs.delete("all")
                    draw_rr(cvs, 1, 1, 39, 21, 10, fill=("#c9a86a" if on else "#3a454e"), outline=("#c9a86a" if on else "#4a565f"), width=1, tags="tg")
                    x = 27 if on else 13
                    cvs.create_oval(x - 9, 3, x + 9, 19, fill="#f2ece1", outline="")
                except Exception:
                    pass
            draw()
            def flip(e=None):
                var.set(not var.get())
                draw()
                self._sync_optional_count_states()
            cvs.bind("<Button-1>", flip)
            var._toggle_draw = draw
            return cvs
        def option(icon, text, sub, var, column):
            box = RoundedFrame(opts, radius=10, fill=CARD2, outline="#3a4750", parent_bg=CARD)
            box.grid(row=0, column=column, sticky="ew", padx=4)
            top = tk.Frame(box.body, bg=CARD2)
            top.pack(fill="x", padx=10, pady=(8, 8))
            tk.Label(top, text=icon, bg=CARD2, fg="#c9a86a", font=("Segoe UI", 11)).pack(side="left", padx=(0, 7))
            tx = tk.Frame(top, bg=CARD2)
            tx.pack(side="left", fill="x", expand=True)
            tk.Label(tx, text=text, bg=CARD2, fg=TEXT, font=("Segoe UI", 10, "bold")).pack(anchor="w")
            tk.Label(tx, text=sub, bg=CARD2, fg="#8b959c", font=("Segoe UI", 8)).pack(anchor="w")
            sw = make_toggle(top, var)
            sw.pack(side="right", padx=(8, 0))
            self.toggles[text] = var
        option("🖼", "Albüm Kapağı Seç", "Kapak fotoğrafı seçimi yapılacak.", self.cover_var, 0)
        option("🖼", "Tablo Fotoğrafı Seç", "Tablo fotoğrafı seçimi yapılacak.", self.table_var, 1)
        GoldButton(inner, "▶   Başla", self.start, SHELL, height=46, radius=11).pack(fill="x", pady=(10, 0))
        self._setup_win = cv.create_window((0, 0), window=shell, anchor="n", width=780)
        self._sync_optional_count_states()
        def _on_cfg(e=None):
            if self._setup_job is not None:
                try: self.after_cancel(self._setup_job)
                except Exception: pass
            self._setup_job = self.after(150, self._setup_paint)
        cv.bind("<Configure>", _on_cfg)
        self.after(50, self._setup_paint)

    def _setup_paint(self):
        if getattr(self, "_is_painting", False):
            return
        self._is_painting = True
        self._setup_job = None
        cv = getattr(self, "setup_canvas", None)
        try:
            if cv is None or not cv.winfo_exists():
                self._is_painting = False
                return
            w = cv.winfo_width()
            h = cv.winfo_height()
            if w < 60 or h < 60:
                self._is_painting = False
                return
            cv.delete("bg", "hero", "foot", "round")
            src = getattr(self, "_bg_src", None)
            if src is not None:
                s = max(w / src.width, h / src.height)
                nw, nh = max(1, int(src.width * s)), max(1, int(src.height * s))
                img = src.resize((nw, nh), Image.Resampling.BILINEAR)
                left, top = (nw - w) // 2, (nh - h) // 2
                img = img.crop((left, top, left + w, top + h))
                self._bg_ref = ImageTk.PhotoImage(img)
                self._bg_pil = img
                cv.create_image(0, 0, image=self._bg_ref, anchor="nw", tags="bg")
            cx = w // 2
            ix, iy = cx, 46
            cv.create_rectangle(ix - 28, iy - 12, ix + 28, iy + 20, outline=GOLD2, width=3, tags="hero")
            cv.create_oval(ix - 12, iy - 6, ix + 12, iy + 18, outline=GOLD2, width=3, tags="hero")
            cv.create_rectangle(ix - 13, iy - 20, ix + 5, iy - 12, outline=GOLD2, width=3, tags="hero")
            cv.create_oval(ix + 18, iy - 6, ix + 24, iy + 0, fill=GOLD2, outline="", tags="hero")
            cv.create_text(cx, 98, text="Foto", anchor="e", fill="#f2ece1", font=("Segoe UI", 28, "bold"), tags="hero")
            cv.create_text(cx, 98, text="Secim", anchor="w", fill=GOLD2, font=("Segoe UI", 28, "bold"), tags="hero")
            cv.create_text(cx, 138, text="Düğün Fotoğraflarınız İçin Hızlı ve Kolay Seçim", fill="#e6e9eb", font=("Segoe UI", 11), tags="hero")
            cv.create_text(cx, 164, text="Müşterilerinizin fotoğraf seçimlerini kolaylaştırın.", fill="#9aa4ab", font=("Segoe UI", 9), tags="hero")
            cv.create_text(cx, 182, text="Siz sadece en güzel anlara odaklanın.", fill="#9aa4ab", font=("Segoe UI", 9), tags="hero")
            try:
                cv.coords(self._setup_win, cx, 204)
            except Exception:
                pass
            cv.create_rectangle(0, h - 32, w, h, fill="#0c1217", outline="", tags="foot")
            cv.create_text(14, h - 16, text="ⓘ  FotoSecim v1.3   |   Düğün Fotoğraf Seçim Uygulaması", anchor="w", fill="#6f7980", font=("Segoe UI", 8), tags="foot")
            cv.create_text(w - 14, h - 16, text="♡  Fotoğraf, en güzel hikayedir...", anchor="e", fill="#6f7980", font=("Segoe UI", 8), tags="foot")
            try:
                sw = self._setup_shell.winfo_width()
                sh = self._setup_shell.winfo_height()
                x0 = cx - sw // 2
                y0 = 204
                self._corner_refs = rounded_photo_corners(cv, getattr(self, "_bg_pil", None), x0, y0, sw, sh, 16, "round")
                draw_rr(cv, x0, y0, x0 + sw, y0 + sh, 16, fill=None, outline="#3d4a55", width=2, tags="round")
                cv.tag_raise("round")
            except Exception:
                pass
            try:
                cv.tag_lower("bg")
            except Exception:
                pass
        finally:
            self._is_painting = False

    def _sync_optional_count_states(self):
        if not hasattr(self,"count_spins"): return
        for label,var in [("Alb\u00fcm Kapa\u011f\u0131",self.cover_var),("Tablo Foto\u011fraf\u0131",self.table_var)]:
            on=bool(var.get())
            spin=self.count_spins.get(label)
            if spin is not None:
                try: spin.configure(state=("normal" if on else "disabled"))
                except Exception: pass
            badge=self.count_badges.get(label) if hasattr(self,"count_badges") else None
            if badge is not None:
                try: badge.configure(text="(Zorunlu)" if on else "(Kapal\u0131)",fg="#7d888f" if on else "#525b61")
                except Exception: pass
            labs=getattr(self,"count_labels",{}).get(label)
            if labs:
                lb,ic,row=labs
                try:
                    lb.configure(fg="#d7dce0" if on else "#525b61"); ic.configure(fg="#b7c0c6" if on else "#525b61")
                except Exception: pass
            try:
                draw=getattr(var,"_toggle_draw",None)
                if callable(draw): draw()
            except Exception: pass

    def choose_folder(self):
        f=filedialog.askdirectory(title="Fotoğrafların bulunduğu klasörü seçin");
        if f: self.folder=Path(f); self.folder_var.set(str(self.folder))
    def start(self):
        if not self.folder: messagebox.showwarning("Klasör gerekli","Önce fotoğrafların bulunduğu klasörü seçin."); return
        try: count=int(self.count_var.get())
        except: messagebox.showwarning("Geçersiz sayı","Normal fotoğraf sayısını doğru girin."); return
        album_name=self.output_name_var.get().strip()
        if getattr(self,"_album_placeholder",None) and album_name==self._album_placeholder: album_name=""
        if count<1 or not album_name: messagebox.showwarning("Eksik bilgi","Fotoğraf sayısı ve albüm adı boş olamaz."); return
        photos=sorted([p for p in self.folder.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS],key=lambda p:p.name.lower())
        try:
            cover_count=int(self.cover_count_var.get()) if self.cover_var.get() else 0
            table_count=int(self.table_count_var.get()) if self.table_var.get() else 0
        except Exception:
            messagebox.showwarning("Geçersiz sayı","Kapak ve tablo adetlerini doğru girin."); return
        if cover_count not in (0,1) or table_count not in (0,1):
            messagebox.showinfo("Tek fotoğraf","Bu sürümde albüm kapağı ve tablo seçimi birer fotoğraf olarak uygulanıyor. Adet alanlarının çoklu seçim desteğini sonraki adımda bağlayacağız.")
            return
        needed=count+cover_count+table_count
        if not photos: messagebox.showerror("Fotoğraf bulunamadı","Klasörde desteklenen fotoğraf bulunamadı."); return
        if len(photos)<needed: messagebox.showwarning("Fotoğraf sayısı yetersiz",f"Klasörde {len(photos)} fotoğraf var; en az {needed} fotoğraf gerekiyor."); return
        self.photos=photos; self.normal_count=count; self.cover_required=self.cover_var.get(); self.table_required=self.table_var.get(); self.output_dir=self.folder/album_name; self.selected.clear(); self.normal_selection.clear(); self.cover=None; self.table=None; self.mode="normal"; self._selection_page()
    def _selection_page(self):
        self.clear(); root=tk.Frame(self,bg=BG); root.pack(fill="both",expand=True); self._topbar(root)
        head=tk.Frame(root,bg=BG); head.pack(fill="x",padx=22,pady=(15,7)); left=tk.Frame(head,bg=BG); left.pack(side="left"); self.step=tk.Label(left,text="1  •  NORMAL FOTOĞRAFLAR",bg=BG,fg=GOLD2,font=("Segoe UI",16,"bold")); self.step.pack(anchor="w"); self.sub=tk.Label(left,text=f"{len(self.photos)} fotoğraf bulundu  •  {self.folder.name}",bg=BG,fg=MUTED,font=("Segoe UI",9)); self.sub.pack(anchor="w",pady=(2,0)); self.counter=tk.Label(head,text="",bg=BG,fg=TEXT,font=("Segoe UI",12,"bold")); self.counter.pack(side="right")
        controls=tk.Frame(root,bg=BG); controls.pack(fill="x",padx=22,pady=(0,9)); self.dark_button(controls,"← Ayarlar",self.go_setup).pack(side="left"); self.dark_button(controls,"↻ Temizle",self.clear_current).pack(side="left",padx=7); self.gold_button(controls,"İLERİ  →",self.next_step).pack(side="right")
        body=tk.Frame(root,bg=BG); body.pack(fill="both",expand=True,padx=22,pady=(0,18)); body.columnconfigure(0,weight=3); body.columnconfigure(1,weight=1); body.rowconfigure(0,weight=1)
        main=tk.Frame(body,bg=PANEL,highlightbackground=LINE,highlightthickness=1); main.grid(row=0,column=0,sticky="nsew",padx=(0,7)); main.rowconfigure(1,weight=1); main.columnconfigure(0,weight=1)
        self.preview=tk.Label(main,text="Fotoğraf seçmek için bir görsele tıklayın",bg="#0f151a",fg="#65717a",font=("Segoe UI",12)); self.preview.grid(row=0,column=0,sticky="ew",padx=10,pady=10,ipady=30)
        self.canvas=tk.Canvas(main,bg="#0f151a",highlightthickness=0); self.canvas.grid(row=1,column=0,sticky="nsew",padx=10,pady=(0,10)); sb=ttk.Scrollbar(main,orient="vertical",command=self.canvas.yview); sb.grid(row=1,column=1,sticky="ns",pady=(0,10)); self.canvas.configure(yscrollcommand=sb.set)
        self.grid_frame=tk.Frame(self.canvas,bg="#0f151a"); self.win=self.canvas.create_window((0,0),window=self.grid_frame,anchor="nw"); self.grid_frame.bind("<Configure>",lambda e:self.canvas.configure(scrollregion=self.canvas.bbox("all"))); self.canvas.bind("<Configure>",lambda e:self.reflow(e.width)); self.canvas.bind_all("<MouseWheel>",lambda e:self.canvas.yview_scroll(int(-e.delta/120),"units"))
        side=tk.Frame(body,bg=PANEL,highlightbackground=LINE,highlightthickness=1); side.grid(row=0,column=1,sticky="nsew",padx=(7,0));
        self.side_title=tk.Label(side,text="SEÇİM BİLGİLERİ",bg=PANEL,fg=GOLD2,font=("Segoe UI",12,"bold")); self.side_title.pack(anchor="w",padx=18,pady=(18,5)); self.side_info=tk.Label(side,text="",justify="left",bg=PANEL,fg=TEXT,font=("Segoe UI",10),anchor="nw"); self.side_info.pack(fill="x",padx=18,pady=10)
        tk.Frame(side,bg=LINE,height=1).pack(fill="x",padx=18,pady=8)
        tk.Label(side,text="İPUCU",bg=PANEL,fg=GOLD,font=("Segoe UI",9,"bold")).pack(anchor="w",padx=18); tk.Label(side,text="Tek tık: seç / kaldır\nÇift tık: büyük görüntü\nSeçimler yeşil çerçeveyle gösterilir.",bg=PANEL,fg=MUTED,font=("Segoe UI",9),justify="left").pack(anchor="w",padx=18,pady=7)
        self._render(); self._update()
    def reflow(self,width):
        cols=max(2,min(5,width//200))
        for i,c in enumerate(self.cards.values()): c.grid(row=i//cols,column=i%cols,padx=6,pady=6,sticky="n")
    def _render(self):
        for w in self.grid_frame.winfo_children(): w.destroy()
        self.cards={}
        for p in self.photos: self.cards[p]=PhotoCard(self.grid_frame,p,self.toggle,self.open_photo)
        self.after(60,lambda:self.reflow(self.canvas.winfo_width()))
    def toggle(self,path):
        if self.mode=="normal":
            if path in self.selected:self.selected.remove(path)
            elif len(self.selected)<self.normal_count:self.selected.add(path)
            else: messagebox.showinfo("Limit doldu",f"En fazla {self.normal_count} normal fotoğraf seçebilirsiniz."); return
        else:
            self.selected={path}
            self.preview_photo(path)
        self.refresh(); self._update()
    def refresh(self):
        for p,c in self.cards.items(): c.selected=p in self.selected; c.refresh()
    def preview_photo(self,path):
        try:
            with Image.open(path) as im:
                im=im.convert("RGB"); im.thumbnail((700,250),Image.Resampling.LANCZOS); self.prev_ref=ImageTk.PhotoImage(im.copy()); self.preview.configure(image=self.prev_ref,text="")
        except: pass
    def _update(self):
        if self.mode=="normal":
            self.step.configure(text="1  •  NORMAL FOTOĞRAFLAR"); self.counter.configure(text=f"Seçilen  {len(self.selected)} / {self.normal_count}"); self.side_info.configure(text=f"Normal fotoğraf\n{len(self.selected)} / {self.normal_count}\n\nKlasör\n{self.folder.name}")
        elif self.mode=="cover":
            self.step.configure(text="2  •  ALBÜM KAPAĞI"); self.counter.configure(text=f"Kapak  {1 if self.selected else 0} / 1"); self.side_info.configure(text="Kapak olarak kullanılacak 1 fotoğraf seçin.\n\nSeçtiğiniz fotoğraf doğrudan kapak olarak kopyalanacaktır.")
        else:
            self.step.configure(text="3  •  TABLO FOTOĞRAFI"); self.counter.configure(text=f"Tablo  {1 if self.selected else 0} / 1"); self.side_info.configure(text="Tablo için kullanılacak fotoğrafı seçin.\n\nTek fotoğraf seçilebilir.")
    def clear_current(self): self.selected.clear(); self.refresh(); self._update()
    def next_step(self):
        if self.mode=="normal":
            if len(self.selected)!=self.normal_count: messagebox.showwarning("Seçim tamamlanmadı",f"Tam olarak {self.normal_count} normal fotoğraf seçmelisiniz."); return
            self.normal_selection=set(self.selected)
            if self.cover_required:self.mode="cover"; self.selected.clear(); self.show_cover_mode()
            elif self.table_required:self.mode="table"; self.selected.clear(); self._selection_refresh()
            else:self.finish()
        elif self.mode=="cover":
            if len(self.selected)!=1: messagebox.showwarning("Kapak seçilmedi","Lütfen 1 adet kapak fotoğrafı seçin."); return
            self.cover=next(iter(self.selected))
            if self.table_required:
                self.mode="table"; self.selected.clear(); self._selection_refresh()
            else:
                self.finish()
        elif self.mode=="table":
            if len(self.selected)!=1: messagebox.showwarning("Tablo seçilmedi","Lütfen 1 adet tablo fotoğrafı seçin."); return
            self.table=next(iter(self.selected)); self.finish()
    def _selection_refresh(self): self._selection_page(); self.mode=self.mode; self._update()
    def show_cover_mode(self): self._selection_page(); self.mode="cover"; self._update()
    def open_photo(self,path):
        try:
            im=Image.open(path).convert("RGB"); im.thumbnail((1050,700),Image.Resampling.LANCZOS); ref=ImageTk.PhotoImage(im.copy()); w=tk.Toplevel(self); w.title(path.name); w.configure(bg="#000"); tk.Label(w,image=ref,bg="#000").pack(padx=10,pady=10); w.image=ref
        except Exception as e: messagebox.showerror("Fotoğraf açılamadı",str(e))
    def go_setup(self):
        if self.mode!="normal" and (self.normal_selection or self.selected):
            if not messagebox.askyesno("Ayarlar","Ayarlar ekranına dönerseniz mevcut seçimler silinecek. Devam edilsin mi?"): return
        self._build_setup()
    def finish(self):
        if not self.normal_selection: messagebox.showerror("Hata","Normal fotoğraf seçimi bulunamadı."); return
        out=self.output_dir
        if out.exists() and not messagebox.askyesno("Klasör zaten var",f"'{out.name}' klasörü zaten var. İçine kopyalansın mı?"): return
        try:
            out.mkdir(parents=True,exist_ok=True)
            for i,src in enumerate(sorted(self.normal_selection,key=lambda p:p.name.lower()),1): shutil.copy2(src,out/f"{i:03d}{src.suffix.lower()}")
            if self.cover: shutil.copy2(self.cover,out/f"ALBUM_KAPAK{self.cover.suffix.lower()}")
            if self.table: shutil.copy2(self.table,out/f"TABLO{self.table.suffix.lower()}")
        except Exception as e: messagebox.showerror("Kopyalama hatası",str(e)); return
        messagebox.showinfo("Tamamlandı",f"Seçim tamamlandı!\n\nNormal: {len(self.normal_selection)}\nKapak: {'Evet' if self.cover else 'Hayır'}\nTablo: {'Evet' if self.table else 'Hayır'}\n\n{out}"); self._build_setup()

if __name__=="__main__": App().mainloop()
