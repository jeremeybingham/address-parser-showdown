## Speed, load time, memory and install size

Machine: Intel(R) Core(TM) i9-9900K CPU @ 3.60GHz; 4 of 14 CPUs usable and 49 GB visible; Linux 6.18.58.1-microsoft-standard-WSL2; Python 3.13.16. Reference profile: 4 CPUs, 8 GB; a run on other hardware is not that profile.
Inputs: 100,000 strings (the shipped golden set's 2,439 strings, repeated). A figure is the median of 5 passes; the range is the fastest to the slowest pass.
Versions: doorplate 0.6.0; libpostal 25099c506612b34b23b1bfe286ca6321fcf06f35, data_checksum a42c356d1283c7e1ff9994b6bfc0a1015956718840e1aff8a5afae7dec237762, pypostal 1.1.11; usaddress 0.5.16, python-crfsuite 0.9.12.

| | doorplate | libpostal | usaddress |
|---|---|---|---|
| Strings per second, one process | 64,876 (63,586 to 66,659) | 12,818 (12,432 to 12,983) | 8,395 (8,302 to 8,458) |
| Strings per second, 4 processes | 235,179 (228,338 to 244,303) | 41,636 (40,087 to 42,845) | 27,026 (25,633 to 27,435) |
| Load time (import and first parse) | 0.003 s | 3.814 s | 0.011 s |
| Memory after loading, one process | 27 MB | 2,958 MB | 27 MB |
| Memory after 100,000 parses, one process | 28 MB | 2,959 MB | 27 MB |
| Memory after loading, 4 processes together (shared pages counted once) | 37 MB | 11,771 MB | 42 MB |
| Install size | 4.9 MB | 2,993.1 MB | 4.8 MB |

Install size covers: doorplate: package and required packages: doorplate; libpostal: libpostal library and model data; usaddress: package and required packages: probableparsing, python-crfsuite, usaddress.

Speed and cost are never folded into the Parser Score. Each call is the parser's own (`doorplate.parse_tokens`, `usaddress.parse`, `postal.parser.parse_address`), without the adapter's alignment; a process is one thread.
