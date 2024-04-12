import cv2
import mediapipe as mp
import math
import numpy as np
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import tkinter as tk
from PIL import Image, ImageTk


class HandVolumeControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hand Volume Control")
        self.root.geometry("1080x800")  

        
        self.cap = None
        self.volume_control_enabled = False

        
        self.title_label = tk.Label(root, text="Hand Volume Control", font=("Helvetica", 16))
        self.title_label.pack(pady=20)
        self.title_label = tk.Label(root, text=" designed by Nazafarin Tavossi and Sara Bayati", font=("Helvetica", 16))
        self.title_label.pack(pady=20)

       
        self.start_stop_button = tk.Button(root, text="Start", command=self.start_stop, font=("Helvetica", 14))
        self.start_stop_button.pack(pady=10)

        
        self.exit_button = tk.Button(root, text="Exit", command=self.exit_program, font=("Helvetica", 14))
        self.exit_button.pack(pady=10)

        
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = interface.QueryInterface(IAudioEndpointVolume)
        self.volume.SetMasterVolumeLevel(-65.25, None)

        
        self.mpHands = mp.solutions.hands
        self.Hands = self.mpHands.Hands()

    def start_stop(self):
        if not self.volume_control_enabled:
            self.cap = cv2.VideoCapture(0)
            self.volume_control_enabled = True
            self.start_stop_button.config(text="Stop")
            self.show_video_feed()
        else:
            self.cap.release()
            self.volume_control_enabled = False
            self.start_stop_button.config(text="Start")

    def show_video_feed(self):
        ret, frame = self.cap.read()
        if ret:
            imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.Hands.process(imgRGB)
            if (results.multi_hand_landmarks):
                for hand in results.multi_hand_landmarks:
                    mp.solutions.drawing_utils.draw_landmarks(frame, hand, self.mpHands.HAND_CONNECTIONS)
                    lmList = []
                    for id, lm in enumerate(hand.landmark):
                        h, w, c = frame.shape
                        cx, cy = int(lm.x * w), int(lm.y * h)
                        lmList.append([id, cx, cy])
                        if len(lmList) == 21:
                            x1, y1 = lmList[4][1], lmList[4][2]
                            x2, y2 = lmList[8][1], lmList[8][2]
                            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                            cv2.circle(frame, (x1, y1), 8, (255, 255, 0), cv2.FILLED)
                            cv2.circle(frame, (x2, y2), 8, (255, 255, 0), cv2.FILLED)
                            cv2.circle(frame, (cx, cy), 8, (255, 255, 0), cv2.FILLED)
                            cv2.line(frame, (x1, y1), (x2, y2), (255, 255, 0), 2)
                            lengthFingers = int(math.hypot(x2 - x1, y2 - y1))
                            handRange = [10, 170]
                            vol = int(np.interp(lengthFingers, handRange, [-65, 0]))
                            self.volume.SetMasterVolumeLevel(vol, None)
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_feed_label.imgtk = imgtk
            self.video_feed_label.configure(image=imgtk)
            self.video_feed_label.after(10, self.show_video_feed)

    def exit_program(self):
        if self.cap:
            self.cap.release()
        self.root.quit()


root = tk.Tk()


app = HandVolumeControlApp(root)


app.video_feed_label = tk.Label(root)
app.video_feed_label.pack()


root.mainloop()
