.. meta::
   :title: Documentation - Acord [Models]
   :type: website
   :url: https://acord.readthedocs.io/api/models.html
   :description: All the models created to simplify interactions with the discord API
   :theme-color: #f54646

.. currentmodule:: acord

******
Models
******
Our models use the ``Pydantic`` module for simple data parsing. 
All methods from :class:`~pydantic.BaseModel` are inherited along with ours.
These methods will not be shown in our docs, 
you can find them in the ``Pydantic`` documentation.

.. comment:
   The reason the if is not indented is due to jinja keeping it indented
   This leads to sphinx not recognising the headers which is painful

{% for object in dir(acord.models) %}
   {% set cls = getattr(acord.models, object, None) %}
   {% set cls_name = getattr(cls, "__name__", "") %}

   {% if cls is callable and cls_name not in disallow %}
{{ cls_name }}
{{ "=" * cls_name|length() }}

.. attributetable:: acord.models.{{ cls_name }}

.. autoclass:: acord.models.{{ cls_name }}
   :members:

   {% endif %}
{% endfor %}