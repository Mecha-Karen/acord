from enum import IntEnum


class ComponentTypes(IntEnum):
    ACTION_ROW = 1
    BUTTON = 2
    SELECT_MENU = 3
    TEXT_INPUT = 4


class ButtonStyles(IntEnum):
    PRIMARY = 1
    """ Blurple """
    SECONDARY = 2
    """ Grey """
    SUCCESS = 3
    """ Green """
    DANGER = 4
    """ Red """
    LINK = 5
    """ Grey, navigates to URL """


class TextInputStyle(IntEnum):
    SHORT = 1
    """ Single line inputs """
    PARAGRAPH = 2
    """ Multi line inputs """
