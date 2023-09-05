from PySide2 import QtWidgets, QtGui, QtCore

class Header(QtWidgets.QWidget):
    """Header class for collapsible group"""

    def __init__(self, name, content_widget,pref_name, prefs,  bg_color, margins):
        """
        Constructor
        :param name: Name for the header
        :param content_widget: Widget containing child elements
        :param pref_name
        :param prefs
        :param bg_color: Color of the background
        :param margins
        """
        super(Header, self).__init__()
        self.pref_name = pref_name
        self.prefs = prefs
        self.content = content_widget
        self.expand_ico = QtGui.QPixmap(":teDownArrow.png")
        self.collapse_ico = QtGui.QPixmap(":teRightArrow.png")

        stacked = QtWidgets.QStackedLayout(self)
        stacked.setStackingMode(QtWidgets.QStackedLayout.StackAll)
        background = QtWidgets.QLabel()
        background.setStyleSheet(".QLabel{background-color: "+bg_color+"; border-radius:0px}")

        widget = QtWidgets.QWidget()
        widget.setStyleSheet("margin-left: "+str(margins[0])+"px;"+
                             "margin-top: "+str(margins[1])+"px;"+
                             "margin-right: "+str(margins[2])+"px;"+
                             "margin-bottom: "+str(margins[3])+"px;")
        layout = QtWidgets.QHBoxLayout(widget)

        self.icon = QtWidgets.QLabel()
        self.icon.setPixmap(self.expand_ico)
        layout.addWidget(self.icon)
        layout.setContentsMargins(10, 0, 10, 0)

        font = QtGui.QFont()
        font.setBold(True)
        label = QtWidgets.QLabel(name)
        label.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Minimum)
        label.setFont(font)

        layout.addWidget(label)

        stacked.addWidget(widget)
        stacked.addWidget(background)
        background.setMinimumHeight(layout.sizeHint().height() * 1.4)

        if self.pref_name in self.prefs:
            pref = self.prefs[self.pref_name]
            if "collapsed" in pref and pref["collapsed"]:
                self.collapse()

    def mousePressEvent(self, *args):
        """
        Handle mouse events, call the function to toggle groups
        :param args
        :return:
        """
        self.expand() if not self.content.isVisible() else self.collapse()

    def expand(self):
        """
        Expand the collapsible widget in the UI
        :return:
        """
        self.content.setVisible(True)
        self.icon.setPixmap(self.expand_ico)
        pref = self.prefs[self.pref_name] if self.pref_name in self.prefs else {}
        pref["collapsed"] = False
        self.prefs[self.pref_name] = pref

    def collapse(self):
        """
        Collapse the collapsible widget in the UI
        :return:
        """
        self.content.setVisible(False)
        self.icon.setPixmap(self.collapse_ico)
        pref = self.prefs[self.pref_name] if self.pref_name in self.prefs else {}
        pref["collapsed"] = True
        self.prefs[self.pref_name] = pref


class BobCollapsibleWidget(QtWidgets.QWidget):
    """Class for creating a collapsible group similar to how it is implement in Maya
        Examples:
            Simple example of how to add a CollapsibleLayout to a QVBoxLayout and attach a QGridLayout
            >>> layout = QtWidgets.QVBoxLayout()
            >>> container = BobCollapsibleWidget("Group")
            >>> layout.addWidget(container)
            >>> content_layout = QtWidgets.QGridLayout(container.contentWidget)
            >>> content_layout.addWidget(QtWidgets.QPushButton("Button"))
    """

    def __init__(self, name,pref_name,  prefs, bg_color="rgb(60, 60, 60)", widget_color="rgb(93, 93, 93)", margins=None):
        """
        Constructor
        :param name: Name for the header
        :param pref_name
        :param prefs
        :param bg_color
        :param widget_color
        :param margins
        """
        super(BobCollapsibleWidget, self).__init__()
        if margins is None:
            margins = [8, 0, 0, 0]

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self._content_widget = QtWidgets.QWidget()
        self._content_widget.setStyleSheet(".QWidget{background-color: "+bg_color+";border-radius:0px;}")
        self.setStyleSheet(".QWidget{background-color: "+widget_color+";border-radius:5px}")
        header = Header(name, self._content_widget,pref_name, prefs, bg_color,margins)
        layout.addWidget(header)
        layout.addWidget(self._content_widget)

        # assign header methods to instance attributes so they can be called outside of this class
        self.collapse = header.collapse
        self.expand = header.expand
        self.toggle = header.mousePressEvent

    @property
    def contentWidget(self):
        """
        Getter for the content widget
        Returns: Content widget
        """
        return self._content_widget
