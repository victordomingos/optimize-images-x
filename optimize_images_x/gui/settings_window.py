import os
import sys
import tkinter as tk
import tkinter.font
from os import cpu_count
from tkinter import ttk, messagebox

# import Pmw
from tkinter.colorchooser import askcolor


class SettingsWindow(ttk.Frame):
    def __init__(self, master, app_status, app_settings, task_settings, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.app_status = app_status
        self.app_settings = app_settings
        self.task_settings = task_settings
        self.gui_style = ttk.Style()

        self.master.bind("<Command-w>", self._on_btn_close)
        self.master.focus()

        self.configure_frames_and_styles()
        self.generate_main_panel()
        self.show_main_panel()
        self.compose_frames()
        self.trace_var_changes()

    def configure_frames_and_styles(self):
        self.master.minsize(640, 360)
        # self.master.maxsize(W_DETALHE_CONTACTO_MAX_WIDTH, W_DETALHE_CONTACTO_MAX_HEIGHT)

        self.master.title("Preferences")

        # self.dicas = Pmw.Balloon(self.master, label_background='#f6f6f6',
        #                          hull_highlightbackground='#b3b3b3',
        #                          state='balloon',
        #                          relmouse='both',
        #                          yoffset=18,
        #                          xoffset=-2,
        #                          initwait=1300)

        self.mainframe = ttk.Frame(self.master)
        self.topframe = ttk.Frame(self.mainframe, padding="5 8 5 5")
        self.centerframe = ttk.Frame(self.mainframe)

        self.gui_style.configure("Panel_Title.TLabel", pady=10,
                                 foreground="grey25",
                                 font=("Helvetica Neue", 16, "bold"))

        self.gui_style.configure("Panel_Body.TLabel", font=("Lucida Grande", 11))
        self.gui_style.configure("TMenubutton", font=("Lucida Grande", 11))
        self.gui_style.configure('Settings.TLabelframe.Label',
                                 font=('Lucida Grande', 13, 'bold'))

        self.btnFont = tk.font.Font(family="Lucida Grande", size=10)
        self.btnTxtColor = "grey22"

    def generate_main_panel(self):
        self.note = ttk.Notebook(self.centerframe, padding="3 20 3 3")
        self.note.bind_all("<<NotebookTabChanged>>", self._on_tab_changed)

        self.tab_general = ttk.Frame(self.note, padding=10)
        self.tab_jpeg = ttk.Frame(self.note, padding=10)
        self.tab_png = ttk.Frame(self.note, padding=10)
        self.tab_more = ttk.Frame(self.note, padding=10)

        self.note.add(self.tab_general, text="General")
        self.note.add(self.tab_jpeg, text="JPEG")
        self.note.add(self.tab_png, text="PNG")
        self.note.add(self.tab_more, text="More…")

        self.generate_tab_general()
        self.generate_tab_jpeg()
        self.generate_tab_png()
        self.generate_tab_more()

        self.mount_tab_general()
        self.mount_tab_jpeg()
        self.mount_tab_png()
        self.mount_tab_more()

    def show_main_panel(self):
        self.note.pack(side='top', expand=True, fill='both')
        self.note.enable_traversal()

    def compose_frames(self):
        self.topframe.pack(side=tk.TOP, fill=tk.X)
        self.centerframe.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        self.mainframe.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

    def generate_tab_general(self):
        self.var_keep_original_size = tk.IntVar(
            value=self.task_settings.keep_original_size)
        self.var_max_w = tk.IntVar(value=self.task_settings.max_width)
        self.var_max_h = tk.IntVar(value=self.task_settings.max_height)
        self.var_recurse = tk.IntVar(value=self.task_settings.recurse_subfolders)
        self.var_fast_mode = tk.IntVar(value=self.task_settings.fast_mode)
        self.var_convert_gray = tk.IntVar(value=self.task_settings.convert_grayscale)
        self.var_no_comparison = tk.IntVar(value=self.task_settings.no_comparison)
        self.var_jobs = tk.IntVar(value=self.task_settings.n_jobs)
        self.var_auto_jobs = tk.IntVar(value=self.task_settings.auto_jobs)

        self.general_fr1 = ttk.Frame(self.tab_general)
        self.general_left = ttk.Labelframe(self.general_fr1,
                                           text='Image size reduction',
                                           style='Settings.TLabelframe')

        self.general_right = ttk.Labelframe(self.general_fr1,
                                            text='Global options',
                                            style='Settings.TLabelframe')

        self.radio_keep_orig_size = ttk.Radiobutton(self.general_left,
                                                    text="Keep original size",
                                                    value=1,
                                                    variable=self.var_keep_original_size)
        self.radio_downsize_img = ttk.Radiobutton(self.general_left,
                                                  text="Downsize image to fit:",
                                                  value=0,
                                                  variable=self.var_keep_original_size)

        self.lbl_max_w = ttk.Label(self.general_left, text="Max width:",
                                   style="Panel_Body.TLabel")

        self.spin_max_w = ttk.Spinbox(self.general_left,
                                      from_=0, to=1000000, increment=5,
                                      textvariable=self.var_max_w)

        self.lbl_max_h = ttk.Label(self.general_left,
                                   text="Max height:",
                                   style="Panel_Body.TLabel")

        self.label2 = ttk.Label(self.general_right,
                                text="label2",
                                style="Panel_Body.TLabel")

        self.spin_max_h = ttk.Spinbox(self.general_left,
                                      from_=0,
                                      to=1000000,
                                      increment=5,
                                      textvariable=self.var_max_h)

        self.chk_recurse = ttk.Checkbutton(
            self.general_right,
            text="Recurse through subfolders",
            variable=self.var_recurse)
        self.chk_fast_mode = ttk.Checkbutton(
            self.general_right,
            text="Fast mode",
            variable=self.var_fast_mode)
        self.chk_convert_gray = ttk.Checkbutton(
            self.general_right,
            text="Convert to grayscale",
            variable=self.var_convert_gray)
        self.chk_no_comparison = ttk.Checkbutton(
            self.general_right,
            text="No file size comparison",
            variable=self.var_no_comparison)

        self.lbl_jobs = ttk.Label(self.general_right,
                                  text="Simultaneous jobs:",
                                  style="Panel_Body.TLabel")
        self.spin_jobs = ttk.Spinbox(self.general_right,
                                     from_=1,
                                     to=256,
                                     textvariable=self.var_jobs)

        self.chk_auto_jobs = ttk.Checkbutton(
            self.general_right,
            text="Auto (based on CPU)",
            variable=self.var_auto_jobs)

    def mount_tab_general(self):
        self.radio_keep_orig_size.grid(column=0, row=0, columnspan=2,
                                       sticky='we')
        self.radio_downsize_img.grid(column=0, row=1, columnspan=2,
                                     sticky='we')
        self.lbl_max_w.grid(column=0, row=2, sticky='we')
        self.spin_max_w.grid(column=1, row=2, sticky='we')
        self.lbl_max_h.grid(column=0, row=3, sticky='we')
        self.spin_max_h.grid(column=1, row=3, sticky='we')

        self.chk_recurse.grid(column=0, row=0, sticky='we')
        self.chk_fast_mode.grid(column=0, row=1, sticky='we')
        self.chk_convert_gray.grid(column=0, row=2, sticky='we')
        self.chk_no_comparison.grid(column=0, row=3, sticky='we')

        self.lbl_jobs.grid(column=0, row=4, sticky='we', pady='12 0')
        self.spin_jobs.grid(column=0, row=5, sticky='we')
        self.chk_auto_jobs.grid(column=0, row=6, sticky='we')

        self.general_left.grid(column=0, row=0, sticky='wens',
                               padx='5', ipady=5, ipadx=5)
        self.general_right.grid(column=1, row=0, sticky='wens',
                                padx='5', ipady=5, ipadx=5)

        for col in range(0, 16):
            self.general_left.columnconfigure(col, weight=1)
            self.general_right.columnconfigure(col, weight=1)

        self.general_fr1.grid_columnconfigure(0, weight=1)
        self.general_fr1.grid_columnconfigure(1, weight=1)

        self.general_fr1.pack(side='top', expand=True, fill='both')

    def generate_tab_jpeg(self):
        self.var_dynamic = tk.IntVar(value=self.task_settings.jpg_dynamic_quality)
        self.var_jpeg_quality = tk.IntVar(value=self.task_settings.jpg_quality)
        self.var_keep_exif = tk.IntVar(value=self.task_settings.keep_exif)

        self.jpeg_fr1 = ttk.Frame(self.tab_jpeg)
        self.jpeg_left = ttk.Labelframe(self.jpeg_fr1,
                                        text='JPEG Quality',
                                        style='Settings.TLabelframe')

        self.jpeg_right = ttk.Labelframe(self.jpeg_fr1,
                                         text='Other options',
                                         style='Settings.TLabelframe')

        self.radio_dynamic = ttk.Radiobutton(self.jpeg_left,
                                             text="Auto/Dynamic",
                                             value=1,
                                             variable=self.var_dynamic)

        self.radio_fixed = ttk.Radiobutton(self.jpeg_left,
                                           text="Fixed value:",
                                           value=0,
                                           variable=self.var_dynamic)

        self.spin_jpeg_quality = ttk.Spinbox(self.jpeg_left,
                                             from_=0,
                                             to=100,
                                             increment=5,
                                             textvariable=self.var_jpeg_quality)

        self.chk_keep_exif = ttk.Checkbutton(self.jpeg_right,
                                             text="Keep EXIF",
                                             variable=self.var_keep_exif)

    def mount_tab_jpeg(self):
        self.radio_dynamic.grid(column=0, row=0, sticky='we')
        self.radio_fixed.grid(column=0, row=1, sticky='we')
        self.spin_jpeg_quality.grid(column=0, row=2, sticky='we')

        self.chk_keep_exif.grid(column=0, row=0, sticky='we')

        self.jpeg_left.grid(column=0, row=0, sticky='wens',
                            padx='5', ipady=5, ipadx=5)
        self.jpeg_right.grid(column=1, row=0, sticky='wens',
                             padx='5', ipady=5, ipadx=5)

        for col in range(0, 16):
            self.jpeg_left.columnconfigure(col, weight=1)
            self.jpeg_right.columnconfigure(col, weight=1)

        self.jpeg_fr1.grid_columnconfigure(0, weight=1)
        self.jpeg_fr1.grid_columnconfigure(1, weight=1)

        self.jpeg_fr1.pack(side='top', expand=True, fill='both')

    def generate_tab_png(self):
        if not self.task_settings.convert_big_to_jpg:
            conversion = 0
        elif self.task_settings.convert_all_to_jpg:
            conversion = 2
        else:
            conversion = 1

        self.var_conversion = tk.IntVar(value=conversion)
        self.var_del_original = tk.IntVar(value=self.task_settings.force_delete)
        self.var_reduce_colors = tk.IntVar(value=self.task_settings.reduce_colors)
        self.var_max_colors = tk.IntVar(value=self.task_settings.max_colors)
        self.var_remove_alpha = tk.IntVar(
            value=self.task_settings.remove_transparency)
        self.var_bg_color = ((self.task_settings.bg_color_red,
                              self.task_settings.bg_color_green,
                              self.task_settings.bg_color_blue),
                             self.task_settings.bg_color_hex)

        self.png_fr1 = ttk.Frame(self.tab_png)
        self.png_left = ttk.Labelframe(self.png_fr1,
                                       text='Convert to JPEG',
                                       style='Settings.TLabelframe')

        self.png_right = ttk.Labelframe(self.png_fr1,
                                        text='Other options',
                                        style='Settings.TLabelframe')

        self.radio_no_conversion = ttk.Radiobutton(self.png_left,
                                                   text="No format conversion",
                                                   value=0,
                                                   variable=self.var_conversion)

        self.radio_convert_big = ttk.Radiobutton(self.png_left,
                                                 text="Convert big images",
                                                 value=1,
                                                 variable=self.var_conversion)

        self.radio_convert_all = ttk.Radiobutton(self.png_left,
                                                 text="Convert all images",
                                                 value=2,
                                                 variable=self.var_conversion)

        self.chk_del_original = ttk.Checkbutton(self.png_left,
                                                text="Delete original PNG file",
                                                variable=self.var_del_original)

        self.radio_keep_colors = ttk.Radiobutton(self.png_right,
                                                 text="Auto (keep current colors)",
                                                 value=0,
                                                 variable=self.var_reduce_colors)

        self.radio_reduce_colors = ttk.Radiobutton(self.png_right,
                                                   text="Reduce palette to max colors:",
                                                   value=1,
                                                   variable=self.var_reduce_colors)

        self.spin_max_colors = ttk.Spinbox(self.png_right,
                                           from_=2,
                                           to=255,
                                           increment=2,
                                           textvariable=self.var_max_colors)

        self.chk_remove_alpha = ttk.Checkbutton(self.png_right,
                                                text="Remove transparency",
                                                variable=self.var_remove_alpha)

        self.btn_set_bg_color = ttk.Button(self.png_right,
                                           text='Set background color',
                                           command=self.choose_color)

        self.lbl_bg_color = tk.Label(self.png_right)
        self.lbl_bg_color['bg'] = self.var_bg_color[1]

    def mount_tab_png(self):
        self.radio_no_conversion.grid(column=0, row=0, sticky='we')
        self.radio_convert_big.grid(column=0, row=1, sticky='we')
        self.radio_convert_all.grid(column=0, row=2, sticky='we')
        self.chk_del_original.grid(column=0, row=3, sticky='we', pady=12)

        self.radio_keep_colors.grid(column=0, row=0, sticky='we')
        self.radio_reduce_colors.grid(column=0, row=1, sticky='we')
        self.spin_max_colors.grid(column=0, row=2, sticky='we')
        self.chk_remove_alpha.grid(column=0, row=3, sticky='we', pady=12)
        self.btn_set_bg_color.grid(column=0, row=4, sticky='we')
        self.lbl_bg_color.grid(column=0, row=5, sticky='we', padx=4)

        self.png_left.grid(column=0, row=0, sticky='wens',
                           padx='5', ipady=5, ipadx=5)
        self.png_right.grid(column=1, row=0, sticky='wens',
                            padx='5', ipady=5, ipadx=5)

        for col in range(0, 16):
            self.png_left.columnconfigure(col, weight=1)
            self.png_right.columnconfigure(col, weight=1)

        self.png_fr1.grid_columnconfigure(0, weight=1)
        self.png_fr1.grid_columnconfigure(1, weight=1)

        self.png_fr1.pack(side='top', expand=True, fill='both')

    def generate_tab_more(self):
        # self.var_del_original = tk.IntVar(value=self.task_settings.force_delete)
        # self.var_reduce_colors = tk.IntVar(value=self.task_settings.reduce_colors)
        # self.var_max_colors = tk.IntVar(value=self.task_settings.max_colors)
        #

        # left:
        # combo box theme (how to apply instantly?)
        # [] remember main window position and size

        # right:
        # [reset All settings]
        # [Reset usage statistics]
        self.radio_themes = []
        self.var_theme = tk.StringVar()
        self.var_theme.set(self.app_settings.app_style)

        self.more_fr1 = ttk.Frame(self.tab_more)
        self.more_left = ttk.Labelframe(self.more_fr1,
                                        text='User Interface',
                                        style='Settings.TLabelframe')

        self.more_right = ttk.Labelframe(self.more_fr1,
                                         text='Reset app defaults',
                                         style='Settings.TLabelframe')

        themes = self.gui_style.theme_names()
        for theme in themes:
            button = ttk.Radiobutton(self.more_left, text=theme, value=theme,
                                     variable=self.var_theme)
            self.radio_themes.append(button)

        self.btn_reset_all = ttk.Button(self.more_right, text='Reset all settings',
                                        command=self.reset_all_settings)

    def mount_tab_more(self):
        self.more_left.grid(column=0, row=0, sticky='wens',
                            padx='5', ipady=5, ipadx=5)
        self.more_right.grid(column=1, row=0, sticky='wens',
                             padx='5', ipady=5, ipadx=5)

        for col in range(0, 16):
            self.more_left.columnconfigure(col, weight=1)
            self.more_right.columnconfigure(col, weight=1)

        # self.combo_theme.pack()

        for radio in self.radio_themes:
            radio.grid(sticky='w')

        self.btn_reset_all.grid(sticky='w')

        self.more_fr1.grid_columnconfigure(0, weight=1)
        self.more_fr1.grid_columnconfigure(1, weight=1)

        self.more_fr1.pack(side='top', expand=True, fill='both')

    def choose_color(self):
        self.var_bg_color = askcolor(title='Select background color')
        self.lbl_bg_color['bg'] = self.var_bg_color[1]
        self._on_value_changed()

    def _on_tab_changed(self, event):
        w = event.widget  # get the current widget
        w.update_idletasks()

        tab = w.nametowidget(w.select())
        tab_name = self.note.tab(self.note.select(), "text")
        if tab_name == "PNG":
            w.update_idletasks()
            self.master.minsize(500, 300)
            self.master.state("normal")
            w.configure(height=tab.winfo_reqheight(),
                        width=tab.winfo_reqwidth())
        elif tab_name == "JPEG":
            w.update_idletasks()
            self.master.minsize(500, 300)
            self.master.state("normal")
            w.configure(height=tab.winfo_reqheight(),
                        width=tab.winfo_reqwidth())
        else:
            self.master.minsize(500, 300)
            w.update_idletasks()
            self.master.state("normal")
            w.configure(height=tab.winfo_reqheight(),
                        width=tab.winfo_reqwidth())

    def _on_btn_close(self, event):
        """ will test for some condition before closing, save if necessary and
                then call destroy()
        """
        self.app_status.is_settings_window_open = False
        window = event.widget.winfo_toplevel()
        window.destroy()

    def _on_value_changed(self, *event):
        self.task_settings.keep_original_size = self.var_keep_original_size.get()
        self.task_settings.max_width = self.var_max_w.get()
        self.task_settings.max_height = self.var_max_h.get()
        self.task_settings.recurse_subfolders = self.var_recurse.get()
        self.task_settings.fast_mode = self.var_fast_mode.get()
        self.task_settings.convert_grayscale = self.var_convert_gray.get()
        self.task_settings.no_comparison = self.var_no_comparison.get()
        self.task_settings.n_jobs = self.var_jobs.get()
        self.task_settings.auto_jobs = self.var_auto_jobs.get()

        if self.var_auto_jobs.get() == 1:
            self.var_jobs.set(cpu_count() + 1)

        self.task_settings.auto_jobs = self.var_auto_jobs.get()

        # JPEG Settings
        self.task_settings.jpg_dynamic_quality = self.var_dynamic.get()
        self.task_settings.jpg_quality = self.var_jpeg_quality.get()
        self.task_settings.keep_exif = self.var_keep_exif.get()

        # PNG settings
        self.task_settings.convert_big_to_jpg = self.var_conversion.get() != 0
        self.task_settings.convert_all_to_jpg = self.var_conversion.get() == 2
        self.task_settings.force_delete = self.var_del_original.get()
        self.task_settings.reduce_colors = self.var_reduce_colors.get()
        self.task_settings.max_colors = self.var_max_colors.get()
        self.task_settings.remove_transparency = self.var_remove_alpha.get()
        self.task_settings.bg_color_red = self.var_bg_color[0][0]
        self.task_settings.bg_color_red = self.var_bg_color[0][1]
        self.task_settings.bg_color_red = self.var_bg_color[0][2]
        self.task_settings.bg_color_hex = self.var_bg_color[1]
        self.task_settings.save()

        selected_theme = self.var_theme.get()
        if self.app_settings.app_style != selected_theme:
            self.gui_style.theme_use(selected_theme)
            self.app_settings.app_style = selected_theme
            self.app_settings.save()

    def reset_all_settings(self):
        msg = 'Resetting all settings will reload all default settings and the ' \
              'application will be restarted immediately.\n\n' \
              'Do you want to proceed?'
        proceed = messagebox.askyesno(title='Reset all settings and restart?',
                                      message=msg, parent=self)
        if proceed:
            self.app_settings.reset()
            self.task_settings.reset()
            self.restart_program()

    def trace_var_changes(self):
        gui_vars = (self.var_keep_original_size,
                    self.var_max_w,
                    self.var_max_h,
                    self.var_recurse,
                    self.var_fast_mode,
                    self.var_convert_gray,
                    self.var_no_comparison,
                    self.var_jobs,
                    self.var_auto_jobs,

                    self.var_dynamic,
                    self.var_jpeg_quality,
                    self.var_keep_exif,

                    self.var_conversion,
                    self.var_del_original,
                    self.var_reduce_colors,
                    self.var_max_colors,
                    self.var_remove_alpha,
                    self.var_theme)

        for gui_var in gui_vars:
            gui_var.trace('w', self._on_value_changed)

    @staticmethod
    def restart_program():
        """Restarts the current program.
        Note: this function does not return. Any cleanup action (like
        saving data) must be done before calling this function."""
        python = sys.executable
        os.execl(python, python, *sys.argv)
