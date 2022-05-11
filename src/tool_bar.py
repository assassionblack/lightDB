"""
Module content Toolbar, NewMagazine, NewCategory and Analyze classes
"""
import logging
from tkinter import Frame, StringVar, Button, Label, Entry, Toplevel, Listbox, Spinbox, IntVar
from tkinter.colorchooser import askcolor
from tkinter.font import families
from tkinter.ttk import Combobox, Notebook

from src.navigation_bar import Navbar
from src.report import Report
from src.settings import configs
from src.table_panel import Table


class ToolBar(Frame):
    """
    class for creating toolbar in main window
    """
    def __init__(self, parent, db_handler, table_panel, navigation_panel, status):
        super().__init__()
        self.parent = parent
        self.navigation_panel = navigation_panel
        self.kod = StringVar()
        self.firm = StringVar()
        self.db_handler = db_handler
        self.table_panel = table_panel
        self.status = status

        self.option_add("*Button.font", "Calibri 10")
        self.option_add("*Label.font", "Calibri 10")
        self.option_add("*Entry.font", "Calibri 10")

        btn_print = Button(self.parent, text="Печать",
                           command=self.report)
        btn_create_new_mag = Button(self.parent, text="Новый магазин",
                                    command=self.new_magazine)
        btn_create_new_cat = Button(self.parent, text="Новая категория",
                                    command=self.new_category)
        btn_analyze_db = Button(self.parent, text="Проверка базы данных",
                                command=self.analyze)

        label_search_by_kod = Label(self.parent, text="Найти по коду:")
        entry_search_by_kod = Entry(self.parent, textvariable=self.kod)
        label_search_by_firm = Label(self.parent, text="Найти по фирме:")
        entry_search_by_firm = Entry(self.parent, textvariable=self.firm)

        btn_preferences = Button(self.parent, text="настройки", command=self.change_preferences)

        btn_print.grid(row=0, column=0)
        btn_create_new_mag.grid(row=0, column=1)
        btn_create_new_cat.grid(row=0, column=2)
        btn_analyze_db.grid(row=0, column=3)
        label_search_by_kod.grid(row=0, column=4)
        entry_search_by_kod.grid(row=0, column=5)
        label_search_by_firm.grid(row=0, column=6)
        entry_search_by_firm.grid(row=0, column=7)
        btn_preferences.grid(row=0, column=8)

        entry_search_by_kod.bind("<Return>", self.search_by_kod)
        entry_search_by_firm.bind("<Return>", self.search_by_firm)

    def report(self):
        """
        print report in document format to file
        """
        Report(self.status).print_report()
        status_var = "report printed"
        self.status.status.set(status_var)

    def new_magazine(self):
        """
        calls an additional window to create new magazine in db
        """
        NewMagazine(self, self.db_handler, self.navigation_panel, self.table_panel, self.status)

    def new_category(self):
        """
        calls an additional window to create new category for magazine in db
        """
        NewCategory(self, self.db_handler, self.navigation_panel, self.table_panel, self.status)

    def analyze(self):
        """
        calls analyze methods for db
        """
        Analyze(self, self.db_handler, self.navigation_panel, self.table_panel, self.status)

    def search_by_kod(self, event=None):
        """
        search in db by 'kod_tovara
        """
        Table(self.table_panel, self.db_handler, self.status, kod=self.kod.get())
        self.kod.set('')

    def search_by_firm(self, event=None):
        """
        search in db by 'firm'
        """
        Table(self.table_panel, self.db_handler, self.status, firm=self.firm.get())
        self.firm.set("")

    def change_preferences(self, event=None):
        Preferences()
        Table(self.table_panel, self.db_handler, self.status)
        Navbar(self.navigation_panel, self.table_panel, self.db_handler, self.status)


