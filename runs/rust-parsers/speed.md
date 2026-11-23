## Speed, load time, memory and install size

Machine: Intel(R) Core(TM) i9-9900K CPU @ 3.60GHz; 4 of 14 CPUs usable and 49 GB visible; Linux 6.18.58.1-microsoft-standard-WSL2; Python 3.13.16. Reference profile: 4 CPUs, 8 GB; a run on other hardware is not that profile.
Inputs: 20,000 strings (the shipped golden set's 2,439 strings, repeated). A figure is the median of 3 passes; the range is the fastest to the slowest pass.
Versions: address_parser 0.1.10; addrust 0.1.2@8e28a7e (default configuration); us_address_parser 0.3.0.

| | address_parser | addrust | us_address_parser |
|---|---|---|---|
| Strings per second, one process | 36,424 (35,478 to 36,427) | 6,953 (6,884 to 6,976) | 87,027 (84,767 to 88,076) |
| Strings per second, 4 processes | 91,764 (89,836 to 132,132) | 20,823 (19,226 to 22,271) | 250,191 (215,300 to 266,275) |
| Load time (import and first parse) | 0.008 s | 0.026 s | 0.039 s |
| Memory after loading, one process | 21 MB | 26 MB | 33 MB |
| Memory after 20,000 parses, one process | 23 MB | 30 MB | 34 MB |
| Memory after loading, 4 processes together (shared pages counted once) | 25 MB | 25 MB | 26 MB |
| Install size | 4.3 MB | 4.3 MB | 4.3 MB |

Install size covers: address_parser: the one worker binary shared by the three Rust parsers; addrust: the one worker binary shared by the three Rust parsers; us_address_parser: the one worker binary shared by the three Rust parsers.

Speed and cost are never folded into the Parser Score. Each call is the parser's own (`doorplate.parse_tokens`, `usaddress.parse`, `postal.parser.parse_address`), without the adapter's alignment; a process is one thread.
