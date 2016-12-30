# gui 

from Tkinter import Label, Menu, PhotoImage, Tk
import tkFileDialog
import numpy
import cv2

class LapCounterGUI(Tk):
    def __init__(self, parent):
        Tk.__init__(self, parent)
        self.parent = parent
        self.initialise()

    def initialise(self):
        self.grid()

        self.title("Lap Counter")
        self.geometry("800x600")
        self.configure(background="#ffffff")

        self.menubar = Menu(self)
        self.filemenu = Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Open Video", command=self.open_video)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.quit)
        self.menubar.add_cascade(label="File", menu=self.filemenu)

        self.config(menu=self.menubar)

        self.title_image_src = PhotoImage(file="lapcounter.gif")

        self.title_image = Label(self, image=self.title_image_src, bd=0)
        self.title_image.grid()

    def open_video(self):
        self.video_filename = tkFileDialog.askopenfilename()
        play_video(self.video_filename)


def play_video(video_filename):
    cap = cv2.VideoCapture(video_filename)

    while (cap.isOpened()):
        ret, frame = cap.read()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        cv2.imshow('frame', gray)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    top = LapCounterGUI(None)
    top.mainloop()
