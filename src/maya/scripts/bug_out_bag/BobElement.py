from abc import *


class BobElement(ABC):
    def __init__(self, name):
        self._name = name
        self._layout = None

    def get_name(self):
        return self._name

    @abstractmethod
    def populate(self):
        pass

    @abstractmethod
    def on_selection_changed(self):
        pass

    @abstractmethod
    def on_dag_changed(self):
        pass
