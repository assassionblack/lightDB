"""module for creating common window"""
import os
import sqlite3
import sys
from tkinter import TOP, X, LEFT, BOTH

from src import DbHandler, Navbar, Table, ToolBar
from src.settings import configs


def window(status, top, navigation_panel, table_panel):
    """
    function for windowing Navbar, Table, Toolbar
    """
    if configs.DB_NAME not in ("", ()):
        if len(sys.argv) > 1:
            if os.path.exists(sys.argv[1]):
                configs.DB_NAME = sys.argv[1]
                load(status, top, navigation_panel, table_panel)


def load(status, top, navigation_panel, table_panel):
    """function for load common frames"""
    db_handler = DbHandler()
    top.pack(side=TOP, fill=X)
    navigation_panel.pack(side=LEFT, fill=BOTH, expand=True, pady=10)
    table_panel.pack(side=LEFT, fill=BOTH, expand=True, pady=10)
    Navbar(navigation_panel, table_panel, db_handler, status)
    Table(table_panel, db_handler, status)
    ToolBar(top, db_handler, table_panel, navigation_panel, status)


def create_db(status, top, navigation_panel, table_panel):
    """function for creating new database and load common frames"""
    DbHandler().new_db()
    load(status, top, navigation_panel, table_panel)


def close_db():
    """close connection to db"""
    DbHandler().cursor.close()
    DbHandler().con.close()
