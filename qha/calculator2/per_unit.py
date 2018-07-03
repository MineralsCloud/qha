from scipy.constants import physical_constants

FORMULA_UNIT_PER_MOLE = physical_constants['Avogadro constant'][0]

class PerFormulaUnit:
    def __init__(self, item):
        self.item = item
    def __getattr__(self, prop):
        item_attr = getattr(self.item, prop)
        if callable(item_attr):
            def wrapper(*argv, **kwargs):
                return item_attr(*argv, **kwargs) / self.item.formula_unit_number
            return wrapper
        else:
            return item_attr / self.item.formula_unit_number

class PerMole:
    def __init__(self, item):
        self.item = item
    def __getattr__(self, prop):
        item_attr = getattr(self.item, prop)
        if callable(item_attr):
            def wrapper(*argv, **kwargs):
                return item_attr(*argv, **kwargs) / self.item.formula_unit_number * float(FORMULA_UNIT_PER_MOLE)
            return wrapper
        else:
            return item_attr / self.item.formula_unit_number * float(FORMULA_UNIT_PER_MOLE)

