import itertools


class ChannelsProperty:
    def __init__(self, items):
        self.description = "Space-separated list of channels"
        self.required = True

        self.channels = []
        self.add(items.split())

    def add(self, first, *channels):
        self.channels.extend(itertools.chain((first,), channels))

    def remove(self, channel):
        self.channels.remove(channel)

    def __iter__(self):
        return iter(self.channels)


class BindProperty:
    def __init__(self, value=None):
        self.description = "Hostname or IP address to listen on"
        self.value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value

    @property
    def required(self):
        return self.__required

    @required.setter
    def required(self, required):
        self.__required = required