class NewMagazine(Toplevel):
    """
    class for additional window to create new magazine in table magazins in db
    """
    def __init__(self, parent, db_handler, navigation_panel, table_panel, status):
        super().__init__(parent)
        self.db_handler = db_handler
        self.navigation_panel = navigation_panel
        self.table_panel = table_panel
        self.status = status
        label = Label(self, text="Название нового магазина", takefocus=True, font=14)
        self.magazine = StringVar()
        entry_name_magazine = Entry(self, font=12, textvariable=self.magazine)
        btn_add = Button(self, text="Добавить")

        label.grid(row=0, column=0)
        entry_name_magazine.grid(row=1, column=0)
        btn_add.grid(row=2, column=0)

        btn_add.bind("<Button-1>", self.add_magazine)

    def add_magazine(self, event):
        """
        add magazine in db
        """
        status = self.db_handler.set_magazine(self.magazine.get())
        self.status.status.set(status)
        logging.info(status)
        Navbar(self.navigation_panel, self.table_panel, self.db_handler, self.status)
        self.destroy()


class NewCategory(Toplevel):
    """
    class for additional window to create new category in table categories in db
    """
    def __init__(self, parent, db_handler, navigation_panel, table_panel, status):
        super().__init__(parent)
        self.db_handler = db_handler
        self.navigation_panel = navigation_panel
        self.table_panel = table_panel
        self.status = status
        label_cat = Label(self, font=14, text="Название новой категории")
        label_mag = Label(self, font=14, text="Название магазина")
        self.category = StringVar()

        self.list_categories = []
        for category in self.db_handler.get_categories():
            self.list_categories.append(category.category)

        self.entry_category = Entry(self, textvariable=self.category)
        self.entry_category.grid(row=1, column=0)
        self.entry_category.bind('<KeyRelease>', self.scan_key)

        self.listbox = Listbox(self, selectmode='browse')
        self.listbox.grid(row=2, column=0)
        self.update_listbox(self.list_categories)

        self.magazine = StringVar()
        combo_magazine = Combobox(self, values=self.db_handler.get_magazines(),
                                  textvariable=self.magazine, state="readonly")
        combo_magazine.current(0)
        btn_add = Button(self, text="Добавить")

        label_cat.grid(row=0, column=0)
        label_mag.grid(row=0, column=1)
        combo_magazine.grid(row=1, column=1)
        btn_add.grid(row=2, column=1)

        btn_add.bind("<Button-1>", self.add_category)
        self.listbox.bind("<<ListboxSelect>>", self.selected_category)

    def scan_key(self, event):
        """
        method for reading inputted key
        """
        val = event.widget.get()

        if val == '':
            data = self.list_categories
        else:
            data = []
            for item in self.list_categories:
                if val.lower() in item.lower():
                    data.append(item)
        self.update_listbox(data)

    def update_listbox(self, data):
        """
        method for update listbox by inputted keys
        """
        self.listbox.delete(0, 'end')
        for item in data:
            self.listbox.insert('end', item)

    def selected_category(self, event):
        """
        put selected variant from listbox in entry
        """
        cur_select = self.listbox.get(self.listbox.curselection()[0])
        self.category.set('')
        self.entry_category.insert(0, cur_select)
        data = []
        for item in self.list_categories:
            if cur_select.lower() in item.lower():
                data.append(item)
        self.update_listbox(data)

    def add_category(self, event):
        """
        put inserted variant of name category to db
        """
        status = self.db_handler.set_category(self.magazine.get(), self.category.get())
        self.status.status.set(status)
        logging.info(status)
        Navbar(self.navigation_panel, self.table_panel, self.db_handler, self.status)
        self.destroy()


class Analyze(Toplevel):
    """
    create additional window for analyze methods
    """
    def __init__(self, parent, db_handler, navigation_panel, table_panel, status):
        super().__init__(parent)
        self.db_handler = db_handler
        self.navigation_panel = navigation_panel
        self.table_panel = table_panel
        self.status = status
        self.label = Label(self, font=14, text="Это может занять некоторое время...")
        btn_start = Button(self, text="Начать")
        btn_end = Button(self, text="Закрыть")
        btn_products = Button(self, text="Расширенный анализ")

        self.label.grid(row=0, columnspan=2)
        btn_start.grid(row=1, column=0)
        btn_end.grid(row=1, column=1)
        btn_products.grid(row=2, columnspan=2)

        btn_start.bind("<Button-1>", self.analyze)
        btn_end.bind("<Button-1>", self.stop)
        btn_products.bind("<Button-1>", self.analyze_products)

    def analyze(self, event):
        """
        calls inspect method rrom db_handler
        """
        status = self.db_handler.inspect()
        self.status.status.set(status)
        logging.info(status)
        Navbar(self.navigation_panel, self.table_panel, self.db_handler, self.status)
        Table(self.table_panel, self.db_handler, self.status)

    def stop(self, event):
        """
        close additional window
        """
        self.destroy()

    def analyze_products(self, event):
        """
        calls inspect_products method from db_handler
        """
        status = self.db_handler.inspect_products()
        self.status.status.set(status)
        logging.info(status)
        self.label.configure(text="проверка записей в таблице товаров завершена")
        Navbar(self.navigation_panel, self.table_panel, self.db_handler, self.status)
        Table(self.table_panel, self.db_handler, self.status)


