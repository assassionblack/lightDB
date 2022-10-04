"""
module for configuration report for db in table format and save him to document
"""
import datetime
import logging
import os
from tkinter import filedialog

from jinja2 import Environment, select_autoescape, FileSystemLoader

from src.db_handler import DbHandler
from src.settings.configs import settings


class Report:
    """
    class configuration document from html template
    """

    def __init__(self, status, magazine=None, category=None):
        logging.getLogger(__name__)
        self.settings = settings
        self.status = status
        self.magazine = magazine
        self.category = category
        self.env = Environment(
            loader=FileSystemLoader(f"/home/{os.getlogin()}/.config/lightDB/"),
            autoescape=select_autoescape(['html', 'xml'])
        )

        self.db_handler = DbHandler()

        if self.magazine is None:
            template = self.env.get_template("report.html")
            self.report = template.render(
                magazine_style=self.settings.get('report-style').get('magazine')[0],
                category_style=self.settings.get('report-style').get('category')[0],
                table_style=self.settings.get('report-style').get('table')[0],
                tr_style=self.settings.get('report-style').get('tr')[0],
                td_th=self.settings.get('report-style').get('td-th')[0],
                names_columns=self.settings.get("names-product-columns").get("to-report"),
                date_now=datetime.date.today(),
                db_handler=self.db_handler
            )
        elif self.category is None:
            template = self.env.get_template("report-magazine.html")
            self.report = template.render(
                magazine_style=self.settings.get('report-style').get('magazine')[0],
                category_style=self.settings.get('report-style').get('category')[0],
                table_style=self.settings.get('report-style').get('table')[0],
                tr_style=self.settings.get('report-style').get('tr')[0],
                td_th=self.settings.get('report-style').get('td-th')[0],
                names_columns=self.settings.get("names-product-columns").get("to-report"),
                date_now=datetime.date.today(),
                db_handler=self.db_handler,
                magazine=self.magazine
            )
        else:
            template = self.env.get_template("report-category.html")
            self.report = template.render(
                magazine_style=self.settings.get('report-style').get('magazine')[0],
                category_style=self.settings.get('report-style').get('category')[0],
                table_style=self.settings.get('report-style').get('table')[0],
                tr_style=self.settings.get('report-style').get('tr')[0],
                td_th=self.settings.get('report-style').get('td-th')[0],
                names_columns=self.settings.get("names-product-columns").get("to-report"),
                date_now=datetime.date.today(),
                db_handler=self.db_handler,
                magazine=self.magazine,
                category=self.category
            )

    def print_report(self):
        """
        method print document to file
        """
        if self.magazine is None:
            name = self.settings.get("report-file").get("output-name") \
                          + "[" + str(datetime.date.today()) + "]"
        elif self.category is None:
            name = self.magazine + "[" + str(datetime.date.today()) + "]"
        else:
            name = self.magazine + "_" + self.category + "_" \
                          + "[" + str(datetime.date.today()) + "]" \

        report_name = filedialog.asksaveasfilename(
            filetypes=(("Document doc", "*.doc"), ("Document html", "*.html")),
            initialdir=f"/home/{os.getlogin()}/Рабочий стол", initialfile=name)
        if report_name not in ((), ""):
            with open(report_name, mode="w", encoding="utf-8") as file:
                file.write(self.report)

            status = f"печать в файл {report_name} завершена!"
            logging.info(status)
            self.status.status.set(status)

    def print_custom_report(self, cats_in_mags):
        template = self.env.get_template("report-custom.html")
        report = template.render(
            magazine_style=self.settings.get('report-style').get('magazine')[0],
            category_style=self.settings.get('report-style').get('category')[0],
            table_style=self.settings.get('report-style').get('table')[0],
            tr_style=self.settings.get('report-style').get('tr')[0],
            td_th=self.settings.get('report-style').get('td-th')[0],
            names_columns=self.settings.get("names-product-columns").get("to-report"),
            date_now=datetime.date.today(),
            db_handler=self.db_handler,
            cats_in_mags=cats_in_mags
        )
        name = self.settings.get("report-file").get("output-name") + "[" \
               + str(datetime.date.strftime(datetime.datetime.now(),
                                            "%Y-%M-%d %H-%M-%S")) + "]"

        report_name = filedialog.asksaveasfilename(
            filetypes=(("Document doc", "*.doc"), ("Document html", "*.html")),
            initialdir=f"/home/{os.getlogin()}/Рабочий стол", initialfile=name)

        if report_name not in ("", ()):
            with open(report_name, mode="w", encoding="utf-8") as file:
                file.write(report)

            status = f"печать в файл {report_name} завершена!"
            logging.info(status)
            self.status.status.set(status)
