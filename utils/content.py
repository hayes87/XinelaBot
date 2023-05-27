import secrets
from utils.sheet import Sheet


class Content:
    def __init__(self):
        self._sheet = Sheet('1NRhDtTA6CVb6JHFUoSUVtEg3H12o-MUE7c4n3dre9xw')
        self._content = {
            "horarios": self._sheet.get_column_values(1),
            "abertura_frases": self._sheet.get_column_values(2),
            "abertura_imagens": self._sheet.get_column_values(3),
            "naodeu_frases": self._sheet.get_column_values(6),
            "naodeu_imagens": self._sheet.get_column_values(7),
            "anuncio": self._sheet.eval_get_column_values(9),
        }

    def get(self, key):
        return self._content.get(key, None)

    def get_random(self, key):
        content = self._content.get(key, None)
        print(content)
        if content is not None:
            return secrets.choice(self._content[key])
