import yt_dlp

def download_youtube(url, download_type='video'):
    print("\nกำลังประมวลผล กรุณารอสักครู่...")
    
    # ตั้งค่าตัวเลือกการดาวน์โหลด
    if download_type == 'audio':
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192', # คุณภาพเสียง 192kbps
            }],
            'outtmpl': '%(title)s.%(ext)s', # ตั้งชื่อไฟล์ตามชื่อคลิป
        }
    else:
        ydl_opts = {
            # เลือกวิดีโอและเสียงที่ดีที่สุด รวมเป็นไฟล์ mp4
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': '%(title)s.%(ext)s',
        }

    # เริ่มกระบวนการดาวน์โหลด
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("\n✅ ดาวน์โหลดเสร็จสมบูรณ์!")
    except Exception as e:
        print(f"\n❌ เกิดข้อผิดพลาด: {e}")
        if download_type == 'audio' and 'ffprobe' in str(e).lower():
            print("👉 คำแนะนำ: ดูเหมือนว่าคุณยังไม่ได้ติดตั้ง FFmpeg ในเครื่อง ซึ่งจำเป็นสำหรับการแปลงไฟล์เป็น MP3 ครับ")

if __name__ == "__main__":
    print("="*40)
    print("  ตัวช่วยดาวน์โหลด YouTube (Video / Audio)  ")
    print("="*40)
    
    target_url = input("🔗 วาง URL ของคลิป YouTube ที่นี่: ").strip()
    
    print("\nเลือกรูปแบบที่ต้องการ:")
    print("1. วิดีโอ (MP4)")
    print("2. เสียงเพลง (MP3)")
    choice = input("👉 กด 1 หรือ 2: ").strip()

    if choice == '2':
        download_youtube(target_url, 'audio')
    elif choice == '1':
        download_youtube(target_url, 'video')
    else:
        print("กรุณาเลือก 1 หรือ 2 เท่านั้นครับ")