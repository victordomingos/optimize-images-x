from tkinter import ttk


class LabelEntry(ttk.Frame):
    """ Generate a ttk.Entry form field with a text label above it. """

    def __init__(self, parent, label, default_text="", style=None, width=0):
        ttk.Frame.__init__(self, parent)
        self.calendar_open = False

        if style:
            self.label = ttk.Label(self, text=label, style=style, anchor="width")
        else:
            self.label = ttk.Label(self, text=label, anchor="width")

        self.entry = ttk.Entry(self, font=("Helvetica-Neue", 12), width=width)
        self.entry.insert(0, default_text)

        self.label.pack(side="top", fill="x", expand=True)
        self.entry.pack(side="top", fill="x", expand=True)

    def clear(self):
        self.entry.delete(0, 'end')

    def get(self):
        return self.entry.get()

    def set(self, text):
        self.clear()
        self.entry.insert(0, text)

    def set_label(self, text):
        self.label.config(text=text)

    def disable(self):
        self.entry.configure(state="disabled")

    def enable(self):
        self.entry.configure(state="enabled")
