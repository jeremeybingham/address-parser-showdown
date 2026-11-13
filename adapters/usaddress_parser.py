"""usaddress, through `usaddress.parse` (default model), aligned to character spans."""

from importlib.metadata import version

import usaddress

from adapters.base import Adapter, Mapping, Span, align


class UsaddressAdapter(Adapter):
    name = "usaddress"

    def __init__(self):
        self.mapping = Mapping(self.name)

    def parse(self, text: str) -> list[Span]:
        return align(text, usaddress.parse(text))

    def versions(self) -> dict[str, str]:
        return {"usaddress": version("usaddress"), "python-crfsuite": version("python-crfsuite")}
