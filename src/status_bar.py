from tkinter import Frame, StringVar, SUNKEN, Label


class Status(Frame):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self.status = StringVar()
        self.status.set("Start")
        self.s_bar = Label(self.parent, textvariable=self.status, relief=SUNKEN,
                           anchor="center", background="green", foreground="yellow")
        self.s_bar.config(font=("bold, Calibri", 18))
        self.s_bar.pack(fill="both")
