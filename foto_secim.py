# -*- coding: utf-8 -*-
"""FotoSecim - Windows düğün fotoğrafı seçim uygulaması."""
import os
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

class App(tk.Tk):
    def __init__(self):
        super().__init__(); self.title("FotoSecim • Düğün Fotoğraf Seçim Uygulaması"); self.geometry("1320x820"); self.minsize(1050,680); self.configure(bg=BG)
        self.folder=None; self.photos=[]; self.cards={}; self.selected=set(); self.normal_selection=set(); self.cover=None; self.table=None; self.mode="normal"; self.normal_count=50; self.cover_required=True; self.table_required=True; self.output_dir=None
        self.folder_var=tk.StringVar(value="Klasör seçin..."); self.output_name_var=tk.StringVar(value=""); self.count_var=tk.IntVar(value=50); self.cover_var=tk.BooleanVar(value=True); self.table_var=tk.BooleanVar(value=True); self.cover_count_var=tk.IntVar(value=1); self.table_count_var=tk.IntVar(value=1)
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
    def _build_setup(self):
        self.clear()
        CARD="#1b242e"; CARD2="#232f39"; SHELL="#131b21"; FIELD="#232f39"
        root=tk.Frame(self,bg=BG); root.pack(fill="both",expand=True)
        self._topbar(root)
        content=tk.Frame(root,bg=BG); content.pack(fill="both",expand=True)
        wrap=tk.Frame(content,bg=BG); wrap.pack(expand=True,fill="both",padx=20,pady=(14,8))
        center=tk.Frame(wrap,bg=BG,width=800); center.pack(expand=True,anchor="center"); center.pack_propagate(True)
        hero=tk.Frame(center,bg=BG); hero.pack(fill="x",pady=(0,14))
        tk.Label(hero,text="\u25cb \U0001F4F7 \u25cb",bg=BG,fg=GOLD2,font=("Segoe UI",26)).pack()
        title=tk.Frame(hero,bg=BG); title.pack()
        tk.Label(title,text="Foto",bg=BG,fg="#f2ece1",font=("Segoe UI",28,"bold")).pack(side="left")
        tk.Label(title,text="Secim",bg=BG,fg=GOLD2,font=("Segoe UI",28,"bold")).pack(side="left")
        tk.Label(hero,text="D\u00fc\u011f\u00fcn Foto\u011fraflar\u0131n\u0131z \u0130\u00e7in H\u0131zl\u0131 ve Kolay Se\u00e7im",bg=BG,fg="#e1e4e6",font=("Segoe UI",12)).pack(pady=(2,0))
        tk.Label(hero,text="M\u00fc\u015fterilerinizin foto\u011fraf se\u00e7imlerini kolayla\u015ft\u0131r\u0131n.\nSiz sadece en g\u00fczel anlara odaklan\u0131n.",bg=BG,fg=MUTED,font=("Segoe UI",9),justify="center").pack(pady=(8,0))
        shell=tk.Frame(center,bg=SHELL,highlightbackground="#2b3840",highlightthickness=1); shell.pack(fill="x",expand=False,padx=40)
        inner=tk.Frame(shell,bg=SHELL); inner.pack(fill="both",expand=True,padx=18,pady=16)
        upper=tk.Frame(inner,bg=SHELL); upper.pack(fill="x"); upper.grid_columnconfigure(0,weight=1); upper.grid_columnconfigure(1,weight=1)
        info=tk.Frame(upper,bg=CARD,highlightbackground=LINE,highlightthickness=1); info.grid(row=0,column=0,sticky="nsew",padx=(0,6))
        tk.Label(info,text="\U0001F4C1  Alb\u00fcm Bilgileri",bg=CARD,fg="#ead1a2",font=("Segoe UI",11,"bold")).pack(anchor="w",padx=14,pady=(12,1))
        tk.Label(info,text="Foto\u011fraflar\u0131n bulundu\u011fu klas\u00f6r\u00fc ve alb\u00fcm ad\u0131n\u0131 belirleyin.",bg=CARD,fg=MUTED,font=("Segoe UI",8)).pack(anchor="w",padx=14,pady=(0,10))
        tk.Label(info,text="Alb\u00fcm Klas\u00f6r\u00fc",bg=CARD,fg="#d7dce0",font=("Segoe UI",9,"bold")).pack(anchor="w",padx=14)
        fr=tk.Frame(info,bg=CARD); fr.pack(fill="x",padx=14,pady=(4,10))
        folder_entry=tk.Entry(fr,textvariable=self.folder_var,state="readonly",bg=FIELD,fg="#aeb7bd",readonlybackground=FIELD,relief="flat",font=("Segoe UI",9)); folder_entry.pack(side="left",fill="x",expand=True,ipady=7,padx=(0,6))
        tk.Button(fr,text="\U0001F4C1",command=self.choose_folder,bg=GOLD,fg="#11161a",activebackground=GOLD2,relief="flat",bd=0,cursor="hand2",font=("Segoe UI",10,"bold"),padx=10,pady=4).pack(side="right")
        tk.Label(info,text="Alb\u00fcm Ad\u0131 (Klas\u00f6r Ad\u0131)",bg=CARD,fg="#d7dce0",font=("Segoe UI",9,"bold")).pack(anchor="w",padx=14)
        self.album_entry=tk.Entry(info,textvariable=self.output_name_var,bg=FIELD,fg=TEXT,insertbackground=TEXT,relief="flat",bd=0,font=("Segoe UI",9)); self.album_entry.pack(fill="x",padx=14,pady=(4,14),ipady=7)
        self._album_placeholder="\u00d6rn: Ay\u015fe & Mehmet"
        def _album_focus_in(e=None):
            if self.output_name_var.get()==self._album_placeholder: self.output_name_var.set(""); self.album_entry.configure(fg=TEXT)
        def _album_focus_out(e=None):
            if not self.output_name_var.get().strip(): self.output_name_var.set(self._album_placeholder); self.album_entry.configure(fg="#7d888f")
        if not self.output_name_var.get().strip(): self.output_name_var.set(self._album_placeholder); self.album_entry.configure(fg="#7d888f")
        self.album_entry.bind("<FocusIn>",_album_focus_in); self.album_entry.bind("<FocusOut>",_album_focus_out)
        counts=tk.Frame(upper,bg=CARD,highlightbackground=LINE,highlightthickness=1); counts.grid(row=0,column=1,sticky="nsew",padx=(6,0))
        tk.Label(counts,text="\U0001F5BC  Se\u00e7im Say\u0131lar\u0131",bg=CARD,fg="#ead1a2",font=("Segoe UI",11,"bold")).pack(anchor="w",padx=14,pady=(12,1))
        tk.Label(counts,text="Se\u00e7ilmesi gereken foto\u011fraf adetlerini belirleyin.",bg=CARD,fg=MUTED,font=("Segoe UI",8)).pack(anchor="w",padx=14,pady=(0,8))
        self.count_spins={}; self.count_badges={}; self.count_labels={}
        def count_row(icon,label,var,enabled_var=None,fixed=False):
            row=tk.Frame(counts,bg=CARD); row.pack(fill="x",padx=14,pady=5)
            ic=tk.Label(row,text=icon,bg=CARD,fg="#b7c0c6",font=("Segoe UI",11)); ic.pack(side="left",padx=(0,8))
            lb=tk.Label(row,text=label,bg=CARD,fg="#d7dce0",font=("Segoe UI",10)); lb.pack(side="left")
            badge=tk.Label(row,text="(Zorunlu)",bg=CARD,fg="#7d888f",font=("Segoe UI",8)); badge.pack(side="right",padx=(6,0))
            spin=tk.Spinbox(row,from_=1,to=99,textvariable=var,width=5,bg=FIELD,fg="#f0f2f4",buttonbackground="#2b3840",relief="flat",font=("Segoe UI",10,"bold"),justify="center",disabledbackground="#10171c",disabledforeground="#59636a",state="normal" if (enabled_var is None or enabled_var.get()) else "disabled")
            spin.pack(side="right",ipady=4)
            self.count_spins[label]=spin; self.count_badges[label]=badge; self.count_labels[label]=(lb,ic,row)
        count_row("\U0001F5BC","Normal Foto\u011fraf Say\u0131s\u0131",self.count_var)
        count_row("\U0001F5BC","Alb\u00fcm Kapa\u011f\u0131",self.cover_count_var,self.cover_var)
        count_row("\U0001F5BC","Tablo Foto\u011fraf\u0131",self.table_count_var,self.table_var)
        extra=tk.Frame(inner,bg=CARD,highlightbackground=LINE,highlightthickness=1); extra.pack(fill="x",pady=(12,0))
        tk.Label(extra,text="\u2699  Ekstra Se\u00e7enekler",bg=CARD,fg="#ead1a2",font=("Segoe UI",11,"bold")).pack(anchor="w",padx=14,pady=(12,1))
        tk.Label(extra,text="\u0130htiyac\u0131n\u0131za g\u00f6re ek se\u00e7imleri aktif edebilirsiniz.",bg=CARD,fg=MUTED,font=("Segoe UI",8)).pack(anchor="w",padx=14,pady=(0,8))
        opts=tk.Frame(extra,bg=CARD); opts.pack(fill="x",padx=14,pady=(0,12)); opts.grid_columnconfigure(0,weight=1); opts.grid_columnconfigure(1,weight=1)
        self.toggles={}
        def make_toggle(parent,var):
            cv=tk.Canvas(parent,width=40,height=22,bg=CARD2,highlightthickness=0,bd=0,cursor="hand2")
            def draw():
                on=bool(var.get())
                cv.delete("all")
                cv.create_rectangle(1,1,39,21,fill="#c9a86a" if on else "#3a454e",outline="#c9a86a" if on else "#4a565f",width=1)
                x=27 if on else 13
                cv.create_oval(x-9,3,x+9,19,fill="#f2ece1",outline="")
            draw()
            def flip(e=None):
                var.set(not var.get()); draw(); self._sync_optional_count_states()
            cv.bind("<Button-1>",flip)
            var._toggle_draw=draw
            return cv
        def option(icon,text,sub,var,column):
            box=tk.Frame(opts,bg=CARD2,highlightbackground=LINE,highlightthickness=1); box.grid(row=0,column=column,sticky="ew",padx=4)
            top=tk.Frame(box,bg=CARD2); top.pack(fill="x",padx=10,pady=(10,0))
            tk.Label(top,text=icon,bg=CARD2,fg="#c9a86a",font=("Segoe UI",11)).pack(side="left",padx=(0,7))
            tx=tk.Frame(top,bg=CARD2); tx.pack(side="left",fill="x",expand=True)
            tk.Label(tx,text=text,bg=CARD2,fg=TEXT,font=("Segoe UI",10,"bold")).pack(anchor="w")
            tk.Label(tx,text=sub,bg=CARD2,fg="#8b959c",font=("Segoe UI",8)).pack(anchor="w")
            sw=make_toggle(top,var); sw.pack(side="right",padx=(8,0))
            self.toggles[text]=var
            box.bind("<Button-1>",lambda e: (var.set(not var.get()), self._sync_optional_count_states()))
        option("\U0001F5BC","Alb\u00fcm Kapa\u011f\u0131 Se\u00e7","Kapak foto\u011fraf\u0131 se\u00e7imi yap\u0131lacak.",self.cover_var,0)
        option("\U0001F5BC","Tablo Foto\u011fraf\u0131 Se\u00e7","Tablo foto\u011fraf\u0131 se\u00e7imi yap\u0131lacak.",self.table_var,1)
        self._sync_optional_count_states()
        tk.Button(inner,text="\u25b6   Ba\u015fla",command=self.start,bg="#cdb183",fg="#1a222a",activebackground="#e3c795",activeforeground="#1a222a",relief="flat",bd=0,cursor="hand2",font=("Segoe UI",12,"bold"),pady=10).pack(fill="x",pady=(12,0))
        footer=tk.Frame(root,bg="#0f151a",height=34); footer.pack(fill="x",side="bottom"); footer.pack_propagate(False)
        tk.Label(footer,text="  \u24d8  FotoSecim v1.3   |   D\u00fc\u011f\u00fcn Foto\u011fraf Se\u00e7im Uygulamas\u0131",bg="#0f151a",fg="#6f7980",font=("Segoe UI",8)).pack(side="left")
        tk.Label(footer,text="\u2661  Foto\u011fraf, en g\u00fczel hikayedir...  ",bg="#0f151a",fg="#6f7980",font=("Segoe UI",8)).pack(side="right")

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
