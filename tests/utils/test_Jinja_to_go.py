from DART.utils.Jinja_to_go import convert_chat_template_to_modelfile


chat_template = """
{% if messages[0]['role'] == 'system' %}
{{ system_message }}
{% endif %}
{% for message in messages %}
{% if message['role'] == 'user' %}
<|user|>
{{ message['content'] | trim }}
{% elif message['role'] == 'assistant' %}
<|assistant|>
{{ message['content'] | trim }}<|EOT|>
{% endif %}
{% endfor %}
<|assistant|>
"""

modelfile = convert_chat_template_to_modelfile(chat_template)

print(modelfile)
