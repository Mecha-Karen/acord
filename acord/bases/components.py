from __future__ import annotations
from typing import Any, List, Optional
import pydantic

from acord.bases import ComponentTypes, ButtonStyles, TextInputStyle


class Component(pydantic.BaseModel):
    type: ComponentTypes
    """ Type of component """
    custom_id: Optional[str]
    """ Custom ID of component cannot be greater then 100 chars """

    @classmethod
    def from_data(cls, data) -> Component:
        if data["type"] == ComponentTypes.BUTTON:
            return Button(**data)
        if data["type"] == ComponentTypes.SELECT_MENU:
            return SelectMenu(**data)
        return cls(**data)


class SelectOption(pydantic.BaseModel):
    label: str
    """ the user-facing name of the option, max 100 characters """
    value: str
    """ the dev-define value of the option, max 100 characters """
    description: str
    """ an additional description of the option, max 100 characters """
    emoji: Optional[Any]
    """ an emoji to display next to the label """
    default: Optional[bool]
    """ will render this option as selected by default """


class ActionRow(Component):
    components: List[Component]
    """ List of components to add to row """
    disabled: Optional[bool] = False
    """ Whether component is disabled """

    @pydantic.validator("components")
    def _validate_lengths(cls, components) -> List[Component]:
        if len(components) > 1 and components[0].type == ComponentTypes.TEXT_INPUT:
            raise ValueError("Modal can only contain 1 text input per row")

        if any(i for i in components if isinstance(i, ActionRow)):
            raise ValueError("Action row cannot contain another action row")

        if not all(i for i in components if isinstance(i, Button)):
            raise ValueError("Action row cannot contain both buttons and select menu")

        if len(components) > 5:
            raise ValueError("Action Row cannot contain more then 5 components")

        return components

    def __init__(self, *components, **data: Any) -> None:
        data.update({"type": ComponentTypes.ACTION_ROW})

        existing = data.get("components", list())
        existing.extend(components)

        if not existing and self.__class__.__fields__["components"].default is not None:
            existing = self.__class__.__fields__["components"].default

        data["components"] = existing

        super().__init__(**data)

    @pydantic.validate_arguments
    def add_component(self, component: Component) -> None:
        """|func|

        Adds a component to your row

        Parameters
        ----------
        component: :class:`Component`
            Component to add to row
        """
        self.components.append(component)


class Button(Component):
    style: ButtonStyles
    """ Style of button """
    label: Optional[str]
    """ Button label, must be less then 80 chars """
    emoji: Optional[Any]
    """ A partial emoji object """
    url: Optional[pydantic.AnyHttpUrl]
    """ URL for link style buttons """
    disabled: Optional[bool] = False
    """ Whether component is disabled """

    @pydantic.validator("label")
    def _validate_label(cls, label):
        if len(label) > 80:
            raise ValueError("label must be less then 80 characters")
        return label

    def __init__(self, **data: Any) -> None:
        data.update({"type": ComponentTypes.BUTTON})

        super().__init__(**data)


class SelectMenu(Component):
    options: List[SelectOption]
    """ List of options """
    placeholder: Optional[str]
    """ Custom placeholder if nothing is selected """
    min_values: Optional[int]
    """ Minimum values of selected items """
    max_values: Optional[int]
    """ Max values of selected items """
    disabled: Optional[bool] = False
    """ Whether component is disabled """

    @pydantic.validator("options")
    def _validate_options(cls, options):
        if len(options) > 25:
            raise ValueError("Select menu cannot have more then 25 options")

        return options

    @pydantic.validator("placeholder")
    def _validate_placeholder(cls, ph):
        if len(ph) > 100:
            raise ValueError("Placeholder cannot be greater then 100 chars")

        return ph

    @pydantic.validator("min_values", "max_values")
    def _validate_mv(cls, v):
        assert 0 <= v <= 25, "Value must be less then 25 and greater then 0"

        return v

    def __init__(self, **data: Any) -> None:
        data.update({"type": ComponentTypes.SELECT_MENU})

        super().__init__(**data)

    @pydantic.validate_arguments
    def add_option(self, option: SelectOption) -> None:
        """|func|

        Adds an option to the select menu

        Parameters
        ----------
        option: :class:`SelectOption`
            New select option to add to menu
        """
        if (len(self.options) + 1) > 25:
            raise ValueError("Select menu cannot have more then 25 options")

        self.options.append(option)


class TextInput(Component):
    style: TextInputStyle
    """ text input style """
    label: str
    """ label for input """
    min_length: Optional[int]
    """ minimum length for input, 0-4000 """
    max_length: Optional[int]
    """ maximum length for input, 0-4000 """
    required: Optional[bool] = False
    """ Whether this component is required to be filled """
    value: Optional[str]
    """ pre-filled value for input """
    placeholder: Optional[str]
    """ Custom placeholder if input is empty, 0-100 """

    def __init__(self, **data: Any) -> None:
        data.update({"type": ComponentTypes.TEXT_INPUT})

        super().__init__(**data)

    @pydantic.validator("min_length", "max_length")
    def _validate_lengths(cls, v) -> int:
        assert 0 <= v <= 4000, "Lengths must be >= 0 but <= 4000"
        return v

    @pydantic.validator("placeholder")
    def _validate_placeholder(cls, v) -> str:
        assert len(v) <= 100, "Placeholder must be less then 100 chars"
        return v


class Modal(pydantic.BaseModel):
    title: str
    """ Title of modal """
    custom_id: str
    """ custom ID of the modal """
    components: List[ActionRow]
    """ List of action rows

    .. note::
        As of 13/02/2022, discord only allows :class:`TextInput` in the action row
    """

    @pydantic.validator("components")
    def _validate_components(cls, v):
        assert all(
            i for i in v if all(j for j in i.components if j.__class__ == TextInput)
        ), "Modal can only contain text inputs!"
        return v
