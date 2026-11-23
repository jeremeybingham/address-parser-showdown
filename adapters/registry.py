"""The adapters by name. A new parser is added here once its module and mapping exist."""

from adapters.address_parser_parser import AddressParserAdapter
from adapters.addrust_parser import AddrustAdapter
from adapters.base import Adapter
from adapters.doorplate_parser import DoorplateAdapter
from adapters.libpostal_parser import LibpostalAdapter
from adapters.us_address_parser_parser import UsAddressParserAdapter
from adapters.usaddress_parser import UsaddressAdapter

ADAPTERS: dict[str, type[Adapter]] = {
    "doorplate": DoorplateAdapter,
    "usaddress": UsaddressAdapter,
    "libpostal": LibpostalAdapter,
    "us_address_parser": UsAddressParserAdapter,
    "addrust": AddrustAdapter,
    "address_parser": AddressParserAdapter,
}
