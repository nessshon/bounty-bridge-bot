from dataclasses import dataclass

from starlette_admin import URLField


@dataclass
class ImageFromURLField(URLField):
    display_template: str = "displays/_image_from_url.html"
    label_template: str = "forms/_image_from_url.html"
    render_function_key: str = "image_url"