class Preferences(Toplevel):
    """
    create additional window for change preferences for program
    """
    def __init__(self):
        super().__init__()

        tab_bar = Notebook(self)
        tab_sizes = Frame(tab_bar)
        tab_bar.add(tab_sizes, text="Размеры")
        tab_style_navbar = Frame(tab_bar)
        tab_bar.add(tab_style_navbar, text="Стиль навигации")
        tab_style_table = Frame(tab_bar)
        tab_bar.add(tab_style_table, text="Стиль таблицы")
        tab_style_report = Frame(tab_bar)
        tab_bar.add(tab_style_report, text="Стиль отчета")
        tab_ssh = Frame(tab_bar)
        tab_bar.add(tab_ssh, text="Настройки ssh")
        tab_bar.pack(expand=1, fill="both")

        all_fonts = sorted(families())
        font_styles = ("normal", "italic", "oblique")
        font_weights = ("normal", "bold")

        # tab_sizes
        label_width_navbar = Label(tab_sizes, text="Ширина раздела навигации")
        self.width_navbar = IntVar(value=configs.settings
                                   .get("sizes").get("width-navbar"))
        spin_width_navbar = Spinbox(tab_sizes, from_=100, to=1000,
                                    textvariable=self.width_navbar)
        label_width_navbar.grid(row=0, column=0)
        spin_width_navbar.grid(row=0, column=1)
        label_height_navbar = Label(tab_sizes, text="Высота раздела навигации")
        self.height_navbar = IntVar(value=configs.settings
                                    .get("sizes").get("height-navbar"))
        spin_height_navbar = Spinbox(tab_sizes, from_=10, to=100,
                                     textvariable=self.height_navbar)
        label_height_navbar.grid(row=1, column=0)
        spin_height_navbar.grid(row=1, column=1)
        label_width_table = Label(tab_sizes, text="Ширина таблицы")
        self.width_table = IntVar(value=configs.settings
                                  .get("sizes").get("width-table"))
        spin_width_table = Spinbox(tab_sizes, from_=500, to=2000,
                                   textvariable=self.width_table)
        label_width_table.grid(row=2, column=0)
        spin_width_table.grid(row=2, column=1)
        label_height_table = Label(tab_sizes, text="Высота таблицы")
        self.height_table = IntVar(value=configs.settings
                                   .get("sizes").get("height-table"))
        spin_height_table = Spinbox(tab_sizes, from_=100, to=1500,
                                    textvariable=self.height_table)
        label_height_table.grid(row=3, column=0)
        spin_height_table.grid(row=3, column=1)

        # tab_style_navbar
        label_navbar_all = Label(tab_style_navbar, text="общие".upper(),
                                 underline=0, relief="flat", font=14, bg="white")
        label_navbar_all.grid(row=0, columnspan=3)
        label_navbar_all_font = Label(tab_style_navbar, text="шрифт")
        self.navbar_all_font = StringVar(
            value=configs.settings.get("styles").get("navbar")[0].get("all-font"))
        menu_navbar_all_font = Combobox(tab_style_navbar, values=all_fonts,
                                        textvariable=self.navbar_all_font)
        label_navbar_all_font.grid(row=1, column=0)
        menu_navbar_all_font.grid(row=1, column=1)
        label_navbar_all_font_size = Label(tab_style_navbar, text="размер шрифта")
        self.navbar_all_font_size = StringVar(
            value=configs.settings.get("styles").get("navbar")[0].get("all-font-size"))
        spin_navbar_all_font_size = Spinbox(tab_style_navbar, from_=6, to=20,
                                            textvariable=self.navbar_all_font_size)
        label_navbar_all_font_size.grid(row=2, column=0)
        spin_navbar_all_font_size.grid(row=2, column=1)
        label_navbar_all_fg = Label(tab_style_navbar, text="цвет текста")
        self.navbar_all_fg = StringVar(
            value=configs.settings.get('styles').get("navbar")[0].get("tree-foreground"))
        entry_navbar_all_fg = Entry(tab_style_navbar, textvariable=self.navbar_all_fg)
        btn_change_navbar_all_fg = Button(tab_style_navbar, text="Изменить",
                                          command=self.change_navbar_all_fg)
        label_navbar_all_fg.grid(row=3, column=0)
        entry_navbar_all_fg.grid(row=3, column=1)
        btn_change_navbar_all_fg.grid(row=3, column=2)

        label_navbar_header = Label(tab_style_navbar, text="заголовки".upper(),
                                    underline=0, relief="flat", font=14, bg="white")
        label_navbar_header.grid(row=4, columnspan=3)
        label_navbar_header_font = Label(tab_style_navbar, text="шрифт")
        self.navbar_header_font = StringVar(
            value=configs.settings.get('styles').get("navbar")[0].get("heading-font"))
        menu_navbar_header_font = Combobox(
            tab_style_navbar, values=all_fonts, textvariable=self.navbar_header_font)
        label_navbar_header_font.grid(row=5, column=0)
        menu_navbar_header_font.grid(row=5, column=1)
        label_navbar_header_font_size = Label(tab_style_navbar, text="размер шрифта")
        self.navbar_header_font_size = StringVar(
            value=configs.settings.get('styles').get("navbar")[0].get("heading-font-size"))
        spin_navbar_header_font_size = Spinbox(
            tab_style_navbar, from_=6, to=30,
            textvariable=self.navbar_header_font_size)
        label_navbar_header_font_size.grid(row=6, column=0)
        spin_navbar_header_font_size.grid(row=6, column=1)
        label_navbar_header_font_style = Label(tab_style_navbar, text="стиль шрифта")
        self.navbar_header_font_style = StringVar(
            value=configs.settings.get('styles').get("navbar")[0].get("heading-font-style"))
        menu_navbar_header_font_style = Combobox(tab_style_navbar, values=font_weights,
                                                 textvariable=self.navbar_header_font_style)
        label_navbar_header_font_style.grid(row=7, column=0)
        menu_navbar_header_font_style.grid(row=7, column=1)
        label_navbar_header_fg = Label(tab_style_navbar, text="цвет текста")
        self.navbar_header_fg = StringVar(
            value=configs.settings.get('styles').get("navbar")[0].get("heading-foreground"))
        entry_navbar_header_fg = Entry(tab_style_navbar, textvariable=self.navbar_header_fg)
        btn_navbar_change_header_fg = Button(
            tab_style_navbar, text="Изменить", command=self.change_navbar_header_fg)
        label_navbar_header_fg.grid(row=8, column=0)
        entry_navbar_header_fg.grid(row=8, column=1)
        btn_navbar_change_header_fg.grid(row=8, column=2)

        # tab_style_table
        label_table_all = Label(tab_style_table, text="общие".upper(),
                                underline=0, relief="flat", font=14, bg="white")
        label_table_all.grid(row=0, columnspan=3)
        label_table_all_font = Label(tab_style_table, text="шрифт")
        self.table_all_font = StringVar(
            value=configs.settings.get("styles").get("table")[0].get("font"))
        menu_table_all_font = Combobox(
            tab_style_table, values=all_fonts, textvariable=self.table_all_font)
        label_table_all_font.grid(row=1, column=0)
        menu_table_all_font.grid(row=1, column=1)
        label_table_all_font_size = Label(tab_style_table, text="размер шрифта")
        self.table_all_font_size = StringVar(
            value=configs.settings.get("styles").get("table")[0].get("font-size"))
        spin_table_all_font_size = Spinbox(
            tab_style_table, from_=6, to=30, textvariable=self.table_all_font_size)
        label_table_all_font_size.grid(row=2, column=0)
        spin_table_all_font_size.grid(row=2, column=1)
        label_table_all_font_style = Label(tab_style_table, text="стиль текста")
        self.table_all_font_style = StringVar(
            value=configs.settings.get('styles').get("table")[0].get("font-style"))
        menu_table_all_font_style = Combobox(tab_style_table, values=font_styles,
                                             textvariable=self.table_all_font_style)
        label_table_all_font_style.grid(row=3, column=0)
        menu_table_all_font_style.grid(row=3, column=1)

        label_table_header = Label(tab_style_table, text="заголовки".upper(),
                                   underline=0, relief="flat", font=14, bg="white")
        label_table_header.grid(row=4, columnspan=3)
        label_table_header_font = Label(tab_style_table, text="шрифт")
        self.table_header_font = StringVar(
            value=configs.settings.get('styles').get("table")[0].get("header-font"))
        menu_table_header_font = Combobox(tab_style_table, values=all_fonts, textvariable=self.table_header_font)
        label_table_header_font.grid(row=5, column=0)
        menu_table_header_font.grid(row=5, column=1)
        label_table_header_font_size = Label(tab_style_table, text="размер шрифта")
        self.table_header_font_size = StringVar(
            value=configs.settings.get('styles').get("table")[0].get("header-font-size"))
        spin_table_header_font_size = Spinbox(
            tab_style_table, from_=6, to=40, textvariable=self.table_header_font_size)
        label_table_header_font_size.grid(row=6, column=0)
        spin_table_header_font_size.grid(row=6, column=1)
        label_table_header_font_style = Label(tab_style_table, text="стиль шрифта")
        self.table_header_font_style = StringVar(
            value=configs.settings.get('styles').get("table")[0].get("header-font-style"))
        menu_table_header_font_style = Combobox(tab_style_table, values=font_weights,
                                                textvariable=self.table_header_font_style)
        label_table_header_font_style.grid(row=7, column=0)
        menu_table_header_font_style.grid(row=7, column=1)
        label_table_header_bg = Label(tab_style_table, text="цвет фона")
        self.table_header_bg = StringVar(
            value=configs.settings.get('styles').get("table")[0].get("header-bg"))
        entry_table_header_bg = Entry(tab_style_table, textvariable=self.table_header_bg)
        btn_change_table_header_bg = Button(
            tab_style_table, text="Изменить", command=self.change_table_header_bg)
        label_table_header_bg.grid(row=8, column=0)
        entry_table_header_bg.grid(row=8, column=1)
        btn_change_table_header_bg.grid(row=8, column=2)

        # tab_style_report
        # [[report-style.magazine]]
        label_report_magazine = Label(tab_style_report, text="стиль заголовка магазин".upper(),
                                      underline=0, relief="flat", font=14, bg="white")
        label_report_magazine.grid(row=0, columnspan=3)
        label_report_magazine_color = Label(tab_style_report, text="цвет")
        self.report_magazine_color = StringVar(
            value=configs.settings.get('report-style').get("magazine")[0].get("color"))
        entry_report_magazine_color = Entry(tab_style_report, textvariable=self.report_magazine_color)
        btn_change_report_magazine_color = Button(
            tab_style_report, text="Изменить",
            command=self.change_report_magazine_color)
        label_report_magazine_color.grid(row=1, column=0)
        entry_report_magazine_color.grid(row=1, column=1)
        btn_change_report_magazine_color.grid(row=1, column=2)
        label_report_magazine_font_weight = Label(tab_style_report, text="стиль")
        self.report_magazine_font_weight = StringVar(
            value=configs.settings.get('report-style').get("magazine")[0].get("font-weight"))
        menu_report_magazine_font_weight = Combobox(tab_style_report, values=font_weights,
                                                    textvariable=self.report_magazine_font_weight)
        label_report_magazine_font_weight.grid(row=2, column=0)
        menu_report_magazine_font_weight.grid(row=2, column=1)
        label_report_magazine_font_size = Label(tab_style_report, text="размер шрифта")
        self.report_magazine_font_size = StringVar(
            value=configs.settings.get('report-style').get("magazine")[0].get("font-size"))
        spin_report_magazine_font_size = Spinbox(
            tab_style_report, from_=6, to=50,
            textvariable=self.report_magazine_font_size)
        label_report_magazine_font_size.grid(row=2, column=0)
        spin_report_magazine_font_size.grid(row=2, column=1)
        label_report_magazine_text_indent = Label(tab_style_report, text="отступ слева")
        self.report_magazine_text_indent = StringVar(
            value=configs.settings.get('report-style').get("magazine")[0].get("text-indent"))
        spin_report_magazine_text_indent = Spinbox(
            tab_style_report, from_=0, to=1000, textvariable=self.report_magazine_text_indent)
        label_report_px = Label(tab_style_report, text="px")
        label_report_magazine_text_indent.grid(row=3, column=0)
        spin_report_magazine_text_indent.grid(row=3, column=1)
        label_report_px.grid(row=3, column=2, sticky="w")
        # [[report - style.category]]
        label_report_category = Label(tab_style_report, text="стиль заголовка категория".upper(),
                                      underline=0, relief="flat", font=14, bg="white")
        label_report_category.grid(row=4, columnspan=3)
        label_report_category_color = Label(tab_style_report, text="цвет")
        self.report_category_color = StringVar(
            value=configs.settings.get('report-style').get("category")[0].get("color"))
        entry_report_category_color = Entry(tab_style_report,
                                            textvariable=self.report_category_color)
        btn_change_report_category_color = Button(
            tab_style_report, text="Изменить",
            command=self.change_report_category_color)
        label_report_category_color.grid(row=5, column=0)
        entry_report_category_color.grid(row=5, column=1)
        btn_change_report_category_color.grid(row=5, column=2)
        label_report_category_font_style = Label(tab_style_report, text="стиль")
        self.report_category_font_style = StringVar(
            value=configs.settings.get('report-style').get("category")[0].get("font-style"))
        menu_report_category_font_style = Combobox(tab_style_report, values=font_styles,
                                                   textvariable=self.report_category_font_style)
        label_report_category_font_style.grid(row=6, column=0)
        menu_report_category_font_style.grid(row=6, column=1)
        label_report_category_font_size = Label(tab_style_report, text="размер шрифта")
        self.report_category_font_size = StringVar(
            value=configs.settings.get('report-style').get("category")[0].get("font-size"))
        spin_report_category_font_size = Spinbox(
            tab_style_report, from_=6, to=50,
            textvariable=self.report_category_font_size)
        label_report_category_font_size.grid(row=7, column=0)
        spin_report_category_font_size.grid(row=7, column=1)
        label_report_category_text_indent = Label(tab_style_report, text="отступ слева")
        self.report_category_text_indent = StringVar(
            value=configs.settings.get('report-style').get("category")[0].get("text-indent"))
        spin_report_category_text_indent = Spinbox(tab_style_report, from_=0, to=1000,
                                                   textvariable=self.report_category_text_indent)
        label_report_px = Label(tab_style_report, text="px")
        label_report_category_text_indent.grid(row=8, column=0)
        spin_report_category_text_indent.grid(row=8, column=1)
        label_report_px.grid(row=8, column=2, sticky='w')
        # [[report - style.table]]
        label_report_table = Label(tab_style_report, text="стиль таблицы".upper(),
                                   underline=0, relief="flat", font=14, bg="white")
        label_report_table.grid(row=9, columnspan=3)
        label_report_table_border = Label(tab_style_report, text="рамки")
        self.report_table_border = StringVar(
            value=configs.settings.get('report-style').get("table")[0].get("border"))
        entry_report_table_border = Entry(
            tab_style_report, textvariable=self.report_table_border)
        btn_change_report_table_border = Button(
            tab_style_report, text="Изменить",
            command=self.change_report_table_border)
        label_report_table_border.grid(row=10, column=0)
        entry_report_table_border.grid(row=10, column=1)
        btn_change_report_table_border.grid(row=10, column=2)
        # [[report - style.td - th]]
        label_report_cell = Label(tab_style_report, text="стиль ячейки".upper(),
                                  underline=0, relief="flat", font=14, bg="white")
        label_report_cell.grid(row=11, columnspan=3)
        label_report_cell_border = Label(tab_style_report, text="рамки")
        self.report_cell_border = StringVar(
            value=configs.settings.get('report-style').get("td-th")[0].get("border"))
        entry_report_cell_border = Entry(
            tab_style_report, textvariable=self.report_cell_border)
        btn_change_report_cell_border = Button(
            tab_style_report, text="Изменить",
            command=self.change_report_cell_border)
        label_report_cell_border.grid(row=12, column=0)
        entry_report_cell_border.grid(row=12, column=1)
        btn_change_report_cell_border.grid(row=12, column=2)
        label_report_cell_font_size = Label(tab_style_report, text="размер шрифта")
        self.report_cell_font_size = StringVar(
            value=configs.settings.get('report-style').get("td-th")[0].get("font-size"))
        spin_report_cell_font_size = Spinbox(
            tab_style_report, from_=6, to=24,
            textvariable=self.report_cell_font_size)
        label_report_cell_font_size.grid(row=13, column=0)
        spin_report_cell_font_size.grid(row=13, column=1)
        # tab_ssh
        label_ssh_server = Label(tab_ssh, text="ssh сервер")
        self.ssh_server = StringVar(
            value=configs.settings.get('ssh').get("server"))
        entry_ssh_server = Entry(tab_ssh, textvariable=self.ssh_server)
        label_ssh_server.grid(row=0, column=0)
        entry_ssh_server.grid(row=0, column=1)
        label_ssh_user = Label(tab_ssh, text="ssh имя юзера")
        self.ssh_user = StringVar(
            value=configs.settings.get('ssh').get("user"))
        entry_ssh_user = Entry(tab_ssh, textvariable=self.ssh_user)
        label_ssh_user.grid(row=1, column=0)
        entry_ssh_user.grid(row=1, column=1)
        label_ssh_output_file = Label(tab_ssh, text="название файла на сервере")
        self.ssh_output_file = StringVar(
            value=configs.settings.get('ssh').get("output-file"))
        entry_ssh_output_file = Entry(tab_ssh, textvariable=self.ssh_output_file)
        label_ssh_output_file.grid(row=2, column=0)
        entry_ssh_output_file.grid(row=2, column=1)
        self.frame_buttons = Frame(self)
        self.frame_buttons.pack()
        btn_save = Button(self.frame_buttons, text='сохранить', command=self.save)
        btn_save.grid(column=0, row=0)
        btn_close = Button(self.frame_buttons, text="закрыть", command=self.close)
        btn_close.grid(column=1, row=0)

    def save(self, event=None):
        """method for save changed settings in toml file"""
        configs.change_setting("sizes", "width-navbar", self.width_navbar.get())
        configs.change_setting("sizes", "height-navbar", self.height_navbar.get())
        configs.change_setting("sizes", "width-table", self.width_table.get())
        configs.change_setting("sizes", "height-table", self.height_table.get())

        configs.change_setting_style(
            "styles", "navbar", "all-font", self.navbar_all_font.get())
        configs.change_setting_style(
            "styles", "navbar", 'all-font-size', self.navbar_all_font_size.get())
        configs.change_setting_style(
            "styles", "navbar", "tree-foreground", self.navbar_all_fg.get())
        configs.change_setting_style(
            "styles", "navbar", "heading-font", self.navbar_header_font.get())
        configs.change_setting_style(
            "styles", "navbar", "heading-font-size", self.navbar_header_font_size.get())
        configs.change_setting_style(
            "styles", "navbar", "heading-font-style", self.navbar_header_font_style.get())
        configs.change_setting_style(
            "styles", "navbar", "heading-foreground", self.navbar_header_fg.get())

        configs.change_setting_style(
            "styles", "table", "font", self.table_all_font.get())
        configs.change_setting_style(
            "styles", "table", "font-size", self.table_all_font_size.get())
        configs.change_setting_style(
            "styles", "table", "font-style", self.table_all_font_style.get())
        configs.change_setting_style(
            "styles", "table", "header-font", self.table_header_font.get())
        configs.change_setting_style(
            "styles", "table", "header-font-size", self.table_header_font_size.get())
        configs.change_setting_style(
            "styles", "table", "header-font-style", self.table_header_font_style.get())
        configs.change_setting_style(
            "styles", "table", "header-bg", self.table_header_bg.get())

        configs.change_setting_style(
            "report-style", "magazine", "color", self.report_magazine_color.get())
        configs.change_setting_style(
            "report-style", "magazine", "font-weight", self.report_magazine_font_weight.get())
        configs.change_setting_style(
            "report-style", "magazine", "font-size", self.report_magazine_font_size.get())
        configs.change_setting_style(
            "report-style", "magazine", "text-indent", self.report_magazine_text_indent.get() + "px")

        configs.change_setting_style(
            "report-style", "category", "color", self.report_category_color.get())
        configs.change_setting_style(
            "report-style", "category", "color", self.report_category_color.get())
        configs.change_setting_style(
            "report-style", "category", "font-style", self.report_category_font_style.get())
        configs.change_setting_style(
            "report-style", "category", "font-size", self.report_category_font_size.get())
        configs.change_setting_style(
            "report-style", "category", "text-indent", self.report_category_text_indent.get())

        configs.change_setting_style(
            "report-style", "table", "border", self.report_table_border.get())
        configs.change_setting_style(
            "report-style", "td-th", "border", self.report_cell_border.get())
        configs.change_setting_style(
            "report-style", "td-th", "font-size", self.report_cell_font_size.get())

        configs.change_setting("ssh", "server", self.ssh_server.get())
        configs.change_setting("ssh", "user", self.ssh_user.get())
        configs.change_setting("ssh", "output-file", self.ssh_output_file.get())

        self.destroy()

    def close(self, event=None):
        """close window preferences"""
        self.destroy()

    def change_navbar_all_fg(self, event=None):
        """change variable from askcolor window"""
        color = askcolor()[1]
        self.navbar_all_fg.set(color)

    def change_navbar_header_fg(self, event=None):
        """change variable from askcolor window"""
        color = askcolor()[1]
        self.navbar_header_fg.set(color)

    def change_table_header_bg(self, event=None):
        """change variable from askcolor window"""
        color = askcolor()[1]
        self.table_header_bg.set(color)

    def change_report_magazine_color(self, event=None):
        """change variable from askcolor window"""
        color = askcolor()[1]
        self.report_magazine_color.set(color)

    def change_report_category_color(self, event=None):
        """change variable from askcolor window"""
        color = askcolor()[1]
        self.report_category_color.set(color)

    def change_report_table_border(self, event=None):
        """change style borders of table"""
        Border(self, "table")

    def change_report_cell_border(self, event=None):
        """change style of cells in table"""
        Border(self, "td-th")


