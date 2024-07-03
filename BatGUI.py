import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2

class VideoPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Player")

        # Create a canvas to display the video
        self.canvas = tk.Canvas(root)
        self.canvas.pack()

        # Add menu bar
        self.menu_bar = tk.Menu(root)
        root.config(menu=self.menu_bar)

        # Add File menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Open Video", command=self.open_file)
        self.file_menu.add_command(label="Save As...", command=self.save_frame)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.exit_application)

        # Add buttons to control playback
        self.control_frame = tk.Frame(root)
        self.control_frame.pack()

        self.play_button = tk.Button(self.control_frame, text="▶️", command=self.play_video, font=("Arial", 20))
        self.play_button.pack(side=tk.LEFT)

        self.pause_button = tk.Button(self.control_frame, text="⏸️", command=self.pause_video, font=("Arial", 20))
        self.pause_button.pack(side=tk.LEFT)

        self.stop_button = tk.Button(self.control_frame, text="⏹️", command=self.stop_video, font=("Arial", 20))
        self.stop_button.pack(side=tk.LEFT)

        self.forward_button = tk.Button(self.control_frame, text="⏩ 10s", command=self.forward_video, font=("Arial", 20))
        self.forward_button.pack(side=tk.LEFT)

        self.backward_button = tk.Button(self.control_frame, text="⏪ 10s", command=self.backward_video, font=("Arial", 20))
        self.backward_button.pack(side=tk.LEFT)

        # Initialize video capture and frame variables
        self.cap = None
        self.frame = None
        self.video_source = None
        self.is_playing = False
        self.fps = 0
        self.total_frames = 0

    def open_file(self):
        self.video_source = filedialog.askopenfilename(
            filetypes=[("Video Files", "*.mp4;*.avi;*.mkv")]
        )
        if self.video_source:
            self.cap = cv2.VideoCapture(self.video_source)
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)
            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.is_playing = True

            # Get video dimensions and resize the window
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.canvas.config(width=width, height=height)
            self.root.geometry(f"{width}x{height+100}")  # +100 for control frame
            self.play_video()

    def play_video(self):
        if self.cap:
            if self.cap.get(cv2.CAP_PROP_POS_FRAMES) == self.total_frames:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.is_playing = True
            self.update_frame()

    def update_frame(self):
        if self.cap.isOpened() and self.is_playing:
            ret, self.frame = self.cap.read()
            if ret:
                # Convert the frame to RGB
                frame_rgb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                # Convert the frame to a PIL image
                frame_image = Image.fromarray(frame_rgb)
                # Convert the PIL image to a Tkinter image
                frame_tk = ImageTk.PhotoImage(image=frame_image)

                # Update the canvas with the new frame
                self.canvas.create_image(0, 0, anchor=tk.NW, image=frame_tk)
                self.canvas.image = frame_tk

                # Call update_frame again after 30 milliseconds
                self.root.after(30, self.update_frame)
            else:
                self.cap.release()

    def pause_video(self):
        self.is_playing = False

    def stop_video(self):
        if self.cap:
            self.is_playing = False
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.cap.release()
            self.cap = cv2.VideoCapture(self.video_source)
            self.canvas.delete("all")

    def forward_video(self):
        if self.cap and self.fps:
            current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
            new_frame = min(current_frame + int(10 * self.fps), self.total_frames - 1)
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame)

    def backward_video(self):
        if self.cap and self.fps:
            current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
            new_frame = max(current_frame - int(10 * self.fps), 0)
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame)

    def save_frame(self):
        if self.frame is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".jpg",
                                                     filetypes=[("JPEG files", "*.jpg"), ("All files", "*.*")])
            if file_path:
                frame_bgr = cv2.cvtColor(self.frame, cv2.COLOR_RGB2BGR)
                cv2.imwrite(file_path, frame_bgr)

    def exit_application(self):
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    player = VideoPlayer(root)
    root.mainloop()
