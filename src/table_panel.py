"""
module for class Table
"""
import logging
from tkinter import Frame

from src.settings.configs import settings
from src.simple_classes import Product
from src.tksheet import Sheet

widths_columns = []


class Table(Frame):
    """
    class Table creating table panel in main window
    """
    def __init__(self, parent, db_handler, status, magazine=None, category=None, kod=None, firm=None):
        logging.getLogger(__name__)
        global widths_columns
        super().__init__()

        self.db_handler = db_handler
        self.status = status
        self.magazine = magazine
        self.category = category
        self.kod = kod
        self.firm = firm
        names_columns = settings.get('names-product-columns').get('to-form-ru')
        self.names_cols_in_prod = settings.get('names-product-columns').get('to-form')
        self.products = self.db_handler.get_products(
            self.magazine, self.category, self.kod, self.firm)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.frame = Frame(parent)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)
        self.sheet = Sheet(
            self.frame, headers=names_columns, width=settings.get("sizes").get("width-table"),
            height=settings.get("sizes").get("height-table"), empty_vertical=0,
            empty_horizontal=0, header_bg=settings.get("styles").get("table")[0].get("header-bg"),
            header_font=(settings.get("styles").get("table")[0].get("header-font"),
                         settings.get("styles").get("table")[0].get("header-font-size"),
                         settings.get("styles").get("table")[0].get("header-font-style")),
            font=(settings.get("styles").get("table")[0].get("font"),
                  settings.get("styles").get("table")[0].get("font-size"),
                  settings.get("styles").get("table")[0].get("font-style")),
            all_columns_displayed=False, displayed_columns=(0, 1, 2, 3, 4, 5, 6, 7),
            data=[[product.firm, product.kod_tovara, product.opisanie, product.razmery,
                   product.tsena, product.raspr, product.category, product.magazine,
                   product.id]
                  for product in self.products])

        for i in range(self.sheet.get_total_rows()):
            self.sheet.create_dropdown(r=i, c=5, values=self.db_handler.get_raspr(),
                                       set_value=self.products[i].raspr)
            self.sheet.create_dropdown(r=i, c=6,
                                       values=self.db_handler.get_categories_for_magazine(
                                           self.products[i].magazine),
                                       set_value=self.products[i].category)
            self.sheet.create_dropdown(r=i, c=7, values=self.db_handler.get_magazines(),
                                       set_value=self.products[i].magazine)

        self.add_new_line()

        self.sheet.set_all_cell_sizes_to_text(False)
        if not widths_columns or widths_columns < self.sheet.get_column_widths():
            self.sheet.set_all_cell_sizes_to_text()
            widths_columns = self.sheet.get_column_widths()
        else:
            self.sheet.set_column_widths(widths_columns)

        self.sheet.set_options(expand_sheet_if_paste_too_big=True)
        self.sheet.readonly_columns([8])
        self.sheet.enable_bindings()
        self.sheet.disable_bindings("column_drag_and_drop")
        self.sheet.disable_bindings("row_drag_and_drop")
        self.sheet.disable_bindings("column_select")
        self.sheet.disable_bindings('rc_insert_column')
        self.sheet.disable_bindings('rc_delete_column')
        self.sheet.disable_bindings('rc_insert_row')
        self.sheet.extra_bindings("end_edit_cell", self.edit_cell_event)
        self.sheet.extra_bindings('begin_delete_rows', self.delete_rows_event)
        self.sheet.extra_bindings('end_paste', self.paste_event)
        self.sheet.extra_bindings("begin_delete", self.cell_dell_event)
        self.sheet.extra_bindings("begin_cut", self.cell_dell_event)
        self.frame.grid(row=0, column=0, sticky="nswe")
        self.sheet.grid(row=0, column=0, sticky="nswe")

    def edit_cell_event(self, event=None):
        """
        method for work with changes in cell of table
        """
        try:
            edited_row = self.sheet.get_row_data(event[0])
            if edited_row[5] == '':
                row_raspr = 1
            else:
                row_raspr = edited_row[5]
            edited_product = Product(
                (edited_row[8], edited_row[7], edited_row[2], edited_row[1], edited_row[4],
                 edited_row[3], edited_row[6], row_raspr, edited_row[0]))
            edited_product.column = self.names_cols_in_prod[event[1]]
            edited_product.value = event[3]

            if edited_product.column == "magazin":
                current_product = self.db_handler.get_product(edited_product.id)
                if current_product.magazine != edited_product.magazine:
                    categories_for_magazine = \
                        self.db_handler.get_categories_for_magazine(edited_product.value)
                    self.sheet.set_dropdown_values(r=event[0], c=6,
                                                   values=categories_for_magazine,
                                                   displayed=categories_for_magazine[0])
                    status = self.db_handler.update_product(edited_product)
                    self.status.status.set(status)
                    edited_product.column = "category"
                    edited_product.value = categories_for_magazine[0]

            if event[0] == self.sheet.get_total_rows() - 1:
                self.create_new_product(edited_product)
            else:
                if event[2] == "Escape":
                    status = "нажата esc, изменение отменено"
                else:
                    status = self.db_handler.update_product(edited_product)
                logging.info(f"товар: {edited_product} обновлен: поле "
                             f"{edited_product.column} изменено на {edited_product.value}")
                self.status.status.set(status)
        except Exception as exc:
            status = f"exception in edit_cell_event: {exc}, event: {event}, " \
                     f"column: {edited_product.column}, value: {edited_product.value}"
            self.status.status.set(status)
            logging.error(status)

    def create_new_product(self, edited_product):
        """
        create new product in table tovars in db
        """
        edited_product.id = self.db_handler.insert_product(edited_product)
        id_new_product = self.sheet.get_total_rows() - 1
        self.sheet.set_cell_data(r=id_new_product, c=8, value=edited_product.id)
        self.add_new_line()
        status = f"товар: {edited_product} добавлен в бд"
        self.status.status.set(status)
        logging.info(status)

    def add_new_line(self):
        """
        add new blank row in table for new record
        """
        self.sheet.insert_row()
        id_last_row = self.sheet.get_total_rows() - 1
        self.sheet.create_dropdown(r=id_last_row, c=5, values=self.db_handler.get_raspr(),
                                   set_value='')
        if self.magazine is None:
            i = 0
            self.magazine = self.db_handler.get_magazines()[i]
            while not self.db_handler.get_categories_for_magazine(self.magazine):
                i += 1
                self.magazine = self.db_handler.get_magazines()[i]
        self.sheet.create_dropdown(r=id_last_row, c=7,
                                   values=self.db_handler.get_magazines(),
                                   set_value=self.magazine)
        if self.category is None:
            try:
                self.category = self.db_handler.get_categories_for_magazine(self.magazine)[0]
            except IndexError as e:
                print(e)
                self.category = self.db_handler.get_categories_for_magazine(self.magazine)[1]
        self.sheet.create_dropdown(
            r=id_last_row, c=6,
            values=self.db_handler.get_categories_for_magazine(self.magazine),
            set_value=self.category)

    def delete_rows_event(self, event=None):
        """
        delete record from db where delete row in table
        """
        try:
            for row_id in event.deleteindexes:
                deleted_row = self.sheet.get_row_data(row_id)
                status = self.db_handler.del_from_table("tovars", deleted_row[8])
                self.status.status.set(status)
                logging.info(f"удален товар: {deleted_row}")
        except Exception as exc:
            status = f"exception in delete_rows_event: {exc}"
            self.status.status.set(status)
            logging.error(status)

    def cell_dell_event(self, event=None):
        """
        change data in db in product to ""
        """
        try:
            selected = event.selectionboxes
            edited_rows = range(selected[0][0][0], selected[0][0][2])
            for row in edited_rows:
                edited_row = self.sheet.get_row_data(row)
                if edited_row[5] == '':
                    row_raspr = 1
                else:
                    row_raspr = edited_row[5]
                edited_product = Product(
                    (edited_row[8], edited_row[7], edited_row[2], edited_row[1], edited_row[4],
                     edited_row[3], edited_row[6], row_raspr, edited_row[0]))
                edited_product.column = self.names_cols_in_prod[event.currentlyselected[1]]
                edited_product.value = ''
                status = self.db_handler.update_product(edited_product)
                self.status.status.set(status)
                logging.info(f"товар обновлен: {edited_product}, "
                             f"поле: {edited_product.column} "
                             f"установлено в {edited_product.value}")
        except Exception as exc:
            status = f"exception in cell_dell_event: {exc}"
            self.status.status.set(status)
            logging.error(status)

    def paste_event(self, event=None):
        """
        paste data to db for product
        """
        try:
            edited_row = self.sheet.get_row_data(event.currentlyselected[0])
            if edited_row[5] == '':
                row_raspr = 1
            else:
                row_raspr = edited_row[5]
            edited_product = Product(
                (edited_row[8], edited_row[7], edited_row[2], edited_row[1], edited_row[4],
                 edited_row[3], edited_row[6], row_raspr, edited_row[0]))
            edited_product.column = self.names_cols_in_prod[event.currentlyselected[1]]
            edited_product.value = event.rows[0][0]
            status = self.db_handler.update_product(edited_product)
            self.status.status.set(status)
            logging.info(f"товар обновлен: {edited_product}, "
                         f"поле: {edited_product.column} установлено в {edited_product.value}")
        except Exception as exc:
            status = f"exception in paste_event: {exc}"
            self.status.status.set(status)
            logging.error(status)
