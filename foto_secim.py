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
        self.folder_var=tk.StringVar(value="Klasör seçilmedi"); self.output_name_var=tk.StringVar(value="Albüm"); self.count_var=tk.IntVar(value=50); self.cover_var=tk.BooleanVar(value=True); self.table_var=tk.BooleanVar(value=True); self.cover_count_var=tk.IntVar(value=1); self.table_count_var=tk.IntVar(value=1)
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
        root=tk.Frame(self,bg=BG); root.pack(fill="both",expand=True)
        self._topbar(root)
        content=tk.Frame(root,bg=BG); content.pack(fill="both",expand=True,padx=44,pady=(26,18))
        hero=tk.Frame(content,bg=BG); hero.pack(fill="x",pady=(0,20))
        tk.Label(hero,text="▣",bg=BG,fg=GOLD2,font=("Segoe UI Symbol",34,"bold")).pack()
        tk.Label(hero,text="FotoSecim",bg=BG,fg="#f1e8dc",font=("Segoe UI",31,"bold")).pack(pady=(0,2))
        tk.Label(hero,text="Düğün Fotoğraflarınız İçin Hızlı ve Kolay Seçim",bg=BG,fg="#e1e4e6",font=("Segoe UI",13)).pack()
        tk.Label(hero,text="Müşterilerinizin fotoğraf seçimlerini kolaylaştırın.\nSiz sadece en güzel anlara odaklanın.",bg=BG,fg=MUTED,font=("Segoe UI",9),justify="center").pack(pady=(9,0))
        shell=tk.Frame(content,bg="#0f171d",highlightbackground="#2b3840",highlightthickness=1); shell.pack(fill="both",expand=True,padx=105)
        upper=tk.Frame(shell,bg="#0f171d"); upper.pack(fill="x",padx=24,pady=(20,0)); upper.columnconfigure(0,weight=1); upper.columnconfigure(1,weight=1)
        info=tk.Frame(upper,bg=PANEL,highlightbackground=LINE,highlightthickness=1); info.grid(row=0,column=0,sticky="nsew",padx=(0,6))
        tk.Label(info,text="▣  Albüm Bilgileri",bg=PANEL,fg="#ead1a2",font=("Segoe UI",12,"bold")).pack(anchor="w",padx=18,pady=(14,2))
        tk.Label(info,text="Fotoğrafların bulunduğu klasörü ve albüm adını belirleyin.",bg=PANEL,fg=MUTED,font=("Segoe UI",9)).pack(anchor="w",padx=18,pady=(0,14))
        tk.Label(info,text="Albüm Klasörü",bg=PANEL,fg="#d7dce0",font=("Segoe UI",9,"bold")).pack(anchor="w",padx=18)
        fr=tk.Frame(info,bg=PANEL); fr.pack(fill="x",padx=18,pady=(5,13))
        tk.Entry(fr,textvariable=self.folder_var,state="readonly",bg=PANEL2,fg="#aeb7bd",readonlybackground=PANEL2,relief="flat",font=("Segoe UI",10)).pack(side="left",fill="x",expand=True,ipady=9,padx=(0,7))
        self.dark_button(fr,"📁  Seç",self.choose_folder).pack(side="right")
        tk.Label(info,text="Albüm Adı (Klasör Adı)",bg=PANEL,fg="#d7dce0",font=("Segoe UI",9,"bold")).pack(anchor="w",padx=18)
        tk.Entry(info,textvariable=self.output_name_var,bg=PANEL2,fg=TEXT,insertbackground=TEXT,relief="flat",bd=0,font=("Segoe UI",10)).pack(fill="x",padx=18,pady=(5,18),ipady=9)
        counts=tk.Frame(upper,bg=PANEL,highlightbackground=LINE,highlightthickness=1); counts.grid(row=0,column=1,sticky="nsew",padx=(6,0))
        tk.Label(counts,text="▧  Seçim Sayıları",bg=PANEL,fg="#ead1a2",font=("Segoe UI",12,"bold")).pack(anchor="w",padx=18,pady=(14,2))
        tk.Label(counts,text="Müşterinin seçmesi gereken fotoğraf adetlerini belirleyin.",bg=PANEL,fg=MUTED,font=("Segoe UI",9)).pack(anchor="w",padx=18,pady=(0,10))
        self.count_spins={}
        def count_row(label,var,enabled_var=None):
            row=tk.Frame(counts,bg=PANEL); row.pack(fill="x",padx=18,pady=4)
            tk.Label(row,text="▧",bg=PANEL,fg="#b7c0c6",font=("Segoe UI Symbol",12)).pack(side="left",padx=(0,9))
            tk.Label(row,text=label,bg=PANEL,fg="#d7dce0",font=("Segoe UI",10)).pack(side="left")
            spin=tk.Spinbox(row,from_=1,to=9999,textvariable=var,width=7,bg=PANEL2,fg="#f0f2f4",buttonbackground="#29343c",relief="flat",font=("Segoe UI",10),justify="center",disabledbackground="#10171c",disabledforeground="#59636a")
            spin.pack(side="right",ipady=5); self.count_spins[label]=spin
            if enabled_var is not None: enabled_var.trace_add("write",lambda *_: self._sync_optional_count_states())
        count_row("Normal Fotoğraf Sayısı",self.count_var)
        count_row("Albüm Kapağı",self.cover_count_var,self.cover_var)
        count_row("Tablo Fotoğrafı",self.table_count_var,self.table_var)
        extra=tk.Frame(shell,bg="#0f171d"); extra.pack(fill="x",padx=24,pady=(14,0))
        ec=tk.Frame(extra,bg=PANEL,highlightbackground=LINE,highlightthickness=1); ec.pack(fill="x")
        tk.Label(ec,text="⚙  Ekstra Seçenekler",bg=PANEL,fg="#ead1a2",font=("Segoe UI",12,"bold")).pack(anchor="w",padx=18,pady=(14,2))
        tk.Label(ec,text="İhtiyacınıza göre ek fotoğraf seçimlerini aktif edebilirsiniz.",bg=PANEL,fg=MUTED,font=("Segoe UI",9)).pack(anchor="w",padx=18,pady=(0,10))
        opts=tk.Frame(ec,bg=PANEL); opts.pack(fill="x",padx=18,pady=(0,15)); opts.grid_columnconfigure(0,weight=1); opts.grid_columnconfigure(1,weight=1)
        def option(text,sub,var,column):
            row=tk.Frame(opts,bg=PANEL2,highlightbackground=LINE,highlightthickness=1); row.grid(row=0,column=column,sticky="ew",padx=4)
            tk.Checkbutton(row,text=text,variable=var,bg=PANEL2,fg=TEXT,activebackground=PANEL2,activeforeground="#fff",selectcolor=PANEL2,font=("Segoe UI",10,"bold"),command=self._sync_optional_count_states).pack(anchor="w",padx=10,pady=(8,0))
            tk.Label(row,text=sub,bg=PANEL2,fg="#7f8990",font=("Segoe UI",8)).pack(anchor="w",padx=34,pady=(0,8))
        option("▧  Albüm Kapağı Seç","Kapak fotoğrafı seçimi yapılacak.",self.cover_var,0)
        option("▧  Tablo Fotoğrafı Seç","Tablo fotoğrafı seçimi yapılacak.",self.table_var,1)
        self._sync_optional_count_states()
        self.gold_button(shell,"▶   BAŞLA",self.start,big=True).pack(fill="x",padx=24,pady=(16,22))
        tk.Label(root,text="FotoSecim v1.3   •   Düğün Fotoğraf Seçim Uygulaması",bg="#0f151a",fg="#6f7980",font=("Segoe UI",8),anchor="w").pack(fill="x",side="bottom",ipady=9,padx=22)

    def _sync_optional_count_states(self):
        if not hasattr(self,"count_spins"): return
        for label,var in [("Albüm Kapağı",self.cover_var),("Tablo Fotoğrafı",self.table_var)]:
            spin=self.count_spins.get(label)
            if spin: spin.configure(state=("normal" if var.get() else "disabled"))

    def choose_folder(self):
        f=filedialog.askdirectory(title="Fotoğrafların bulunduğu klasörü seçin");
        if f: self.folder=Path(f); self.folder_var.set(str(self.folder))
    def start(self):
        if not self.folder: messagebox.showwarning("Klasör gerekli","Önce fotoğrafların bulunduğu klasörü seçin."); return
        try: count=int(self.count_var.get())
        except: messagebox.showwarning("Geçersiz sayı","Normal fotoğraf sayısını doğru girin."); return
        if count<1 or not self.output_name_var.get().strip(): messagebox.showwarning("Eksik bilgi","Fotoğraf sayısı ve albüm adı boş olamaz."); return
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
        self.photos=photos; self.normal_count=count; self.cover_required=self.cover_var.get(); self.table_required=self.table_var.get(); self.output_dir=self.folder/self.output_name_var.get().strip(); self.selected.clear(); self.normal_selection.clear(); self.cover=None; self.table=None; self.mode="normal"; self._selection_page()
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
