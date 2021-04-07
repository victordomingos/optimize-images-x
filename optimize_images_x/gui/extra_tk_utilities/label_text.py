import tkinter as tk

from tkinter import ttk


class LabelText(ttk.Frame):
    """
    Generate an empty tkinter.scrolledtext form field with a text label above it.
    """

    def __init__(self, parent, label, style=None, width=0, height=0):
        ttk.Frame.__init__(self, parent)
        if style:
            self.label = ttk.Label(self, text=label, style=style, anchor="width")
        else:
            self.label = ttk.Label(self, text=label, anchor="width")

        self.scrolledtext = tk.Text(self, font=("Helvetica-Neue", 12),
                                    highlightcolor="LightSteelBlue2",
                                    wrap='word',
                                    width=width,
                                    height=height)

        self.label.pack(side="top", fill="x", expand=False)
        self.scrolledtext.pack(side="top", fill="both", expand=True)

    def get(self):
        return self.scrolledtext.get(1.0, tk.END)

    def set(self, text):
        self.clear()
        self.scrolledtext.insert('insert', text)

    def clear(self):
        self.scrolledtext.delete('1.0', 'end')

    def set_label(self, text):
        self.label.config(text=text)

    def enable(self):
        self.scrolledtext.configure(state="enabled", bg="white")

    def disable(self):
        self.scrolledtext.configure(state="disabled",
                                    bg="#fafafa",
                                    highlightbackground="#fafafa",
                                    highlightthickness=1)
