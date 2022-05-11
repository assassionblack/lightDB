lightDB
=======

Приложение для работы с базой данных sqlite3

============================================

Platform
========
    linux
    may be unix based systems
        tested on:
            linuxmint
            archlinux

Features
========

    создание базы данных
    визуальное редактирование базы данных
    добавление/удаление категорий товаров
    добавление/удаление магазинов
    печать отчета (всего товара) в html формате (можно открывать в office пакетах)
    анализатор бд: удаление пробелов, пустых категорий, пустых магазинов, пустых записей
    возможность создания бекапа (пункт меню сохранить как...)

Versions release note:
======================

    1.0.1:
        fix some bugs
        change searching to "like" from "="
        add unregistered search
    1.1:
        fix some bugs
        add unregistered search
    1.2:
        fix some bugs
        add menu preferences
    1.3:
        fix bugs
        add features:
            - create new database
            - open database from file
            - if given path to database - this database was opened
    2.0:
        fix bugs
        add window for configuration settings

PreInstallation
===============

    copy logging_conf.json, settings.toml
                from src/settings/ to ~/.config/lightDB/
    copy report.html, report-category.html, report-custom.html, report-magazine.html
                from src/templates/ to ~/.config/lightDB
    
Setup
=====

    to build:
        install from pip: jinja2, pyinstaller
        cd lightDB
        build:
            pyinstaller --onefile --windowed src/main.py --name lightDB
        copy or cut lightDB from build/ to ~/.local/bin/

Run
====
    
    to run:
        type "lightDB" or "lightDB {path_to_database}" in terminal
    to open database created not in lightDB this database must be:
        tables:
            - categories:
                - id            integer, autoincrement
                - category_name text
            - cats_in_mags:
                - id            integer, autoincrement
                - mag_name      integer (= id in magazins)
                - cat_name      integer (= id in categories)
            - magazins:
                - id            integer, autoincrement
                - magazin_name  text
            - raspr
                - id            integer, autoincrement
                - raspr_flag    text
            -tovars
                - id            integer, autoincrement
                - magazin       integer (= id in magazins)
                - opisanie      text
                - kod_tovara    text
                - tsena         text
                - razmery       text
                - category      integer (= id in categories)
                - raspr         integer (= id in raspr)
                - firma         text
        table magazins must have at least one magazine
        table categories must have at least one category
        table cats_in_mags must have at least one record
        raspr after create must insert two values ('','р')