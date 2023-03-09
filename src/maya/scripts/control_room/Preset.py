from utils import *


class Preset:

    # Create a preset from a preset_dict retrieved
    @classmethod
    def create_from_existant(cls, preset_dict):
        name = preset_dict["name"]
        del preset_dict["name"]
        if "active" in preset_dict:
            active = preset_dict["active"]
            del preset_dict["active"]
        else:
            active = False
        return cls(name, preset_dict, active)

    def __init__(self, name, fields=None, active=False):
        self.__name = name.replace(" ", "_")
        self.__fields = {} if fields is None or type(fields) is not dict else fields
        self.__active = active

    # ###################################################### dict ######################################################

    # Set an attribute
    def set(self, part_name, key, value):
        if part_name not in self.__fields:
            self.__fields[part_name] = {}
        self.__fields[part_name][key] = value

    # Get an attribute
    def get(self, part_name, key):
        if part_name not in self.__fields or key not in self.__fields[part_name]:
            return None
        return self.__fields[part_name][key]

    # Getter of the keys
    def keys(self):
        return self.__fields.keys()

    # Getter of the values
    def values(self):
        return self.__fields.values()

    # Getter of the items
    def items(self):
        return self.__fields.items()

    # ###################################################### dict ######################################################

    # Equals function
    def __eq__(self, other):
        return other.__name == self.__name

    # Setter of the active state
    def set_active(self, active):
        self.__active = active

    # Getter of the active state
    def is_active(self):
        return self.__active

    # Getter of the name
    def get_name(self):
        return self.__name

    # Setter of the name
    def set_name(self, name):
        self.__name = name

    # Generate an array from the preset
    def to_preset_array(self):
        preset_dict = self.__fields.copy()
        preset_dict["name"] = self.__name
        preset_dict["active"] = self.__active
        return preset_dict
