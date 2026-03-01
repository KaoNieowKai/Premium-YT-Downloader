import os
import platform
import subprocess
import threading
import re
import customtkinter as ctk
from tkinter import messagebox, filedialog
import yt_dlp
import sys

def resource_path(relative_path):
    """ ดึงที่อยู่ไฟล์ให้ถูกต้อง ไม่ว่าจะรันแบบ .py หรือ .exe """
    try:
        # กรณีรันเป็นไฟล์ .exe (PyInstaller จะเก็บ path ไว้ใน _MEIPASS)
        base_path = sys._MEIPASS
    except Exception:
        # กรณีรันเป็นไฟล์ .py ปกติ
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- ตั้งค่าธีมหลัก ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

final_save_path = ""
url_entries = [] # ตัวแปรเก็บรายการช่องกรอกลิงก์ทั้งหมด

# --- ฟังก์ชันการทำงาน ---
def choose_directory():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        path_var.set(folder_selected)

def open_folder(path):
    if not path or not os.path.exists(path):
        return
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])

def update_ui(percent_float, percent_text, status_text=None, status_color=None):
    progress_bar.set(percent_float)
    percent_label.configure(text=percent_text)
    if status_text and status_color:
        status_label.configure(text=status_text, text_color=status_color)

def progress_hook(d):
    if d['status'] == 'downloading':
        percent_str = d.get('_percent_str', '0.0%')
        clean_percent_str = re.sub(r'\x1b\[[0-9;]*m', '', percent_str).strip().replace('%', '')
        
        try:
            percent_float = float(clean_percent_str) / 100.0
            percent_text = f"{int(percent_float * 100)}%"
            app.after(0, update_ui, percent_float, percent_text)
        except ValueError:
            pass
            
    elif d['status'] == 'finished':
        app.after(0, update_ui, 1.0, "100%", "⏳ กำลังดำเนินการแปลงไฟล์/รวมไฟล์...", "#F1C40F")

def add_url_entry():
    # สร้างช่องกรอกลิงก์อันใหม่
    new_entry = ctk.CTkEntry(url_list_frame, placeholder_text=f"🔗 วางลิงก์ YouTube ช่องที่ {len(url_entries)+1}...", width=420, height=38, font=ctk.CTkFont(size=13), corner_radius=8)
    new_entry.pack(pady=5)
    url_entries.append(new_entry)
    
    # สั่งให้กล่อง scroll เลื่อนลงมาล่างสุดอัตโนมัติเวลาเพิ่มช่องใหม่
    app.after(10, lambda: url_list_frame._parent_canvas.yview_moveto(1.0))

def download_media():
    base_path = path_var.get().strip()
    
    # ไล่เก็บลิงก์จากทุกๆ ช่องที่มีการกรอกข้อมูล
    url_list = []
    for entry in url_entries:
        val = entry.get().strip()
        if val: # ถ้าช่องไม่ว่าง ค่อยเอามาใส่คิว
            url_list.append(val)
            
    if not url_list:
        messagebox.showwarning("แจ้งเตือน", "กรุณาวางลิงก์ YouTube อย่างน้อย 1 ช่องครับ")
        return
    if not base_path:
        messagebox.showwarning("แจ้งเตือน", "กรุณาเลือกโฟลเดอร์สำหรับบันทึกไฟล์ครับ")
        return
    
    choice = format_seg.get()
    
    open_folder_btn.pack_forget()
    update_ui(0.0, "0%", f"กำลังเตรียมดาวน์โหลดทั้งหมด {len(url_list)} คิว...", "#3498DB")
    download_btn.configure(state="disabled", text="⏳ กำลังดำเนินการ...")
    
    # รันเบื้องหลัง
    thread = threading.Thread(target=process_download, args=(url_list, choice, base_path))
    thread.start()

def process_download(url_list, choice, base_path):
    global final_save_path 
    
    try:
        sub_folder_name = "MP3" if choice == '🎵 เสียงเพลง (MP3)' else "MP4"
        final_save_path = os.path.join(base_path, sub_folder_name)
        
        if not os.path.exists(final_save_path):
            os.makedirs(final_save_path)
            
        out_template = os.path.join(final_save_path, '%(title)s.%(ext)s')
        
        ydl_opts = {
            'outtmpl': out_template,
            'progress_hooks': [progress_hook],
            'quiet': True,
            'noprogress': False,
            'ignoreerrors': True 
        }

        if choice == '🎵 เสียงเพลง (MP3)':
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        else:
            ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download(url_list)
        
        app.after(0, update_ui, 1.0, "100%", f"✅ เสร็จสมบูรณ์! โหลดทั้ง {len(url_list)} คิวเรียบร้อยแล้ว", "#2ECC71")
        app.after(0, lambda: open_folder_btn.pack(pady=(5, 0)))
        
    except Exception as e:
        app.after(0, update_ui, 0.0, "0%", "❌ เกิดข้อผิดพลาด!", "#E74C3C")
        messagebox.showerror("ข้อผิดพลาด", f"เกิดข้อผิดพลาด:\n{e}")
        
    finally:
        app.after(0, lambda: download_btn.configure(state="normal", text="🚀 เริ่มดาวน์โหลด"))
        # ลบข้อความออกจากทุกช่องเมื่อโหลดเสร็จ
        for entry in url_entries:
            app.after(0, entry.delete, 0, 'end')

