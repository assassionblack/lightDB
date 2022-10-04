"""
module for displaying menu bar
"""
import logging
import os
import shutil
from tkinter import Frame, Menu, filedialog, StringVar
from tkinter.messagebox import askyesno

from paramiko.client import SSHClient
from paramiko.ssh_exception import NoValidConnectionsError
from scp import SCPClient

from src.report import Report
from src.settings import configs


class CommonMenu(Frame):
    """
    class create menus
    """
    def __init__(self, parent, status, top, navigation_panel, table_panel):
        logging.getLogger(__name__)
        super().__init__()
        self.status = status
        self.parent = parent
        self.top = top
        self.navigation_panel = navigation_panel
        self.table_panel = table_panel

        self.option_add("*Menu.font", "Calibri 10")

        self.common_menu = Menu(self.parent)
        self.parent.config(menu=self.common_menu)

        self.menu_file = Menu(self.common_menu)
        self.common_menu.add_cascade(label='Файл', menu=self.menu_file)
        self.menu_file.add_command(label="Открыть", command=self.open_db)
        self.menu_file.add_command(label="Создать", command=self.create_db)
        self.menu_file.add_command(label="Сохранить как...", command=self.save_as)
        self.menu_file.add_command(label='Закрыть', accelerator="Alt+F4",
                                   command=self.close)

        self.menu_edit = Menu(self.common_menu)
        self.common_menu.add_cascade(label='Правка', menu=self.menu_edit)
        self.menu_edit.add_command(label='Печать', accelerator="Ctrl+p",
                                   command=self.report)
        self.menu_edit.add_separator()
        ssh = configs.settings['copy']['ssh']
        if ssh != "true":
            ssh = "0"
        else:
            ssh = "1"
        self.check_save = StringVar()
        self.check_save.set(ssh)
        self.menu_edit.add_checkbutton(label="отправить при завершении на сервер?",
                                       onvalue="1", offvalue="0", variable=self.check_save,
                                       command=self.save_to_ssh)

        self.bind_all("<Control-p>", self.report)
        self.bind_all("<Alt-F4>", self.close)

    def open_db(self, event=None):
        configs.DB_NAME = filedialog.askopenfilename(
            filetypes=(("DB files", "*.db"),),
            initialdir=f"/home/{os.getlogin()}/Рабочий стол")
        if configs.DB_NAME not in ((), ''):
            from src.db_window import load
            load(self.status, self.top, self.navigation_panel, self.table_panel)

    def create_db(self, event=None):
        configs.DB_NAME = filedialog.asksaveasfilename(
            filetypes=(("DB files", "*.db"),),
            initialdir=f"/home/{os.getlogin()}/Рабочий стол")
        if configs.DB_NAME not in ((), ''):
            from src.db_window import create_db
            create_db(self.status, self.top, self.navigation_panel, self.table_panel)

    def report(self, event=None):
        """
        method printing report for db to file
        """
        Report(self.status).print_report()
        status_var = "отчет передан на печать"
        self.status.status.set(status_var)
        logging.info(status_var)

    def save_as(self, event=None):
        """
        method for copy db to given path
        """
        file_name = filedialog.asksaveasfilename(
            filetypes=(("DB files", "*.db"),), initialdir=f"/home/{os.getlogin()}/")
        if file_name not in ('', ()):
            shutil.copy(configs.DB_NAME, file_name)
        status_var = f"бд скопирована в {file_name}"
        self.status.status.set(status_var)
        logging.info(status_var)

    def close(self, event=None):
        """
        method for closing connection with db and close program
        """
        message = "Вы уверены, что хотите закрыть это окно?"
        if askyesno(message=message, parent=self.parent):
            if configs.settings.get('copy').get('ssh') == 'true':
                try:
                    ssh = SSHClient()
                    ssh.load_system_host_keys()
                    ssh.connect(configs.settings.get("ssh").get("server"),
                                username=configs.settings.get("ssh").get("user"))

                    with SCPClient(ssh.get_transport()) as scp:
                        scp.put(configs.DB_NAME, 'base.db')
                    status_var = "база данных отправлена на сервер"
                    self.status.status.set(status_var)
                    logging.info(status_var)
                except NoValidConnectionsError as exc:
                    status_var = f"бд не отправлена на сервер, соединение не установлено:" \
                                 f"\n\r{exc}"
                    self.status.status.set(status_var)
                    logging.error(status_var)

            from src.db_window import close_db
            close_db()
            status_var = "соединение с бд закрыто\nпрограмма закрыта"
            self.status.status.set(status_var)
            logging.info(status_var)
            self.parent.destroy()

    def save_to_ssh(self, event=None):
        """method for change flag for copy db into ssh server"""
        if self.check_save.get() == '0':
            configs.change_setting("copy", "ssh", "false")
        else:
            configs.change_setting("copy", "ssh", "true")
