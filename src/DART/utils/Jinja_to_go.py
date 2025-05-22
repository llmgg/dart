import re


def convert_chat_template_to_modelfile(template: str):
    # 初始化 Ollama Modelfile 内容
    modelfile_content = []

    # 提取系统消息（如果有）
    system_match = re.search(r"{% if.*?system.*?%}(.*?){% endif %}", template, re.DOTALL)
    if system_match:
        system_content = re.sub(r"{{ system_message }}", "{{ .System }}", system_match.group(1))
        modelfile_content.append(f"SYSTEM \"\"\"\n{system_content.strip()}\n\"\"\"")

    # 提取对话模板
    messages_match = re.search(r"{% for message in messages %}(.*?){% endfor %}", template, re.DOTALL)
    if messages_match:
        role_templates = []
        role_content = messages_match.group(1)

        # 分割不同角色的模板
        roles = re.split(r"{% if.*?%}", role_content)
        for role_block in roles:
            role_type_match = re.search(r"message$'role'$ == '(system|user|assistant)' %}", role_block)
            if not role_type_match:
                continue

            role_type = role_type_match.group(1)
            content = re.sub(
                r"{{ message$'content'$ \| trim }}",
                "{{ .Prompt }}" if role_type == "user" else "{{ .Response }}",
                role_block.split("%}")[1].strip()
            )

            # 清理特殊字符并添加模板
            content = content.replace("'", "\\\"")
            role_templates.append(f"{{{{ if .{role_type.capitalize()} }}}} {content} {{{{ end }}}}")

        # 构建对话模板
        full_template = " ".join(role_templates)
        modelfile_content.append(f"TEMPLATE \"\"\"\n{full_template}\n\"\"\"")

        # 添加后缀处理（如果有）
        if "eos_token" in template:
            modelfile_content.append("PARAMETER stop \"<|EOT|>\"")

    # 返回 Modelfile
    return "\n\n".join(modelfile_content)

