import os.path
import unittest

from src import DbHandler, Product, Category, Magazine
from src.settings import configs


class DbHandlerTestCase(unittest.TestCase):
    def setUp(self):
        configs.DB_NAME = "source/base.db"
        if os.path.exists(configs.DB_NAME):
            os.remove(configs.DB_NAME)
        DbHandler().new_db()
        self.db_handler = DbHandler()

    def test_created_db(self):
        self.assertEqual("магазин", self.db_handler.get_magazines()[0].magazine)
        self.assertEqual("категория", self.db_handler.get_categories()[0].category)

    def test_set_category(self):
        self.db_handler.set_category("магазин", "категория2")
        self.assertIn(Category((1, "категория2")), self.db_handler.get_categories())

    def test_set_magazine(self):
        self.db_handler.set_magazine("магазин2")
        self.assertIn(Magazine((1, "магазин2")), self.db_handler.get_magazines())

    def test_insert_product(self):
        product = Product((0, "магазин", "opisanie", "kod_tovara", "tsena",
                           "razmery", "категория", 1, "firm"))
        product.column = ''
        product.value = ''
        prod_id = self.db_handler.insert_product(product)
        product = self.db_handler.get_product(prod_id)
        products = self.db_handler.get_products()
        self.assertIn(product, products)

    def test_update_product(self):
        product = Product((0, "магазин", "opisanie", "kod_tovara", "tsena",
                           "razmery", "категория", 1, "firm"))
        product.column = ""
        product.value = ""
        id_prod = self.db_handler.insert_product(product)
        old_prod = self.db_handler.get_product(id_prod)
        product.column = "opisanie"
        product.value = "opisanie1"
        self.db_handler.update_product(product)
        new_prod = self.db_handler.get_product(id_prod)
        self.assertNotEqual((old_prod.id, old_prod.magazine, old_prod.opisanie, old_prod.kod_tovara,
                             old_prod.tsena, old_prod.razmery, old_prod.category, old_prod.raspr, old_prod.firm),
                            (new_prod.id, new_prod.magazine, new_prod.opisanie, new_prod.kod_tovara,
                             new_prod.tsena, new_prod.razmery, new_prod.category, new_prod.raspr, new_prod.firm))

    def test_update_magazine(self):
        old_magazine = self.db_handler.get_magazines()[0]
        self.db_handler.update_magazine("magazine", old_magazine)
        new_magazine = self.db_handler.get_magazines()[0]
        self.assertNotEqual(old_magazine.magazine, new_magazine.magazine)

    def test_update_category(self):
        old_category = self.db_handler.get_categories()[0]
        self.db_handler.update_category("category", old_category)
        new_category = self.db_handler.get_categories()[0]
        self.assertNotEqual(old_category.category, new_category.category)

    def test_del_from_table(self):
        self.db_handler.del_from_table("magazines", 2)
        self.assertNotIn(Magazine((1, "магазин2")), self.db_handler.get_magazines())
        self.db_handler.del_from_table("categories", 2)
        self.assertNotIn(Category((1, "категория2")), self.db_handler.get_categories())

    def tearDown(self):
        os.remove(configs.DB_NAME)


if __name__ == '__main__':
    unittest.main()
