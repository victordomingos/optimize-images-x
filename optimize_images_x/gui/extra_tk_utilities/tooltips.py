# encoding: utf-8
"""A small, dependency-free tooltip helper for Tkinter/ttk widgets.

Tkinter has no native tooltips, so this shows a borderless Toplevel with a short
help text after the pointer rests over a widget for a moment.
"""
import tkinter as tk


class Tooltip:
    """Attach a hover tooltip with the given text to a widget."""

    def __init__(self, widget, text, delay=500, wraplength=320):
        self.widget = widget
        self.text = text
        self.delay = delay  # ms before the tip appears
        self.wraplength = wraplength
        self._after_id = None
        self._tip = None
        widget.bind("<Enter>", self._schedule, add="+")
        widget.bind("<Leave>", self._hide, add="+")
        widget.bind("<ButtonPress>", self._hide, add="+")

    def _schedule(self, _event=None):
        self._cancel()
        self._after_id = self.widget.after(self.delay, self._show)

    def _cancel(self):
        if self._after_id is not None:
            try:
                self.widget.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None

    def _show(self):
        if self._tip is not None or not self.text:
            return
        x = self.widget.winfo_rootx() + 12
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6
        self._tip = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify="left",
                         background="#ffffe0", foreground="#222222",
                         relief="solid", borderwidth=1,
                         wraplength=self.wraplength, padx=6, pady=4)
        label.pack()

    def _hide(self, _event=None):
        self._cancel()
        if self._tip is not None:
            try:
                self._tip.destroy()
            except Exception:
                pass
            self._tip = None


def add_tooltip(widget, text):
    """Convenience helper that returns the created Tooltip."""
    return Tooltip(widget, text)
