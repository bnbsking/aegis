from collections import OrderedDict


val_type = str | bool | None
"""
cache for deid classes, value can be
    str (deid_text)
    bool (deid_passed)
    None (not in cache)
"""


class LRUCache:
    def __init__(self, capacity: int):
        self.cap = capacity
        self.O = OrderedDict()

    def get(self, key: str) -> val_type:
        if key in self.O:
            self.O.move_to_end(key)
            return self.O[key]
        return None
    
    def put(self, key: str, value: val_type) -> None:
        if key not in self.O and len(self.O) == self.cap:
            self.O.popitem(last=False)
        self.O[key] = value
        self.O.move_to_end(key)
