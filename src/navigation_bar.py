"""
module for navigation bar
"""
import logging
from tkinter import Frame, Scrollbar, VERTICAL, HORIZONTAL, N, S, E, W, END, Menu, Toplevel, Label, StringVar, Entry, \
    Button
from tkinter.ttk import Treeview, Style

from src.report import Report
from src.settings.configs import settings
from src.table_panel import Table


class Navbar(Frame):
    """
    class for creating navigation bar for db
    """
    def __init__(self, parent, table_panel, db_handler, status):
        super().__init__()
        self.magazine = ''
        self.parent = parent
        self.table = table_panel
        self.db_handler = db_handler
        self.status = status
        self.print_list = []

        style = Style()
        style.configure("Treeview",
                        foreground=settings.get("styles").get("navbar")[0]
                        .get("tree-foreground"),
                        font=(settings.get("styles").get("navbar")[0].get("all-font"),
                              settings.get("styles").get("navbar")[0]
                              .get("all-font-size")))
        style.configure("Treeview.Heading", font=(settings.get("styles").get("navbar")[0]
                                                  .get("heading-font"),
                                                  settings.get("styles").get("navbar")[0]
                                                  .get("heading-font-size"),
                                                  settings.get("styles").get("navbar")[0]
                                                  .get("heading-font-style")),
                        foreground=settings.get("styles").get("navbar")[0]
                                           .get("heading-foreground"))

        head = "Категория"
        self.cats_in_mags = self.db_handler.get_cats_in_mags()

        self.nodes = {}
        self.tree = Treeview(parent, height=settings.get("sizes").get("height-navbar"))
        self.tree.heading("#0", text=head, anchor=W)
        ysb = Scrollbar(parent, orient=VERTICAL, command=self.tree.yview())
        xsb = Scrollbar(parent, orient=HORIZONTAL, command=self.tree.xview())
        self.tree.configure(yscrollcommand=ysb.set, xscrollcommand=xsb.set)
        xsb.config(command=self.tree.xview)
        ysb.config(command=self.tree.yview)

        self.tree.grid(row=0, column=0, sticky=N + S + E + W)
        ysb.grid(row=0, column=1, sticky=N + S)
        xsb.grid(row=1, column=0, sticky=E + W)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.popup = Menu(self.parent, tearoff=0)
        self.popup.add_command(label="Печать", command=self.print_report)
        self.popup.add_command(label="Изменить", command=self.change_item)
        self.popup.add_separator()
        self.popup.add_command(label="Добавить в список печати", command=self.add_to_print_list)
        self.popup.add_command(label="очистить список печати", command=self.clean_print_list)
        self.popup.add_command(label="Распечатать список", command=self.print_printlist)

        def popup_menu(event):
            self.popup.selection = self.tree.identify_row(event.y)
            self.popup.post(event.x_root, event.y_root)

        self.tree.bind("<Button-3>", popup_menu)

        self.tree.bind("<<TreeviewOpen>>", self.open_node)
        self.populate_node("", self.cats_in_mags)
        self.tree.bind("<<TreeviewSelect>>", self.select_node)

        self.tree.column("#0", width=settings.get("sizes").get("width-navbar"))

    def populate_node(self, parent, category, magazine=''):
        """
        method for creating population for current node
        :param parent: parent node
        :param category: category of product
        :param magazine: name of magazine
        """
        if magazine == '':
            self.tree.insert(parent, END, text="Все")
        for entry in sorted(category):
            node = self.tree.insert(parent, END, text=entry, open=False, tags=magazine)
            if entry in self.cats_in_mags:
                self.nodes[node] = entry
                self.tree.insert(node, END)

    def open_node(self, event):
        """
        method to open node if this node has children
        """
        item = self.tree.focus()
        line = self.nodes.pop(item, False)
        if line in self.cats_in_mags:
            children = self.tree.get_children(item)
            self.tree.delete(children[0])
            self.populate_node(item, self.cats_in_mags[line], line)

    def select_node(self, event):
        """
        method to open table for current magazine and category
        """
        self.open_node("<<TreeviewOpen>>")
        for selection in self.tree.selection():
            item = self.tree.item(selection)
            if item['text'] == "Все":
                Table(self.table, self.db_handler, self.status)
            elif item['text'] in self.cats_in_mags:
                magazine = item['text']
                Table(self.table, self.db_handler, self.status, magazine)
            else:
                category = item['text']
                magazine = item['tags'][0]
                Table(self.table, self.db_handler, self.status,  magazine, category)

    def print_report(self):
        selection = self.popup.selection
        item = self.tree.item(selection)
        if item['text'] == "Все":
            Report(self.status).print_report()
        elif item['text'] in self.cats_in_mags:
            magazine = item['text']
            Report(self.status, magazine).print_report()
        else:
            category = item['text']
            magazine = item['tags'][0]
            Report(self.status, magazine, category).print_report()

    def change_item(self):
        selection = self.popup.selection
        item = self.tree.item(selection)
        if item['text'] == "Все":
            self.status.status.set("нельзя переименовать")
        elif item['text'] in self.cats_in_mags:
            old_name_magazine = item['text']
            ChangeMagazine(self.parent, self.db_handler, self.table,
                           self.status, old_name_magazine)
        else:
            old_name_category = item['text']
            ChangeCategory(self.parent, self.db_handler, self.table,
                           self.status, old_name_category)

    def add_to_print_list(self):
        selection = self.popup.selection
        item = self.tree.item(selection)
        if item['tags'] != "":
            magazine = item['tags'][0]
            category = item['text']
            item = (magazine, category)
            self.print_list.append(item)

    def clean_print_list(self):
        self.print_list.clear()

    def print_printlist(self):
        if len(self.print_list) != 0:
            Printed(self.parent, self.db_handler, self.status, self.print_list)


