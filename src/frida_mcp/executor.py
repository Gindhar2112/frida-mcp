"""Script execution with automatic try-catch wrapping and send->console.log conversion."""

import re


def wrap_script(js_code: str) -> str:
    """Wrap user script: replace send() calls with console.log, add try-catch."""
    # Replace send(...) with console.log(JSON.stringify(...))
    # Match send( but not something_send(
    converted = re.sub(
        r'(?<![.\w])send\(',
        'console.log(JSON.stringify(',
        js_code
    )
    # Add matching closing paren for the JSON.stringify(
    # Each send(x) becomes console.log(JSON.stringify(x))
    # We need to add )) where send had )
    # Simple approach: count replacements and fix parens
    # Better: just do a smarter replacement
    converted = _convert_send_calls(js_code)

    stripped = converted.strip()
    if stripped.startswith("try"):
        return converted

    return f"""try {{
{converted}
}} catch(e) {{
    console.log(JSON.stringify({{type: "error", message: e.toString(), stack: e.stack}}));
}}"""


def _convert_send_calls(js_code: str) -> str:
    """Convert send({...}) to console.log(JSON.stringify({...}))."""
    # Replace standalone send( with console.log(JSON.stringify(
    # and add extra ) at the matching close paren
    result = []
    i = 0
    while i < len(js_code):
        # Check for 'send(' not preceded by word char or dot
        if js_code[i:i+5] == 'send(' and (i == 0 or not js_code[i-1].isalnum() and js_code[i-1] != '.'):
            # Find matching closing paren
            depth = 1
            j = i + 5
            while j < len(js_code) and depth > 0:
                if js_code[j] == '(':
                    depth += 1
                elif js_code[j] == ')':
                    depth -= 1
                j += 1
            # Extract the argument
            arg = js_code[i+5:j-1]
            result.append(f'console.log(JSON.stringify({arg}))')
            i = j
        else:
            result.append(js_code[i])
            i += 1
    return ''.join(result)


def validate_script(js_code: str) -> str | None:
    """Basic script validation. Returns error message or None if OK."""
    if not js_code or not js_code.strip():
        return "Script is empty."

    open_braces = js_code.count("{")
    close_braces = js_code.count("}")
    if open_braces != close_braces:
        return f"Unbalanced braces: {open_braces} open vs {close_braces} close."

    return None
