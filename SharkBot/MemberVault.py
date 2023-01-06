import SharkBot

class _Items:

    def __init__(self, items: list[str]):
        self._items: list[SharkBot.Item.Item] = [SharkBot.Item.get(item_id) for item_id in items]

    def __iter__(self):
        return (item for item in self._items)

    def __contains__(self, item):
        return item in self._items

    def add(self, *items: SharkBot.Item.Item):
        self._items += items

    def remove(self, *items: SharkBot.Item.Item):
        _items = self._items
        try:
            for item in items:
                _items.remove(item)
        except ValueError:
            raise SharkBot.Errors.ItemNotInVaultError(items)
        finally:
            self._items = _items

    @property
    def data(self) -> list[str]:
        return list(item.id for item in self._items)

class _Auto:

    def __init__(self, items: list[str]):
        self._items: set[SharkBot.Item.Item] = {SharkBot.Item.get(item_id) for item_id in items}

    def __iter__(self):
        return (item for item in self._items)

    def __contains__(self, item):
        return item in self._items

    def add(self, *items: SharkBot.Item.Item):
        self._items.update(items)

    def remove(self, *items: SharkBot.Item.Item):
        _items = self._items
        try:
            for item in items:
                _items.remove(item)
        except KeyError:
            raise SharkBot.Errors.ItemNotInVaultError(items)
        finally:
            self._items = _items

    @property
    def data(self) -> list[str]:
        return list(item.id for item in self._items)

class MemberVault:

    def __init__(self, items: list[str], auto: list[str]):
        self.items = _Items(items)
        self.auto = _Auto(auto)

    def __contains__(self, item):
        return item in self.items

    def add(self, *items: SharkBot.Item.Item):
        self.items.add(*items)

    def remove(self, *items: SharkBot.Item.Item):
        self.items.remove(*items)

    @property
    def data(self) -> dict[str, list[str]]:
        return {
            "items": self.items.data,
            "auto": self.auto.data
        }