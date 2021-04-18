import tkinter as tk
import tkinter.font
from tkinter import ttk

from optimize_images_x import __version__
from optimize_images_x.calcs import human
from optimize_images_x.global_setup import APP_NAME
from optimize_images_x.global_setup import CREDITS, APP_LICENSE


class ThanksWindow:
    def __init__(self):
        self.about_w = 320
        self.about_h = 370

        self.thanksRoot = tk.Toplevel()
        self.thanksRoot.title("Special thanks")

        self.thanksRoot.focus()

        self.thanksRoot.update_idletasks()
        w = self.thanksRoot.winfo_screenwidth()
        h = self.thanksRoot.winfo_screenheight()
        self.size = tuple(
            int(_) for _ in self.thanksRoot.geometry().split('+')[0].split('x'))
        self.x = int(w / 2 - self.about_w / 2)
        self.y = int(h / 3 - self.about_h / 2)
        self.thanksRoot.configure(background='grey92')
        self.thanksRoot.geometry(
            "{}x{}+{}+{}".format(self.about_w, self.about_h, self.x, self.y))
        self.thanksframe = ttk.Frame(self.thanksRoot, padding="10 10 10 10")
        self.thanksframe_bottom = ttk.Frame(
            self.thanksRoot, padding="10 10 10 10")

        self.campo_texto = tk.Text(self.thanksframe, wrap='word', height=20)
        self.campo_texto.insert("end", "\n".join(CREDITS))
        self.campo_texto.tag_configure("center", justify='center')
        self.campo_texto.tag_add("center", 1.0, "end")
        self.campo_texto.pack(side='top')

        self.close_button = ttk.Button(
            self.thanksframe_bottom, text="Thanks!", command=self.thanksRoot.destroy)
        self.close_button.pack()
        self.thanksframe.pack(side=tk.TOP)
        self.thanksframe_bottom.pack(side=tk.BOTTOM)
        self.thanksRoot.bind("<Command-w>", self.close_window)

    @staticmethod
    def close_window(event):
        window = event.widget.winfo_toplevel()
        window.destroy()
        return "break"


class AboutWindow:
    def __init__(self, app_stats, *event):
        self.app_stats = app_stats
        self.about_w = 320
        self.about_h = 370

        self.popupRoot = tk.Toplevel()
        self.popupRoot.title("")

        self.popupRoot.focus()

        self.popupRoot.update_idletasks()
        w = self.popupRoot.winfo_screenwidth()
        h = self.popupRoot.winfo_screenheight()
        size = tuple(int(_)
                     for _ in self.popupRoot.geometry().split('+')[0].split('x'))
        x = int(w / 2 - self.about_w / 2)
        y = int(h / 3 - self.about_h / 2)
        self.popupRoot.configure(background='grey92')
        self.popupRoot.geometry(
            "{}x{}+{}+{}".format(self.about_w, self.about_h, x, y))

        self.pframe_top = ttk.Frame(self.popupRoot, padding="10 10 10 2")
        self.pframe_middle = ttk.Frame(self.popupRoot, padding="10 2 2 10")
        self.pframe_bottom = ttk.Frame(self.popupRoot, padding="10 2 10 10")

        # icon_path = APP_PATH + "/images/icon.gif"
        # self.icon = tk.PhotoImage(file=icon_path)
        # self.label = ttk.Label(self.pframe_top, image=self.icon)
        # self.label.pack(side='top')
        # self.label.bind('<Button-1>', thanks)

        self.appfont = tkinter.font.Font(size=15, weight='bold')
        self.copyfont = tkinter.font.Font(size=10)

        # ---------- TOPO -----------
        self.app_lbl = ttk.Label(
            self.pframe_top, font=self.appfont, text=APP_NAME)

        self.assin_lbl = ttk.Label(
            self.pframe_top,
            text="Saving space and making\nwebsites faster since 2018.\n\n")

        self.version_lbl = ttk.Label(self.pframe_top,
                                     font=self.copyfont,
                                     text=f"Version {__version__}\n\n")

        # ---------- MEIO -----------

        loaded_imgs = self.app_stats.images_loaded
        loaded_weight = self.app_stats.total_weight_loaded
        processed_imgs = self.app_stats.images_processed
        weight_saved = self.app_stats.total_weight_saved
        avg_weight_saved = 0
        avg_process_rate = 0.0

        if processed_imgs > 0:
            avg_weight_saved = weight_saved / processed_imgs
            avg_process_rate = processed_imgs / self.app_stats.processing_time

        self.lbl_imgs_loaded = ttk.Label(self.pframe_middle,
                                         text=f"Loaded images: {loaded_imgs}")

        self.lbl_imgs_loaded = ttk.Label(
            self.pframe_middle,
            text=f"Total loaded weight: {human(loaded_weight)}")

        self.lbl_processed_imgs = ttk.Label(
            self.pframe_top,
            text=f"Optimized images: {processed_imgs}")

        self.lbl_weight_saved = ttk.Label(
            self.pframe_middle,
            text=f"Total saved space: {human(weight_saved)}")

        self.lbl_avg_weight_saved = ttk.Label(
            self.pframe_middle,
            text=f"Avg. weight reduction: {human(avg_weight_saved)}/f")

        self.lbl_avg_process_rate = ttk.Label(
            self.pframe_middle,
            text=f"Avg. processing rate: {avg_process_rate:.1f} f/s")

        # ---------- FUNDO -----------
        self.copyright_lbl = ttk.Label(
            self.pframe_bottom, font=self.copyfont, text="\n\n© 2021 Victor Domingos")
        self.license_lbl = ttk.Label(
            self.pframe_bottom, font=self.copyfont, text=APP_LICENSE)

        self.app_lbl.pack(pady='20 8')
        self.version_lbl.pack()
        self.assin_lbl.pack()

        self.lbl_imgs_loaded.pack()
        self.lbl_imgs_loaded.pack()
        self.lbl_processed_imgs.pack()
        self.lbl_weight_saved.pack()
        self.lbl_avg_weight_saved.pack()
        self.lbl_avg_process_rate.pack()

        self.copyright_lbl.pack()
        self.license_lbl.pack()
        self.pframe_top.pack(side=tk.TOP)
        self.pframe_middle.pack(side=tk.TOP)
        self.pframe_bottom.pack(side=tk.TOP)

        self.pframe_top.focus()
        self.popupRoot.bind("<Command-w>", self.close_window)

    @staticmethod
    def close_window(event):
        window = event.widget.winfo_toplevel()
        window.destroy()
        return "break"


def thanks(*event):
    ThanksWindow()


def about(*event):
    AboutWindow()
