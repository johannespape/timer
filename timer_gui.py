import os
import sys
import math
import time

import tkinter as tk
from threading import Thread

import vlc

class Timer(tk.Frame):
    def __init__(self, root, work_time=25, short_break_time=5, long_break_time=15, clock_speed=1000):
        tk.Frame.__init__(self)
        self.timer_time = 0
        self.clock_speed = clock_speed
        self.work_time = work_time * 60
        self.short_break_time = short_break_time * 60
        self.long_break_time = long_break_time * 60
        self.work_session = 1
        self.short_break = 0
        self.root = root

        # Logic
        self.timer_stopped = 1
        self.sessions_count = 1

        # GUI options
        self.width = 100
        self.height = 100
        self.padx = 3
        self.pady = 3

        # Clock display
        self.frame1 = tk.Frame(master=root, width=self.width, height=self.height)
        self.frame1.pack(fill=tk.BOTH, expand=True, padx=self.padx, pady=self.pady)
        self.lbl_time = tk.Label(master=self.frame1, text="00:00", bg="red")
        self.lbl_time.config(font=("Helvetica bold", 50), fg="white")
        self.lbl_time.pack(fill=tk.BOTH, expand=True)

        # Progress display
        self.frame2 = tk.Frame(master=root, width=self.width, height=self.height/10)
        self.frame2.pack(fill=tk.BOTH, expand=True, padx=self.padx, pady=self.pady)
        self.lbl_progress = tk.Label(master=self.frame2, text="0/4")
        self.lbl_progress.pack(fill=tk.BOTH, expand=True)

        # Buttons
        self.frame3 = tk.Frame(master=root, width=self.width, height=self.height/2)
        self.frame3.pack(fill=tk.BOTH, expand=True, padx=self.padx)
        self.btn_start_stop = tk.Button(master=self.frame3, text="Start/Stop", command=self.start_stop_timer)
        self.btn_start_stop.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.btn_skip = tk.Button(master=self.frame3, text="Skip session", command=self.skip_session)
        self.btn_skip.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.btn_reset = tk.Button(master=self.frame3, text="Reset timer", command=self.reset_timer)
        self.btn_reset.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.frame4 = tk.Frame(master=root, width=self.width, height=self.height/2)
        self.frame4.pack(fill=tk.BOTH, expand=True, padx=self.padx, pady=self.pady)
        self.btn_close = tk.Button(master=self.frame4, text="Close timer", command=self.close_timer)
        self.btn_close.pack(side=tk.LEFT,fill=tk.BOTH, expand=True)

    def draw_time(self):
        minutes = math.floor(self.timer_time/60)
        seconds = self.timer_time%60
        if seconds < 10 and minutes < 10:
            self.lbl_time["text"] = f"0{minutes}:0{seconds}"
        elif seconds >= 10 and minutes < 10:
            self.lbl_time["text"] = f"0{minutes}:{seconds}"
        elif seconds < 10 and minutes >= 10:
            self.lbl_time["text"] = f"{minutes}:0{seconds}"
        else:
            self.lbl_time["text"] = f"{minutes}:{seconds}"

    def draw_session_progress(self):
        if self.sessions_count % 4 == 0:
            self.lbl_progress["text"] = f"{4}/4"
        else:
            self.lbl_progress["text"] = f"{self.sessions_count % 4}/4"

    """
        Main function in program. Handles logic for displaying time.
        Utilizes draw_time and draw_session_progress to interface with frames.
    """
    def display_time(self):
        self.draw_session_progress()
        # Determine session
        if self.work_session:
            time_limit = self.work_time
        elif self.short_break:
            time_limit = self.short_break_time
        else:
            time_limit = self.long_break_time
        if self.timer_time <= time_limit + 1 and not self.timer_stopped:
            self.draw_time()
            self.timer_time += 1
            self.root.after(self.clock_speed, self.display_time)
        if self.timer_time == time_limit + 2:
            self.timer_stopped = 1
            self.timer_time = 0
            thread = Thread(target=self.timer_notification)
            thread.start()
            time.sleep(0.1)
            self.session_logic() # Update session logic
            self.draw_time()

    def start_stop_timer(self):
        if self.timer_stopped == 1:
            self.timer_stopped = 0
            self.display_time()
        else:
            self.timer_stopped = 1

    def session_logic(self):
        if not self.work_session:
            self.work_session = 1
            self.short_break = 0
            self.sessions_count += 1
            self.lbl_time.config(bg="red")
        elif not self.short_break:
            if self.sessions_count % 4 == 0:
                self.work_session = 0
                self.short_break = 0
                self.lbl_time.config(bg="green")
            else:
                self.work_session = 0
                self.short_break = 1
                self.lbl_time.config(bg="blue")

    def skip_session(self):
        self.timer_stopped = 1
        self.session_logic()
        self.timer_time = 0
        self.draw_time()

    def reset_timer(self):
        self.timer_time = 0
        self.timer_stopped = 1
        self.draw_time()

    def close_timer(self):
        self.root.quit()
        self.root.destroy()

    def timer_notification(self):
        # Format notification
        popup_root = tk.Tk()
        popup_root.title("Notification")
        if self.work_session:
            lbl_popup = tk.Label(popup_root, text = "Session done, take a break", font = ("Verdana", 20))
        else:
            lbl_popup = tk.Label(popup_root, text = "Break over, start session", font = ("Verdana", 20))
        lbl_popup.pack()
        popup_root.geometry('400x50+700+500')
        popup_root.after(4000, popup_root.destroy) # Kill after 2 seconds

        # Play bell
        thread = Thread(target=self.bell)
        thread.start()

        # Display Notification
        popup_root.mainloop()

    @staticmethod
    def bell():
        sound_player = vlc.MediaPlayer("file:///home/johannes/scripts/timer/microwave_notification_sound.mp3")
        sound_player.play()
        # duration = 0.25  # Seconds
        # freq = 440  # Hz
        # os.system('play -nq -t alsa synth {} sine {}'.format(duration, freq))
        # os.system('play -nq -t alsa synth {} sine {}'.format(duration, freq*5/4))
        # os.system('play -nq -t alsa synth {} sine {}'.format(duration, freq*3/2))
        # os.system('play -nq -t alsa synth {} sine {}'.format(duration*2, freq*15/8))

# Mainloop
if __name__ == "__main__":
    window = tk.Tk()
    window.title("Pomodoro Timer")

    if len(sys.argv) == 4:
        # User can provide custom timer specifications via command line input
        try:
            work_time = int(sys.argv[1])
            short_break_time = int(sys.argv[2])
            long_break_time = int(sys.argv[3])
            timer = Timer(window, work_time, short_break_time, long_break_time)
        except:
            print("Failed to initalize timer with given command line input.")
    else:
        # Default option is 25 min work, 5 min short break, 15 min long break
        timer = Timer(window)

    window.mainloop()