# --- สร้างหน้าต่างโปรแกรม (UI Layout) ---
app = ctk.CTk()
app.title("Premium YT Downloader")
app.iconbitmap(resource_path("app_icon.ico"))
app.geometry("600x680") # ปรับความสูงเพิ่มให้พอดีกับช่องลิงก์
app.resizable(True, False)

header_frame = ctk.CTkFrame(app, fg_color="transparent")
header_frame.pack(pady=(20, 10))

title_label = ctk.CTkLabel(header_frame, text="✨ Premium YT Downloader", font=ctk.CTkFont(size=26, weight="bold"))
title_label.pack()
subtitle_label = ctk.CTkLabel(header_frame, text="Dev By NongChamp!", font=ctk.CTkFont(size=13), text_color="gray")
subtitle_label.pack()

main_frame = ctk.CTkFrame(app, corner_radius=15)
main_frame.pack(padx=30, pady=5, fill="both", expand=True)

# --- ส่วนกล่องจัดการลิงก์ ---
url_label = ctk.CTkLabel(main_frame, text="🔗 วางลิงก์ YouTube (แยกช่องละ 1 ลิงก์):", font=ctk.CTkFont(size=14, weight="bold"))
url_label.pack(pady=(15, 5))

# กล่องรองรับการ Scroll (เลื่อนขึ้นลงได้)
url_list_frame = ctk.CTkScrollableFrame(main_frame, width=450, height=140, fg_color="#2B2B2B", corner_radius=10)
url_list_frame.pack(pady=(0, 5))

# ปุ่มเพิ่มช่องลิงก์
add_btn = ctk.CTkButton(main_frame, text="➕ เพิ่มช่องลิงก์", command=add_url_entry, font=ctk.CTkFont(size=12, weight="bold"), height=30, width=120, fg_color="#34495E", hover_color="#2C3E50", corner_radius=8)
add_btn.pack(pady=(0, 15))

# สร้างช่องเริ่มต้นให้ 3 ช่อง
for _ in range(3):
    add_url_entry()
# -----------------------------

path_var = ctk.StringVar(value=os.getcwd()) 
path_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
path_frame.pack(pady=(0, 15))

path_entry = ctk.CTkEntry(path_frame, textvariable=path_var, width=320, height=35, font=ctk.CTkFont(size=12), text_color="gray", state="readonly", corner_radius=8)
path_entry.grid(row=0, column=0, padx=(0, 10))

browse_btn = ctk.CTkButton(path_frame, text="📂 เลือกโฟลเดอร์", command=choose_directory, width=120, height=35, fg_color="#4B4B4B", hover_color="#333333", corner_radius=8)
browse_btn.grid(row=0, column=1)

format_seg = ctk.CTkSegmentedButton(main_frame, values=["🎬 วิดีโอ (MP4)", "🎵 เสียงเพลง (MP3)"], width=450, height=40, font=ctk.CTkFont(size=14, weight="bold"))
format_seg.set("🎬 วิดีโอ (MP4)") 
format_seg.pack(pady=(5, 10))

status_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
status_frame.pack(fill="x", padx=40, pady=5)

status_label = ctk.CTkLabel(status_frame, text="พร้อมใช้งาน!", font=ctk.CTkFont(size=14), text_color="gray")
status_label.pack()

progress_frame = ctk.CTkFrame(status_frame, fg_color="transparent")
progress_frame.pack(fill="x", pady=5)

progress_bar = ctk.CTkProgressBar(progress_frame, width=380, height=10, corner_radius=5)
progress_bar.set(0)
progress_bar.pack(side="left", padx=(0, 10))

percent_label = ctk.CTkLabel(progress_frame, text="0%", font=ctk.CTkFont(size=12, weight="bold"))
percent_label.pack(side="left")

download_btn = ctk.CTkButton(app, text="🚀 เริ่มดาวน์โหลด", command=download_media, font=ctk.CTkFont(size=16, weight="bold"), height=50, width=250, fg_color="#E62117", hover_color="#B3120A", corner_radius=25)
download_btn.pack(pady=(10, 5))

open_folder_btn = ctk.CTkButton(app, text="📁 เปิดโฟลเดอร์ไฟล์", command=lambda: open_folder(final_save_path), font=ctk.CTkFont(size=14), height=35, width=150, fg_color="#27AE60", hover_color="#219150", corner_radius=8)

app.mainloop()