class ChangeMagazine(Toplevel):
    """
    class for additional window to change name of magazine in table magazins in db
    """
    def __init__(self, parent, db_handler, table_panel, status, old_name_magazine):
        super().__init__(parent)
        self.parent = parent
        self.db_handler = db_handler
        self.table_panel = table_panel
        self.status = status
        self.old_name_magazine = old_name_magazine
        label = Label(self, text="Новое название магазина", takefocus=True, font=14)
        self.magazine = StringVar()
        entry_name_magazine = Entry(self, font=12, textvariable=self.magazine)
        entry_name_magazine.insert(0, self.old_name_magazine)
        btn_change = Button(self, text="Изменить")
        self.label_status = Label(self, text="", font=14)

        label.grid(row=0, column=0)
        entry_name_magazine.grid(row=1, column=0)
        btn_change.grid(row=2, column=0)
        self.label_status.grid(row=3, column=0)

        btn_change.bind("<Button-1>", self.change_magazine)

    def change_magazine(self, event):
        """
        change name of magazine in db
        """
        all_magazines = self.db_handler.get_magazines()
        magazines = []
        for magazine in all_magazines:
            magazines.append(magazine.magazine)
        if self.magazine.get() not in magazines:
            status = self.db_handler.update_magazine(self.magazine.get(), self.old_name_magazine)
            self.status.status.set(status)
            logging.info(status)
            Navbar(self.parent, self.table_panel, self.db_handler, self.status)
            self.destroy()
        else:
            self.label_status.config(text="такой магазин уже существует")


class ChangeCategory(Toplevel):
    """
    class for additional window to change name of category in table categories in db
    """
    def __init__(self, parent, db_handler, table_panel, status, old_name_category):
        super().__init__(parent)
        self.parent = parent
        self.db_handler = db_handler
        self.table_panel = table_panel
        self.status = status
        self.old_name_category = old_name_category
        label = Label(self, text="Новое название категории", takefocus=True, font=14)
        self.category = StringVar()
        entry_name_category = Entry(self, font=12, textvariable=self.category)
        entry_name_category.insert(0, self.old_name_category)
        btn_change = Button(self, text="Изменить")
        self.label_status = Label(self, text="", font=14)

        label.grid(row=0, column=0)
        entry_name_category.grid(row=1, column=0)
        btn_change.grid(row=2, column=0)
        self.label_status.grid(row=3, column=0)

        btn_change.bind("<Button-1>", self.change_category)

    def change_category(self, event):
        """
        change name of category in db
        """
        all_categories = self.db_handler.get_categories()
        categories = []
        for category in all_categories:
            categories.append(category.category)
        if self.category.get() not in categories:
            status = self.db_handler.update_category(self.category.get(), self.old_name_category)
            self.status.status.set(status)
            logging.info(status)
            Navbar(self.parent, self.table_panel, self.db_handler, self.status)
            self.destroy()
        else:
            self.label_status.config(text="такая категория уже существует")


class Printed(Toplevel):
    def __init__(self, parent, db_handler, status, print_list):
        super().__init__(parent)
        self.parent = parent
        self.db_handler = db_handler
        self.status = status
        self.print_list = print_list
        self.cats_in_mags = {}
        magazines = set()
        category = []
        for item in self.print_list:
            magazine = item[0]
            magazines.add(magazine)
        for magazine in magazines:
            for item in self.print_list:
                if magazine == item[0]:
                    category += [item[1]]
                self.cats_in_mags[magazine] = category
            category = []

        label = Label(self, text="Список на печать", takefocus=True, font=14)
        label.pack()
        for magazine in self.cats_in_mags:
            label = Label(self, text=magazine, font=12, foreground='red')
            label.pack()
            for category in self.cats_in_mags[magazine]:
                lbl = Label(self, text=category, font=10, foreground='blue')
                lbl.pack()
        btn_print = Button(self, text="Печать")
        btn_cancel = Button(self, text="Отменить")

        btn_print.pack()
        btn_cancel.pack()

        btn_print.bind("<Button-1>", self.print_report)
        btn_cancel.bind("<Button-1>", self.cancel)

    def print_report(self, event=None):
        Report(self.status).print_custom_report(self.cats_in_mags)
        self.destroy()

    def cancel(self, event=None):
        self.destroy()
