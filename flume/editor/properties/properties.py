import itertools
import sys


class Property(object):
    def __init__(self, name, *items, value=None):
        self.name = name
        self.value = value
        self.children = []
        if items:
            self.add(*items)

    @classmethod
    def create(cls, name, value):
        return Property(name, value=value)

    @classmethod
    def compose(cls, name, *items):
        return Property(name, *items)

    def make_item(self, value):
        return Property(self, value=value)

    def make_composite(self, *items):
        return Property(self, *items)

    @property
    def composite(self):
        return bool(self.children)

    def add(self, first, *items):
        self.children.extend(itertools.chain((first,), items))

    def remove(self, item):
        self.children.remove(item)

    def __iter__(self):
        return iter(self.children)

    @property
    def value(self):
        return ", ".join(item.value for item in self) if self.children else self.__value

    @value.setter
    def value(self, value):
        self.__value = value

    def print(self, indent="", file=sys.stdout):
        print("{}${:.2f} {}".format(indent, self.value, self.name),
              file=file)
        for child in self:
            child.print(indent + "       ")


class ChannelsProperty(Property):
    def __init__(self, name, *items, value=None):
        super().__init__(name, *items, value=value)

