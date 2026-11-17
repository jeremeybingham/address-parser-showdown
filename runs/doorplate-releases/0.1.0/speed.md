## Speed, load time, memory and install size

Machine: Intel(R) Core(TM) i9-9900K CPU @ 3.60GHz; 4 of 14 CPUs usable and 49 GB visible; Linux 6.18.58.1-microsoft-standard-WSL2; Python 3.13.16. Reference profile: 4 CPUs, 8 GB; a run on other hardware is not that profile.
Inputs: 100,000 strings (the shipped golden set's 2,439 strings, repeated). A figure is the median of 5 passes; the range is the fastest to the slowest pass.
Versions: doorplate 0.1.0.

| | doorplate |
|---|---|
| Strings per second, one process | 31,433 (31,273 to 31,562) |
| Strings per second, 4 processes | 95,084 (90,911 to 103,472) |
| Load time (import and first parse) | 0.001 s |
| Memory after loading, one process | 26 MB |
| Memory after 100,000 parses, one process | 27 MB |
| Memory after loading, 4 processes together (shared pages counted once) | 35 MB |
| Install size | 4.1 MB |

Install size covers: doorplate: package and required packages: doorplate.

Speed and cost are never folded into the Parser Score. Each call is the parser's own (`doorplate.parse_tokens`, `usaddress.parse`, `postal.parser.parse_address`), without the adapter's alignment; a process is one thread.
