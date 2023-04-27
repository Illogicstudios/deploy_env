import json
import base64
import os.path

import pymel.core as pm
from common.utils import *
from .Preset import *


class PresetManager:
    # ################################################### Singleton ####################################################
    __instance = None

    # Getter of the instance for the Singleton pattern
    @staticmethod
    def get_instance():
        if PresetManager.__instance is None:
            PresetManager.__instance = PresetManager()
            PresetManager.__instance.retrieve_presets()
            PresetManager.__instance.retrieve_default_presets()
        return PresetManager.__instance

    # ################################################### Singleton ####################################################

    def __init__(self):
        self.__presets = []
        self.__default_presets = []
        self.__active_preset = None

    # Clear the presets
    def clear(self):
        self.__presets.clear()
        self.__active_preset = None

    # Add a preset
    def add_preset(self, preset_to_add):
        to_remove = None
        for preset in self.__presets:
            if preset.get_name() == preset_to_add.get_name():
                to_remove = preset
                break
        if to_remove is not None:
            self.remove_preset(to_remove)
        if preset_to_add.is_active():
            for curr_preset in self.__presets:
                curr_preset.set_active(False)

        if preset_to_add not in self.__presets:
            self.__presets.append(preset_to_add)

    # Remove a preset
    def remove_preset(self, preset_to_remove):
        if preset_to_remove is not None:
            self.__presets.remove(preset_to_remove)

    # Setter of the active state of a preset
    def set_preset_active(self, active_preset):
        # Set all presets to inactive except the wanted one
        if active_preset is not None:
            for preset in self.__presets:
                preset.set_active(preset is active_preset)

    # Retrieve the existing presets in the scene
    def retrieve_presets(self):
        self.clear()
        if "presets" in pm.fileInfo:
            found_active = False
            json_presets = pm.fileInfo["presets"].replace("\\\"", "\"")
            try:
                arr_json_presets = json.loads(json_presets)
                for json_preset in arr_json_presets:
                    preset = Preset.create_from_existant(json_preset)
                    if preset.is_active() and not found_active:
                        self.__active_preset = preset
                    self.__presets.append(preset)
            except:
                print_warning("Error while trying to parse an existing preset")

    # Save presets in the scene
    def save_presets(self):
        arr_json_presets = []
        for preset in self.__presets:
            arr_json_presets.append(preset.to_preset_array())
        pm.fileInfo["presets"] = json.dumps(arr_json_presets)

    # Getter of the presets
    def get_presets(self):
        self.__presets.sort(key=lambda x: x.get_name())
        return self.__presets

    # Getter of the default presets
    def get_default_presets(self):
        return self.__default_presets

    # Retrieve all the default presets
    def retrieve_default_presets(self):
        self.__default_presets = []
        default_preset_dir = os.path.join(os.path.dirname(__file__), "default_preset")
        for preset_filename in os.listdir(default_preset_dir):
            preset_path = os.path.join(default_preset_dir, preset_filename)
            try:
                if os.path.isfile(preset_path):
                    with open(preset_path, "r") as f:
                        preset_json = f.read().replace("\\\"", "\"").replace("\\n", "")
                        self.__default_presets.append(Preset.create_from_existant(json.loads(preset_json)))
            except:
                print_warning("Error while trying to parse a default preset : "+preset_path)


    # Getter of whether a preset exist with a given name
    def has_preset_with_name(self, name):
        for preset in self.__presets:
            if preset.get_name() == name:
                return True
