.. meta::
   :title: Documentation - Acord [Webhooks]
   :type: website
   :url: https://acord.readthedocs.io/api/webhooks.html
   :description: Acord webhooks
   :theme-color: #f54646

.. currentmodule:: acord

********
Webhooks
********

.. note::
    Webhook messages cannot physically interact with normal messages,
    this will be changed in future updates. 
    But a quick work around is to simply fetch that message

{% for cls in [acord.Webhook, acord.PartialWebhook, acord.WebhookType] %}
   {% set cls_name = getattr(cls, "__name__", "") %}

   {% if cls is callable and cls_name not in disallow %}
{{ cls_name }}
{{ "=" * cls_name|length() }}

{% if is_function(cls) %}
    .. autofunction:: acord.{{ cls_name }}

{% else %}
    .. attributetable:: acord.{{ cls_name }}

    .. autoclass:: acord.{{ cls_name }}
        :members:
        :inherited-members:
        :exclude-members: {{ SHARED_PROPERTIES|join(", ") }}

{% endif %}

   {% endif %}
{% endfor %}
