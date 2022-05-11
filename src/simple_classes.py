"""
simple classes for converting data from db to specify class

classes:
    Category
    CatsInMags
    Magazine
    Product
    Raspr
"""


class Category:
    """
    class defines objects for categories in table categories in db
    """
    def __init__(self, category):
        (self.id, self.category) = category

    def __str__(self):
        return self.category

    def __eq__(self, other):
        return self.category == other.category


class CatsInMags:
    """
    class defines objects for categories in magazines in table cats_in_mags in db
    """
    def __init__(self, cats_in_mags):
        (self.id, self.magazine, self.category) = cats_in_mags

    def __str__(self):
        return f"{self.magazine} {self.category}"

    def __eq__(self, other):
        return f"{self.magazine} {self.category}" == f"{other.magazine} {other.category}"


class Magazine:
    """
    class defines objects for magazines in table magazins in db
    """
    def __init__(self, magazine):
        (self.id, self.magazine) = magazine

    def __str__(self):
        return self.magazine

    def __eq__(self, other):
        return self.magazine == other.magazine


class Product:
    """
    class defines object for product in table tovars in db
    """
    def __init__(self, product: tuple = None):
        if product is None:
            self.id = self.magazine = self.opisanie = self.kod_tovara = self.tsena = \
                self.razmery = self.category = self.raspr = self.firm = None
        else:
            (self.id, self.magazine, self.opisanie, self.kod_tovara,
             self.tsena, self.razmery, self.category, self.raspr, self.firm) = product

    def __str__(self):
        return f"{self.magazine},{self.opisanie},{self.kod_tovara},{self.tsena},{self.razmery}," \
               f"{self.category},{self.raspr},{self.firm}"

    def __eq__(self, other):
        return f"{self.magazine},{self.opisanie},{self.kod_tovara},{self.tsena},{self.razmery}," \
               f"{self.category},{self.raspr},{self.firm}" == \
               f"{other.magazine},{other.opisanie},{other.kod_tovara},{other.tsena},{other.razmery}," \
               f"{other.category},{other.raspr},{other.firm}"


class Raspr:
    """
    class defines object for raspr in table raspr in db
    """
    def __init__(self, raspr):
        (self.id, self.raspr) = raspr

    def __str__(self):
        return self.raspr