"""
module for application mainloop
"""
import logging
import os.path
import tkinter.ttk
from tkinter.messagebox import askyesno

import paramiko
from paramiko.client import SSHClient
from scp import SCPClient

from src.common_menu import CommonMenu
from src.db_window import window, close_db
from src.settings import configs
from src.status_bar import Status


def confirm_delete():
    message = "Вы уверены, что хотите закрыть это окно?"
    if askyesno(message=message, parent=root):
        if configs.settings.get("copy").get("ssh") == 'true':
            try:
                ssh = SSHClient()
                ssh.load_system_host_keys()
                ssh.connect(configs.settings.get("ssh").get("server"),
                            username=configs.settings.get("ssh").get("user"))

                with SCPClient(ssh.get_transport()) as scp:
                    scp.put('/home/assassion/ideas', 'ideas2')
                    scp.get('ideas2')
                status_var = "база данных отправлена на сервер"
                status_bar.status.set(status_var)
                logging.info(status_var)
            except paramiko.ssh_exception.NoValidConnectionsError as exc:
                status_var = f"бд не отправлена на сервер, соединение не установлено:" \
                             f"\n\r{exc}"
                status_bar.status.set(status_var)
                logging.error(status_var)
        close_db()
        status_var = "соединение с бд закрыто\nпрограмма закрыта"
        status_bar.status.set(status_var)
        logging.info(status_var)
        root.destroy()


if __name__ == '__main__':
    logging.getLogger(__name__)
    root = tkinter.Tk()
    root.title("lightDB")
    root.attributes("-zoomed", True)
    width, height = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry(f"{width}x{height}")

    status = tkinter.Frame(root)
    status.pack(side=tkinter.BOTTOM, anchor="center", fill=tkinter.BOTH, padx=10.0)

    status_bar = Status(status)

    top = tkinter.Frame(root)
    navigation_panel = tkinter.Frame(root)
    table_panel = tkinter.Frame(root)

    common_menu = CommonMenu(root, status_bar, top, navigation_panel, table_panel)

    window(status_bar, top, navigation_panel, table_panel)

    root.protocol("WM_DELETE_WINDOW", confirm_delete)

    root.mainloop()