class Border(Toplevel):
    """
    create additional window for analyze methods
    """
    def __init__(self, parent, element):
        super().__init__(parent)

        self.element = element
        styles = ["inset", "outset", "solid", "double", "dotted", "dashed", "groove", "ridge"]

        lbl_width = Label(self, font=14, text="ширина рамки")
        self.width = IntVar(value=1)
        spin_width = Spinbox(self, from_=0, to=4, textvariable=self.width)
        lbl_style = Label(self, font=14, text="стиль рамки")
        self.style = StringVar(value="solid")
        menu_style = Combobox(self, values=styles, textvariable=self.style)
        lbl_color = Label(self, font=14, text="цвет рамки")
        self.color = ""
        btn_color = Button(self, text="цвет", command=self.change_color)

        btn_change = Button(self, text="изменить")
        btn_end = Button(self, text="Закрыть")

        lbl_width.grid(row=0, column=0)
        lbl_style.grid(row=0, column=1)
        lbl_color.grid(row=0, column=2)
        spin_width.grid(row=1, column=0)
        menu_style.grid(row=1, column=1)
        btn_color.grid(row=1, column=2)
        btn_change.grid(row=2, column=0)
        btn_end.grid(row=2, column=1)

        btn_change.bind("<Button-1>", self.change)
        btn_end.bind("<Button-1>", self.exit)

    def change_color(self, event=None):
        self.color = askcolor()[1]

    def change(self, event=None):
        if self.element == "table":
            configs.change_setting_style(
                "report-style", "table", "border", f"{self.width.get()}px {self.style.get()} {self.color}")
        elif self.element == "td-th":
            configs.change_setting_style(
                "report-style", "td-th", "border", f"{self.width.get()}px {self.style.get()} {self.color}")

    def exit(self, event=None):
        self.destroy()
