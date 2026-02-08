import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
import subprocess
import platform
from PIL import Image

# === 1. استيراد نظام التتبع الخاص بـ MoviePy ===
try:
    from proglog import ProgressBarLogger
except ImportError:
    # في حالة نادرة لم تكن مثبتة
    import pip
    pip.main(['install', 'proglog'])
    from proglog import ProgressBarLogger

# محاولة استيراد moviepy
try:
    from moviepy.editor import VideoFileClip
except ImportError:
    try:
        from moviepy import VideoFileClip
    except:
        from moviepy.editor import VideoFileClip

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# === 2. كلاس مخصص لربط التقدم بالشريط ===
class MyBarLogger(ProgressBarLogger):
    def __init__(self, progress_bar_widget, status_label_widget):
        super().__init__(init_state=None)
        self.progress_bar_widget = progress_bar_widget
        self.status_label_widget = status_label_widget

    def bars_callback(self, bar, attr, value, old_value=None):
        # هذه الدالة يتم استدعاؤها تلقائياً من MoviePy عند كل تحديث
        # bar == 't' يعني شريط الوقت (المعالجة الرئيسية)
        if bar == 't':
            total = self.bars[bar]['total']
            if total > 0:
                percentage = value / total
                # تحديث قيمة الشريط (يقبل قيم من 0.0 إلى 1.0)
                self.progress_bar_widget.set(percentage)
                
                # تحديث النص (اختياري)
                pct_text = int(percentage * 100)
                self.status_label_widget.configure(text=f"جاري المعالجة... {pct_text}%")

class VideoCutterApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(" Video Cutter Pro - SQ")
        self.geometry("700x750") 
        self.resizable(False, False)

        self.font_title = ("Segoe UI", 26, "bold")
        self.font_label = ("Segoe UI", 14)
        self.font_button = ("Segoe UI", 15, "bold")
        self.font_small = ("Segoe UI", 12)

        self.video_path = ""
        self.video_clip = None
        self.duration = 0
        self.saved_file_path = ""

        # --- عناصر الواجهة ---

        self.label_title = ctk.CTkLabel(self, text="برنامج قص وتعديل الفيديو", font=self.font_title)
        self.label_title.pack(pady=(20, 10))

        # منطقة المعاينة
        self.preview_frame = ctk.CTkFrame(self, width=320, height=180, fg_color="black")
        self.preview_frame.pack(pady=10)
        self.preview_frame.pack_propagate(False)

        self.label_preview = ctk.CTkLabel(self.preview_frame, text="معاينة الفيديو", text_color="gray")
        self.label_preview.pack(expand=True, fill="both")

        self.btn_select = ctk.CTkButton(self, text="📂 اختيار ملف الفيديو", 
                                      command=self.select_video, 
                                      font=self.font_button, width=220, height=40)
        self.btn_select.pack(pady=10)

        self.label_path = ctk.CTkLabel(self, text="لم يتم اختيار ملف", text_color="gray", font=self.font_small)
        self.label_path.pack(pady=5)

        # التحكم في الوقت
        self.frame_timeline = ctk.CTkFrame(self)
        self.frame_timeline.pack(pady=5, padx=20, fill="x")

        self.label_start = ctk.CTkLabel(self.frame_timeline, text="بداية: 00:00", font=self.font_label)
        self.label_start.pack(pady=2)
        self.slider_start = ctk.CTkSlider(self.frame_timeline, from_=0, to=100, command=self.update_start_time)
        self.slider_start.set(0)
        self.slider_start.pack(fill="x", padx=25, pady=5)

        self.label_end = ctk.CTkLabel(self.frame_timeline, text="نهاية: 00:00", font=self.font_label)
        self.label_end.pack(pady=2)
        self.slider_end = ctk.CTkSlider(self.frame_timeline, from_=0, to=100, command=self.update_end_time)
        self.slider_end.set(100)
        self.slider_end.pack(fill="x", padx=25, pady=5)

        # الخيارات
        self.frame_options = ctk.CTkFrame(self)
        self.frame_options.pack(pady=10, padx=20, fill="x")
        
        self.check_mute = ctk.CTkCheckBox(self.frame_options, text="كتم الصوت", font=self.font_small)
        self.check_mute.pack(side="left", padx=20, pady=10)

        self.check_audio_only = ctk.CTkSwitch(self.frame_options, text="حفظ كصوت (MP3)", font=self.font_small)
        self.check_audio_only.pack(side="right", padx=20, pady=10)

        self.label_speed = ctk.CTkLabel(self.frame_options, text="السرعة:", font=self.font_small)
        self.label_speed.pack(side="left", padx=(10, 5))
        self.option_speed = ctk.CTkOptionMenu(self.frame_options, values=["1.0x", "1.5x", "2.0x"], width=80)
        self.option_speed.set("1.0x")
        self.option_speed.pack(side="left", padx=5)

        # أزرار الحفظ
        self.btn_save = ctk.CTkButton(self, text="💾 حفظ وتصدير", 
                                    command=self.start_saving_thread, 
                                    state="disabled", 
                                    fg_color="#555555", hover_color="#24A36B",
                                    font=self.font_button, width=220, height=45)
        self.btn_save.pack(pady=10)

        self.btn_open_folder = ctk.CTkButton(self, text="📂 فتح المجلد", 
                                           command=self.open_output_folder,
                                           state="disabled", fg_color="#555555", font=self.font_button, width=220, height=45)
        self.btn_open_folder.pack(pady=5)

        # حالة والشريط
        self.label_status = ctk.CTkLabel(self, text="البرنامج جاهز", text_color="#DCE4EE", font=self.font_small)
        self.label_status.pack(pady=5)
        
        # شريط التقدم
        self.progressbar = ctk.CTkProgressBar(self, width=450)
        self.progressbar.set(0) # نبدأ من الصفر
        self.progressbar.pack(pady=10)

    def update_preview_image(self, seconds):
        if self.video_clip:
            try:
                frame = self.video_clip.get_frame(seconds)
                image = Image.fromarray(frame)
                image.thumbnail((320, 180)) 
                ctk_image = ctk.CTkImage(light_image=image, dark_image=image, size=image.size)
                self.label_preview.configure(image=ctk_image, text="") 
            except Exception as e:
                print(f"Error previewing frame: {e}")

    def select_video(self):
        file_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.avi *.mkv *.mov *.wmv")])
        if file_path:
            self.video_path = file_path
            self.label_path.configure(text=os.path.basename(file_path))
            self.btn_open_folder.configure(state="disabled")
            
            try:
                self.video_clip = VideoFileClip(file_path)
                self.duration = self.video_clip.duration
                
                self.slider_start.configure(to=self.duration)
                self.slider_end.configure(to=self.duration)
                self.slider_end.set(self.duration)
                
                self.update_start_time(0)
                self.update_end_time(self.duration)
                
                self.btn_save.configure(state="normal")
                self.label_status.configure(text=f"تم التحميل: {self.format_time(self.duration)}")
                self.progressbar.set(0) # تصفير الشريط عند تحميل فيديو جديد
            except Exception as e:
                messagebox.showerror("خطأ", f"فشل تحميل الفيديو: {e}")

    def format_time(self, seconds):
        mins, secs = divmod(int(seconds), 60)
        hours, mins = divmod(mins, 60)
        if hours > 0:
            return f"{hours:02d}:{mins:02d}:{secs:02d}"
        return f"{mins:02d}:{secs:02d}"

    def update_start_time(self, value):
        self.label_start.configure(text=f"بداية: {self.format_time(value)}")
        self.update_preview_image(value) 
        if value >= self.slider_end.get():
            self.slider_end.set(value + 1)
            self.label_end.configure(text=f"نهاية: {self.format_time(value + 1)}")

    def update_end_time(self, value):
        self.label_end.configure(text=f"نهاية: {self.format_time(value)}")
        self.update_preview_image(value)
        if value <= self.slider_start.get():
            self.slider_start.set(value - 1)
            self.label_start.configure(text=f"بداية: {self.format_time(value - 1)}")

    def start_saving_thread(self):
        save_thread = threading.Thread(target=self.save_video)
        save_thread.start()

    def save_video(self):
        start_time = self.slider_start.get()
        end_time = self.slider_end.get()

        if start_time >= end_time:
            messagebox.showwarning("تنبيه", "وقت البداية يجب أن يكون قبل وقت النهاية")
            return

        is_audio_only = self.check_audio_only.get()
        file_ext = ".mp3" if is_audio_only else ".mp4"
        file_type = "Audio File" if is_audio_only else "Video File"
        
        save_path = filedialog.asksaveasfilename(defaultextension=file_ext, 
                                                 filetypes=[(file_type, f"*{file_ext}")])
        
        if save_path:
            self.saved_file_path = save_path
            self.disable_controls(True)
            self.progressbar.set(0) # تصفير الشريط
            self.label_status.configure(text="جاري التجهيز...")
            
            # === إنشاء كائن الـ Logger المخصص ===
            # نمرر له الشريط والليبل ليقوم بتحديثهم
            logger = MyBarLogger(self.progressbar, self.label_status)

            try:
                if hasattr(self.video_clip, 'subclipped'):
                     new_clip = self.video_clip.subclipped(start_time, end_time)
                else:
                     new_clip = self.video_clip.subclip(start_time, end_time)
                
                if not is_audio_only:
                    speed_str = self.option_speed.get().replace("x", "")
                    speed_factor = float(speed_str)
                    
                    if speed_factor != 1.0:
                        new_clip = new_clip.speedx(speed_factor)

                    if self.check_mute.get():
                        new_clip = new_clip.without_audio()

                    # نمرر الـ logger هنا
                    new_clip.write_videofile(save_path, codec="libx264", audio_codec="aac", 
                                           preset="medium", logger=logger)
                else:
                    if new_clip.audio:
                        # نمرر الـ logger هنا أيضاً
                        new_clip.audio.write_audiofile(save_path, logger=logger)
                    else:
                        raise Exception("الفيديو الأصلي لا يحتوي على صوت!")

                self.label_status.configure(text="تم الحفظ بنجاح! (100%)")
                self.progressbar.set(1) # التأكد أنه ممتلئ في النهاية
                messagebox.showinfo("نجاح", "تمت العملية بنجاح!")
                self.btn_open_folder.configure(state="normal")

            except Exception as e:
                self.label_status.configure(text="حدث خطأ")
                messagebox.showerror("خطأ", f"حدث خطأ: {e}")
            finally:
                self.disable_controls(False)

    def disable_controls(self, disable):
        state = "disabled" if disable else "normal"
        self.btn_save.configure(state=state)
        self.btn_select.configure(state=state)
        self.slider_start.configure(state=state)
        self.slider_end.configure(state=state)

    def open_output_folder(self):
        if self.saved_file_path:
            folder_path = os.path.dirname(self.saved_file_path)
            try:
                if platform.system() == "Windows":
                    os.startfile(folder_path)
                elif platform.system() == "Darwin":
                    subprocess.Popen(["open", folder_path])
                else:
                    subprocess.Popen(["xdg-open", folder_path])
            except Exception as e:
                messagebox.showerror("خطأ", f"لا يمكن فتح المجلد: {e}")

if __name__ == "__main__":
    app = VideoCutterApp()
    app.mainloop()