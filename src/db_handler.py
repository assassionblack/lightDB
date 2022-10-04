"""
Module for working with sqlite db
"""
import logging
import sqlite3

from src.settings import configs
from src.simple_classes import *


class DbHandler:
    """
    class singleton for working with db
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DbHandler, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        logging.getLogger(__name__)
        try:
            self.con = sqlite3.connect(configs.DB_NAME)
            self.cursor = self.con.cursor()
            self.status = "бд открыта"
            logging.info(self.status)
        except sqlite3.Error as sql_err:
            self.status = f"ошибка подключения к бд: {sql_err}"
            logging.error(self.status)

        def sqlite_lower(value_):
            return value_.lower()

        self.con.create_function("LOWER", 1, sqlite_lower)

    def __get_data(self, sql):
        try:
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except sqlite3.Error as sql_err:
            self.status = f"ошибка в методе __get_data: {sql_err}, введенный запрос: {sql}"
            logging.error(self.status)
            return []

    def __set_data(self, sql, data=''):
        try:
            self.cursor.execute(sql, data)
            self.con.commit()
            self.status = "Данные записаны"
        except sqlite3.Error as sql_err:
            self.status = f"ошибка в методе __set_data: {sql_err}, введенный запрос: {sql}"
            logging.error(self.status)
        return self.status

    def get_categories(self):
        """
        method get data from table categories
        :return: list[Category]
        """
        sql = "SELECT * FROM categories ORDER BY category_name"
        categories = self.__get_data(sql)
        cats = []
        for category in categories:
            cat = Category(category)
            cats.append(cat)
        return cats

    def set_category(self, magazine, category):
        """
        set new category in table categories
        :param magazine: name of magazine in db
        :param category: name of new category
        """
        category = category.strip()
        sql = f"INSERT INTO categories (category_name) " \
              f"SELECT '{category}' " \
              f"WHERE NOT EXISTS(SELECT 1 FROM categories WHERE category_name='{category}')"
        self.__set_data(sql)
        sql = f"SELECT id FROM magazins WHERE magazin_name='{magazine}'"
        mag_id = self.__get_data(sql)
        sql = f"SELECT id FROM categories WHERE category_name='{category}'"
        cat_id = self.__get_data(sql)
        sql = f"INSERT INTO cats_in_mags (mag_name,cat_name) " \
              f"VALUES ('{mag_id[0][0]}','{cat_id[0][0]}')"
        self.__set_data(sql)
        self.status = f"категория: {magazine}:{category} добавлена в бд"
        logging.info(self.status)
        return self.status

    def get_categories_for_magazine(self, magazine=None):
        """
        get categories for current magazine
        :param magazine: name of magazine in db
        :return: list[Category]
        """
        if magazine is None:
            magazine = self.get_magazines()[0]
        sql = "SELECT categories.id,category_name " \
              "FROM categories,magazins,cats_in_mags " \
              f"WHERE categories.id=cats_in_mags.cat_name AND magazins.id=cats_in_mags.mag_name " \
              f"AND magazins.magazin_name='{magazine}' ORDER BY categories.category_name"
        categories = self.__get_data(sql)
        cats = []
        for cat_in_mag in categories:
            cat = Category(cat_in_mag)
            cats.append(cat)
        return cats

    def get_magazines(self):
        """
        get all magazines from db
        :return: list[Magazine]
        """
        sql = "SELECT * FROM magazins ORDER BY magazin_name"
        magazines = self.__get_data(sql)
        mags = []
        for magazine in magazines:
            mag = Magazine(magazine)
            mags.append(mag)
        return mags

    def set_magazine(self, magazine):
        """
        set new category in table categories
        :param magazine: str
        """
        magazine = magazine.strip()
        sql = f"INSERT INTO magazins (magazin_name) VALUES ('{magazine}')"
        self.__set_data(sql)
        self.status = f"магазин: {magazine} добавлен в бд"
        logging.info(self.status)
        return self.status

    def get_raspr(self):
        """
        get all raspr in table raspr
        :return: list[Raspr]
        """
        sql = "SELECT * FROM raspr"
        rasprs = self.__get_data(sql)
        rasprs_objects = []
        for raspr in rasprs:
            raspr_object = Raspr(raspr)
            rasprs_objects.append(raspr_object)
        return rasprs_objects

    def get_cats_in_mags(self):
        """
        get all data from table cats_in_mags in readable format
        :return: Map{magazine, list[categories]}
        """
        sql = "SELECT magazins.magazin_name,categories.category_name " \
              "FROM cats_in_mags,magazins,categories " \
              "WHERE mag_name=magazins.id AND cat_name=categories.id " \
              "ORDER BY mag_name, cat_name"
        cats_in_mags = self.__get_data(sql)
        mag_cats = {}
        categories = []
        for cat in cats_in_mags:
            if cat[0] in mag_cats:
                categories.append(cat[1])
            else:
                categories = [cat[1]]
            mag_cats[cat[0]] = categories
        return mag_cats

    def get_product(self, id_product):
        """
        get product by id
        :param id_product: id of product in table tovars
        :return: Product
        """
        sql = f"SELECT tovars.id,magazin_name,opisanie,kod_tovara,tsena,razmery," \
              f"category_name,raspr_flag,firma " \
              f"FROM tovars,magazins,categories,raspr WHERE magazin=magazins.id " \
              f"AND category=categories.id " \
              f"AND raspr=raspr.id AND tovars.id='{id_product}' " \
              f"ORDER BY magazin_name,category_name,firma,kod_tovara,opisanie"
        prod = self.__get_data(sql)
        for product in prod:
            return Product(product)

    def get_products(self, magazine=None, category=None, kod=None, firm=None):
        """
        get all products from table tovars
        :param magazine: name of magazine
        :param category: name of category
        :param kod: kod_tovara in db
        :param firm: name of firm in db
        :return: list[Product]
        """
        if magazine is None:
            sql = self.__get_all_products()
        else:
            if category is None:
                sql = self.__get_products_by_magazine(magazine)
            else:
                sql = self.__get_products_by_category(magazine, category)
        if kod is not None:
            sql = self.__get_products_by_kod(kod.lower())
        if firm is not None:
            sql = self.__get_products_by_firm(firm.lower())
        products = self.__get_data(sql)
        prods = []
        for item in products:
            prods.append(Product(item))
        return prods

    def __get_all_products(self):
        return "SELECT tovars.id,magazin_name,opisanie,kod_tovara,tsena,razmery," \
               "category_name,raspr_flag,firma " \
               "FROM tovars,magazins,categories,raspr WHERE magazin=magazins.id " \
               "AND category=categories.id " \
               "AND raspr=raspr.id ORDER BY magazin_name,category_name,firma,kod_tovara,opisanie"

    def __get_products_by_magazine(self, magazine):
        return f"SELECT tovars.id,magazin_name,opisanie,kod_tovara,tsena,razmery," \
               f"category_name,raspr_flag,firma " \
               f"FROM tovars,magazins,categories,raspr WHERE magazin=magazins.id " \
               f"AND category=categories.id AND raspr=raspr.id AND magazin_name='{magazine}' " \
               f"ORDER BY category_name,firma,kod_tovara,opisanie"

    def __get_products_by_category(self, magazine, category):
        return f"SELECT tovars.id,magazin_name,opisanie,kod_tovara,tsena,razmery,category_name," \
               f"raspr_flag,firma FROM tovars,magazins,categories,raspr " \
               f"WHERE magazin=magazins.id AND category=categories.id AND raspr=raspr.id " \
               f"AND magazin_name='{magazine}' AND category_name='{category}' " \
               f"ORDER BY firma,kod_tovara,opisanie"

    def __get_products_by_kod(self, kod=""):
        return f"SELECT tovars.id,magazin_name,opisanie,kod_tovara,tsena,razmery," \
               f"category_name,raspr_flag,firma " \
               f"FROM tovars,magazins,categories,raspr " \
               f"WHERE magazin=magazins.id AND category=categories.id " \
               f"AND raspr=raspr.id AND LOWER(kod_tovara)='{kod}' " \
               f"ORDER BY magazin_name,category_name,firma,opisanie"

    def __get_products_by_firm(self, firm=""):
        return f"SELECT tovars.id,magazin_name,opisanie,kod_tovara,tsena,razmery," \
               f"category_name,raspr_flag,firma " \
               f"FROM tovars,magazins,categories,raspr " \
               f"WHERE magazin=magazins.id AND category=categories.id " \
               f"AND raspr=raspr.id AND LOWER(firma)='{firm}' " \
               f"ORDER BY magazin_name,category_name,kod_tovara,opisanie"

    def insert_product(self, product):
        """
        insert new product in table tovars
        :param product: Product
        :return product.id: int
        """
        if product.column == "magazin":
            sql = f"SELECT id FROM magazins WHERE magazin_name='{product.value}'"
            product.value = self.__get_data(sql)[0][0]
        elif product.column == "category":
            sql = f"SELECT id FROM categories WHERE category_name='{product.value}'"
            product.value = self.__get_data(sql)[0][0]
        elif product.column == "raspr":
            if product.value == '':
                product.value = 1
            elif product.value == 'р':
                product.value = 2
        else:
            product.value = product.value.strip()
        sql = f"SELECT id FROM magazins WHERE magazin_name='{product.magazine}'"
        product.magazine = self.__get_data(sql)[0][0]
        sql = f"SELECT id FROM categories WHERE category_name='{product.category}'"
        product.category = self.__get_data(sql)[0][0]
        sql = "SELECT id FROM tovars ORDER BY id DESC LIMIT 1"
        if not self.__get_data(sql):
            product.id = 1
        else:
            product.id = self.__get_data(sql)[0][0] + 1
        sql = f"INSERT INTO tovars " \
              f"VALUES ({product.id},'{product.magazine}','{product.opisanie}'," \
              f"'{product.kod_tovara}','{product.tsena}','{product.razmery}'," \
              f"'{product.category}','{product.raspr}','{product.firm}')"
        self.__set_data(sql)
        self.status = f"добавление товара: {product}"
        logging.info(self.status)
        return product.id

    def update_product(self, product):
        """
        update record in table - set new data in cell
        :param product: Product extended two parameters: column - name of column in db
        and value - string for change cell
        """
        if product.column == "magazin":
            sql = f"SELECT id FROM magazins WHERE magazin_name='{product.value}'"
            product.value = self.__get_data(sql)[0][0]
        elif product.column == "category":
            sql = f"SELECT id FROM categories WHERE category_name='{product.value}'"
            product.value = self.__get_data(sql)[0][0]
        elif product.column == "raspr":
            if product.value == '':
                product.value = 1
            elif product.value == 'р':
                product.value = 2
        else:
            if product.value != "":
                product.value = product.value.strip()
        sql = f"UPDATE tovars SET {product.column}='{product.value}' " \
              f"WHERE id={product.id}"
        self.__set_data(sql)
        self.status = f"обновление товара: {product}, запись в поле:" \
                      f" {product.column} значения: {product.value}"
        logging.info(self.status)
        return self.status

    def update_magazine(self, magazine, old_name):
        sql = f"UPDATE magazins SET magazin_name='{magazine}' " \
              f"WHERE magazin_name='{old_name}'"
        self.__set_data(sql)
        self.status = f"обновление имени магазина: {old_name} на {magazine}"
        logging.info(self.status)
        return self.status

    def update_category(self, category, old_name):
        sql = f"UPDATE categories SET category_name='{category}' " \
              f"WHERE category_name='{old_name}'"
        self.__set_data(sql)
        self.status = f"обновление имени категории: {old_name} на {category}"
        logging.info(self.status)
        return self.status

    def del_from_table(self, table, id_in_table):
        """
        delete record from table in db
        after deleting checks db with method inspect() for deleting
        category and magazine if it is needed
        :param table: name of table
        :param id_in_table: id record in table
        """
        sql = f"DELETE FROM '{table}' WHERE id='{id_in_table}'"
        if table == "tovars":
            product = self.get_product(id_in_table)
        else:
            product = "not a product"
        self.__set_data(sql)
        if table == "tovars":
            self.status = f"удалено из таблицы: {table}, по id: {id_in_table}: {product}"
        else:
            self.status = f"удалено из таблицы: {table}, по id: {id_in_table}"
        logging.info(self.status)
        return self.status

    def inspect(self):
        """
        inspection of db for blank categories and magazines

        printing all categories and magazines which will be removed
        """
        self.status = "start inspect"
        logging.info(self.status)
        sql = "SELECT id FROM magazins"
        id_mags = self.__get_data(sql)
        ids = []
        for i in id_mags:
            ids.append(i[0])

        ids_mags_to_remove = []
        for id_mag in ids:
            sql = f"SELECT * FROM tovars WHERE magazin={id_mag}"
            prods = self.__get_data(sql)
            if len(prods) == 0:
                ids_mags_to_remove.append(id_mag)

        sql = "SELECT id FROM categories"
        id_cats = self.__get_data(sql)
        ids = []
        for i in id_cats:
            ids.append(i[0])
        ids_cats_to_remove = []
        for id_cat in ids:
            sql = f"SELECT * FROM tovars WHERE category={id_cat}"
            prods = self.__get_data(sql)
            if len(prods) == 0:
                ids_cats_to_remove.append(id_cat)

        sql = "SELECT * FROM cats_in_mags"
        cats_in_mags = self.__get_data(sql)
        cat_mags = []
        for cat_in_mag in cats_in_mags:
            cat_mag = CatsInMags(cat_in_mag)
            cat_mags.append(cat_mag)
        ids_catmag_to_remove = []
        for cat in cat_mags:
            sql = f"SELECT * FROM tovars " \
                  f"WHERE magazin='{cat.magazine}' AND category='{cat.category}'"
            prods = self.__get_data(sql)
            if len(prods) == 0:
                ids_catmag_to_remove.append(cat.id)

        for id_mag in ids_mags_to_remove:
            self.del_from_table("magazins", id_mag)
            self.status = f"магазин {id_mag} удален"
            logging.info(self.status)
            if len(self.get_magazines()) <= 1:
                self.new_db()
        else:
            self.status = "нечего удалять из магазинов"
            logging.info(self.status)

        for id_cat in ids_cats_to_remove:
            self.del_from_table("categories", id_cat)
            self.status = f"категория {id_cat} удалена"
            logging.info(self.status)
            if len(self.get_categories()) < 1:
                self.set_category(self.get_magazines()[0], "категория")
        else:
            self.status = "нечего удалять в категориях"
            logging.info(self.status)

        for id_catmag in ids_catmag_to_remove:
            self.del_from_table("cats_in_mags", id_catmag)
            self.status = f"категория в cat_in_mag {id_catmag} удалена"
            logging.info(self.status)
        else:
            self.status = "нечего удалять в cats_in_mags"
            logging.info(self.status)
        self.status = "проверка завершена"
        logging.info(self.status)
        return self.status

    def inspect_products(self):
        """
        check db for un stripped strings and blanked products

        printing all products which will be removed from db
        """
        self.status = "начало проверки товаров"
        logging.info(self.status)
        sql = "SELECT * FROM tovars"
        products = []
        for product in self.__get_data(sql):
            products.append(Product(product))

        for product in products:
            product.value = product.firm.strip()
            product.column = "firma"
            if product.firm != product.value:
                self.update_product(product)
            product.value = product.razmery.strip()
            product.column = "razmery"
            if product.razmery != product.value:
                self.update_product(product)
            product.value = product.tsena.strip()
            product.column = "tsena"
            if product.tsena != product.value:
                self.update_product(product)
            product.value = product.kod_tovara.strip()
            product.column = "kod_tovara"
            if product.kod_tovara != product.value:
                self.update_product(product)
            product.value = product.opisanie.strip()
            product.column = "opisanie"
            if product.opisanie != product.value:
                self.update_product(product)
        self.status = "очистка от пробелов в начале и конце записей в таблицах выполнена"
        logging.info(self.status)

        for product in products:
            if product.firm == product.kod_tovara == product.opisanie == product.razmery == \
                    product.tsena == "":
                self.del_from_table("tovars", product.id)
                self.status = f"удален товар: {product}"
                logging.info(self.status)
                continue
            if not isinstance(product.magazine, int):
                sql = f"SELECT id FROM magazins WHERE magazin_name='{product.magazine}'"
                magazine = self.__get_data(sql)[0][0]
                sql = f"UPDATE tovars SET magazin='{magazine}' WHERE id={product.id}"
                self.__set_data(sql)
            if not isinstance(product.category, int):
                sql = f"SELECT id FROM categories WHERE category_name='{product.category}'"
                category = self.__get_data(sql)[0][0]
                sql = f"UPDATE tovars SET category='{category}' WHERE id={product.id}"
                self.__set_data(sql)
            if not isinstance(product.raspr, int):
                if product.raspr == '':
                    raspr = 1
                elif product.raspr == 'р':
                    raspr = 2
                sql = f"UPDATE tovars SET raspr='{raspr}' WHERE id={product.id}"
                self.__set_data(sql)
        self.status = "удаление пустых товаров завершено"
        logging.info(self.status)
        return self.status

    def new_db(self):
        """create new database for program"""
        con = sqlite3.connect(configs.DB_NAME)
        cursor = con.cursor()

        def create_tables():
            """create all tables needed for program"""
            sql = "CREATE TABLE IF NOT EXISTS 'magazins' (" \
                  "id INTEGER NOT NULL " \
                  "    PRIMARY KEY AUTOINCREMENT " \
                  "    UNIQUE," \
                  "magazin_name TEXT)"
            self.__set_data(sql)
            sql = "CREATE TABLE IF NOT EXISTS 'raspr' (" \
                  "id INTEGER NOT NULL " \
                  "   PRIMARY KEY AUTOINCREMENT " \
                  "   UNIQUE," \
                  "raspr_flag TEXT)"
            self.__set_data(sql)
            sql = "CREATE TABLE IF NOT EXISTS 'categories' (" \
                  "id INTEGER NOT NULL " \
                  "   PRIMARY KEY AUTOINCREMENT " \
                  "   UNIQUE," \
                  "category_name TEXT)"
            self.__set_data(sql)
            sql = "CREATE TABLE IF NOT EXISTS 'cats_in_mags' (" \
                  "id INTEGER NOT NULL " \
                  "   PRIMARY KEY AUTOINCREMENT " \
                  "   UNIQUE," \
                  "mag_name INTEGER," \
                  "cat_name INTEGER)"
            self.__set_data(sql)
            sql = "CREATE TABLE IF NOT EXISTS 'tovars' (" \
                  "id INTEGER NOT NULL " \
                  "   PRIMARY KEY AUTOINCREMENT " \
                  "   UNIQUE," \
                  "magazin INTEGER," \
                  "opisanie TEXT," \
                  "kod_tovara TEXT," \
                  "tsena TEXT," \
                  "razmery TEXT," \
                  "category INTEGER," \
                  "raspr INTEGER," \
                  "firma TEXT)"
            self.__set_data(sql)
            db_handler = DbHandler()
            db_handler.set_magazine("магазин")
            db_handler.set_category("магазин", "категория")
            sql = "INSERT INTO raspr (raspr_flag) values (''),('р')"
            db_handler.cursor.execute(sql)
            db_handler.con.commit()

        create_tables()
