import math
import sys
from pymel.core import *


# Clear a layout recusrively
def clear_layout(layout):
    children = []
    for i in range(layout.count()):
        child = layout.itemAt(i).widget()
        if not child:
            clear_layout(layout.itemAt(i).layout())
        else:
            children.append(child)
    for child in children:
        child.deleteLater()


def unload_packages(silent=True, packages=None):
    if packages is None:
        packages = []

    # construct reload list
    reload_list = []
    for i in sys.modules.keys():
        for package in packages:
            if i.startswith(package):
                reload_list.append(i)

    # unload everything
    for i in reload_list:
        try:
            if sys.modules[i] is not None:
                del (sys.modules[i])
                if not silent:
                    print("Unloaded: %s" % i)
        except:
            pass


def __get_val(v):
    if type(v) is str:
        return "\"" + v + "\""
    else:
        return str(v)


def print_var(*vs, empty_tab=False):
    vs = vs[0] if len(vs) == 1 else vs
    tabulation = "\t" if empty_tab else "`\t"
    __print_var_aux(vs, tabulation)


def __print_var_aux(v, tabulation, tabs=0, v_in_dict=False):
    if type(v) is dict:
        if v_in_dict: print("")
        if len(v) == 0:
            print("{}")
        else:
            print(tabs * tabulation + "{")
            for key, elems in v.items():
                print((tabs + 1) * tabulation + __get_val(key) + " : ", end="")
                __print_var_aux(elems, tabulation, tabs + 1, True)
            print(tabs * tabulation + "}")
    elif type(v) is list or type(v) is tuple:
        if type(v) is list:
            char_start = "["
            char_end = "]"
        else:
            char_start = "("
            char_end = ")"
        if len(v) == 0:
            print(char_start + char_end)
        else:
            if v_in_dict: print("")
            print(tabs * tabulation + char_start)
            for elem_list in v:
                __print_var_aux(elem_list, tabulation, tabs + 1, False)
            print(tabs * tabulation + char_end)
    else:

        tabs_str = "" if v_in_dict else tabs * tabulation
        try:
            print(tabs_str + __get_val(v))
        except:
            print(tabs_str + "Unknown value")


def print_warning(msg, char_filler='-'):
    if type(msg) is not list and type(msg) is not tuple:
        msg = [msg]

    max_len_msg_line = 0
    for m in msg:
        max_len_msg_line = max(max_len_msg_line, len(m))
    warning_filler = char_filler * int(2 * max_len_msg_line / 3 - 5 / 2)
    warning_msg = warning_filler + " /!\\ " + warning_filler
    warning(warning_msg)
    for m in msg:
        float_length = (len(warning_msg) - len(m)) / 2
        warning_space_filler = ' ' * int(float_length)
        warning_space_filler2 = ' ' * math.ceil(float_length)
        warning(warning_space_filler + m + warning_space_filler2)
    warning(warning_msg)
