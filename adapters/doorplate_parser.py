"""doorplate, through `parse_tokens` (its token labels), aligned to character spans."""

import doorplate

from adapters.base import Adapter, Mapping, Span, align


class DoorplateAdapter(Adapter):
    name = "doorplate"

    def __init__(self):
        self.mapping = Mapping(self.name)

    def parse(self, text: str) -> list[Span]:
        try:
            pieces = doorplate.parse_tokens(text)
        except doorplate.ParseError:  # blank input or an intersection: it claims nothing
            return []
        return align(text, pieces)

    def versions(self) -> dict[str, str]:
        return {"doorplate": doorplate.__version__}
