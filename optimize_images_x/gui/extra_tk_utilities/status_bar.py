import tkinter as tk
import tkinter.font

from tkinter import ttk


class StatusBar(ttk.Frame):
    """ Simple Status Bar class with an embeded progress bar.
    """

    def __init__(self, master):
        ttk.Frame.__init__(self, master)
        self.progress_value = 0
        self.right_frame = ttk.Frame(self)

        self.lblStatusColor = "grey22"
        self.statusFont = tkinter.font.Font(family="Lucida Grande", size=11)
        self.label = ttk.Label(
            self, anchor=tk.W, font=self.statusFont, foreground=self.lblStatusColor)

        self.progress_bar = ttk.Progressbar(self.right_frame,
                                            length=125,
                                            mode='indeterminate')

        self.label.pack(padx=4, pady=4)
        self.right_frame.place(in_=self, relx=1, rely=1, y=-10, anchor='e')
        self.pack(side=tk.BOTTOM, fill=tk.X)

    def set(self, texto):
        """ Set the text display in the status bar. """
        self.label.config(text=texto)
        self.label.update()

    def clear(self):
        """ Remove all text from the status bar. """
        self.label.config(text="")
        self.label.update_idletasks()

    def show_progress(self, max_value=100, value=0, length=125, mode='indeterminate'):
        """ Display a progress bar in the right side of the status bar. It
            can accept a different maximum value, if needed. Mode must be
            either "determinate" (it will display a real progress bar that
            can be updated), or "indeterminate" (it will display a simple
            progress bar that does not show a specific value.
        """
        self.progress_reset()
        self.progress_bar['mode'] = mode
        if length:
            self.progress_bar['length'] = length
        if mode == 'indeterminate':
            self.progress_bar.start()
        else:
            self.progress_bar['maximum'] = max_value
            self.progress_update(value)

        self.progress_bar.pack(side='right', padx="0 14")
        self.progress_bar.update()
        self.right_frame.place(in_=self, relx=1, rely=1, y=-9, anchor='e')
        self.master.update()

    def _hide_progress(self):
        """ Do the actual hiding of the progress bar. """
        self.progress_bar.stop()
        self.right_frame.place_forget()
        self.progress_reset()

    def hide_progress(self, last_update=None):
        """ Reset the progress bar and hide it. Optionaly, it can show
            momentaneously a final value, by providing a value to the
            last_update argument.
        """
        if last_update:
            self.progress_update(last_update)
            self.after(300, self._hide_progress)
        else:
            self._hide_progress()

    def progress_update(self, value):
        """ Make the progress bar advance by indicating its new value. """
        if value > self.progress_value:
            self.progress_value = value
            self.progress_bar['value'] = self.progress_value
            self.progress_bar.update()
            self.progress_bar.after(150, lambda: self.progress_update(self.progress_value + 1))

    def progress_reset(self):
        """ Make the progress bar go back to zero. """
        self.progress_value = 0
        self.progress_bar['value'] = 0
        self.progress_bar.update()
