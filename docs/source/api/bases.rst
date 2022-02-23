.. meta::
   :title: Documentation - Acord [Bases]
   :type: website
   :url: https://acord.readthedocs.io/api/bases.html
   :description: All objects used for the discord API
   :theme-color: #f54646

.. currentmodule:: acord

*****
Bases
*****
Bases are objects which represent different objects in the discord API.
They minify the code written and can help improve readability in your code!


{% for object in dir(acord.bases) %}
   {% set cls = getattr(acord.bases, object, None) %}
   {% set cls_name = getattr(cls, "__name__", "") %}

   {% if cls is callable and cls_name not in disallow %}
{{ cls_name }}
{{ "=" * cls_name|length() }}

{% if is_function(cls) %}
    .. autofunction:: acord.bases.{{ cls_name }}

{% else %}
    .. attributetable:: acord.bases.{{ cls_name }}

    .. autoclass:: acord.bases.{{ cls_name }}
        :members:
        :inherited-members: {{ filter_properties(cls) }}

{% endif %}

   {% endif %}
{% endfor %}
