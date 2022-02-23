.. meta::
   :title: Documentation - Acord [Application Commands]
   :type: website
   :url: https://acord.readthedocs.io/api/ext/application_commands.html
   :description: Acord application commands
   :theme-color: #f54646

.. currentmodule:: acord

********************
Application Commands
********************
Application commands are recommended to be subclassed,
but theres always a decorator for those who dont like that.


{% for object in dir(acord.ext.application_commands) %}
   {% set cls = getattr(acord.ext.application_commands, object, None) %}
   {% set cls_name = getattr(cls, "__name__", "") %}

   {% if cls is callable and cls_name not in disallow %}
{{ cls_name }}
{{ "=" * cls_name|length() }}

{% if is_function(cls) == True %}
    .. autofunction:: acord.ext.application_commands.{{ cls_name }}

{% else %}
    .. attributetable:: acord.ext.application_commands.{{ cls_name }}

    .. autoclass:: acord.ext.application_commands.{{ cls_name }}
        :members:
        :inherited-members:
        :exclude-members: {{ SHARED_PROPERTIES|join(", ") }}

{% endif %}

   {% endif %}
{% endfor %}
