from abc import *


class BobElement(ABC):
    def __init__(self, name):
        """
        Constructor
        :param name
        """
        self._name = name
        self._layout = None

    def get_name(self):
        """
        Getter of the name
        :return: name
        """
        return self._name

    @abstractmethod
    def populate(self):
        """
        Populate the UI
        :return:
        """
        pass

    @abstractmethod
    def on_selection_changed(self):
        """
        Event on selection changed
        :return:
        """
        pass

    @abstractmethod
    def on_dag_changed(self):
        """
        Event on dag changed
        :return:
        """
        pass
