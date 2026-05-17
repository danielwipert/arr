"""Shared prompt-rendering helper.

`str.format` chokes on literal braces in prompts that show JSON examples,
which is most of them. This module exposes a tiny `{name}`-only renderer
that leaves all other braces alone.
"""

from __future__ import annotations


def render(template: str, **kwargs: str) -> str:
    """Replace `{name}` placeholders in `template`. Literal braces are kept as-is."""
    out = template
    for key, value in kwargs.items():
        out = out.replace("{" + key + "}", value)
    return out
