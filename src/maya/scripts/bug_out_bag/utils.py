import sys


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


def print_var(*vs):
    for v in vs:
        __print_var_aux(v)


def __print_var_aux(v, tabs=0, v_in_dict=False):
    tabulation = "`\t"
    if type(v) is dict:
        if v_in_dict : print("")
        if len(v) == 0 : print("{}")
        else:
            print(tabs * tabulation + "{")
            for key, elems in v.items():
                print((tabs + 1) * tabulation + __get_val(key) + " : ", end="")
                __print_var_aux(elems,tabs + 1, True)
            print(tabs * tabulation + "}")
    elif type(v) is list or type(v) is tuple:
        if len(v) == 0 : print("[]")
        else:
            if v_in_dict : print("")
            print(tabs * tabulation + "[")
            for elem_list in v:
                __print_var_aux(elem_list,tabs + 1, False)
            print(tabs * tabulation + "]")
    else:

        tabs_str = "" if v_in_dict else tabs * tabulation
        try:
            print(tabs_str + __get_val(v))
        except:
            print(tabs_str + "Unknown value")
