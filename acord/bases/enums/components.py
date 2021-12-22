from enum import IntEnum


class ComponentTypes(IntEnum):
    ACTION_ROW = 1
    BUTTON = 2
    SELECT_MENU = 3


class ButtonStyles(IntEnum):
    PRIMARY = 1
    """ Blurple """
    SECONDARY = 2
    """ Grey """
    SUCESS = 3
    """ Green """
    DANGER = 4
    """ Red """
    LINK = 5
    """ Grey, navigates to URL """
