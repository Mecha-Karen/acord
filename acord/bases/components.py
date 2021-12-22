from __future__ import annotations
from typing import Any, List, Optional
import pydantic

from acord.bases import ComponentTypes, ButtonStyles


class Component(pydantic.BaseModel):
    type: ComponentTypes
    """ Type of component """
    custom_id: Optional[str]
    """ Custom ID of component cannot be greater then 100 chars """
    disabled: Optional[bool] = False
    """ Whether component is disabled """


class SelectOption(pydantic.BaseModel):
    label: str
    """ the user-facing name of the option, max 100 characters """
    value: str
    """ the dev-define value of the option, max 100 characters """
    description: str
    """ an additional description of the option, max 100 characters """
    emoji: Optional[Any]
    """ an emoji to dispay next to the label """
    default: Optional[bool]
    """ will render this option as selected by default """


class ActionRow(Component):
    components: List[Component]

    @pydantic.validator('components')
    def _validate_lengths(cls, components) -> List[Component]:
        if any(i for i in components if isinstance(i, ActionRow)):
            raise ValueError('Action row cannot contain another action row')

        if len(components) > 5:
            raise ValueError('Action Row cannot contain more then 5 components')

        return components

    def __init__(self, *components, **data: Any) -> None:
        data.update({'type': ComponentTypes.ACTION_ROW})

        existing = data.get("components", list())
        existing.extend(components)

        data['components'] = existing

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

    def __init__(self, **data: Any) -> None:
        data.update({'type': ComponentTypes.BUTTON})

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

    @pydantic.validator("options")
    def _validate_options(cls, options):
        if len(options) > 25:
            raise ValueError('Select menu cannot have more then 25 options')

        return options

    @pydantic.validator("placeholder")
    def _validate_placeholder(cls, ph):
        if len(ph) > 100:
            raise ValueError('Placeholder cannot be greater then 100 chars')

        return ph

    @pydantic.validator("min_values", "max_values")
    def _validate_mv(cls, **kwargs):
        min_value = kwargs['values']['min_values']
        max_value = kwargs['values']['max_value']

        assert 0 <= min_value <= 25, "Min value must be less then 25 and greater then 0"
        assert 0 <= max_value <= 25, "Max value must be less then 25 and greater then 0"

        return (min_value or 0), (max_value or 0)

    def __init__(self, **data: Any) -> None:
        data.update({'type': ComponentTypes.SELECT_MENU})

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
            raise ValueError('Select menu cannot have more then 25 options')

        self.options.append(option)
