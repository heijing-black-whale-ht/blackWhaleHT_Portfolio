import os
from functools import lru_cache
from flask import current_app
from markupsafe import Markup

@lru_cache(maxsize=None)
def _load_svg(style: str, name: str) -> str:
    path = os.path.join(
        current_app.static_folder, "icons", style, f"{name}.svg"
    )
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def icon(name: str, style: str = "outline", classes: str = "w-5 h-5") -> Markup:
    svg = _load_svg(style, name)
    # inject classes into the <svg ...> tag 
    svg = svg.replace("<svg", f'<svg class="{classes}"', 1)
    return Markup(svg)