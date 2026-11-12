# address-parser-showdown

A neutral, repeatable comparison of US address parsers: [doorplate](https://github.com/jeremeybingham/doorplate),
[usaddress](https://github.com/datamade/usaddress) and [libpostal](https://github.com/openvenues/libpostal) to start
with, and any other parser that supplies an adapter.

> **Status: shell.** Nothing is scored yet. The plan and the v0.1.0 tracker are in the repository's issues
> (milestone **v0.1.0**); the rules that keep the comparison fair are in [`METHODOLOGY.md`](METHODOLOGY.md).

## What it will hold

| Folder | What |
|---|---|
| [`schema/`](schema/README.md) | The neutral label schema every parser's output is mapped to |
| [`adapters/`](adapters/README.md) | One module per parser: a string in, character spans in the parser's own labels out, plus its mapping table |
| [`sets/`](sets/README.md) | The test sets, each with a `MANIFEST.md` (source, license, counts, checksums) |
| [`scorer/`](scorer/README.md) | Span-based scoring, record accuracy, field F1 and the Parser Score |
| [`runs/`](runs/README.md) | Prediction files and results per pinned parser version |
| [`report/`](report/README.md) | The research report, written after the runs |

## Conflict of interest

doorplate's author builds this repository. The mitigations (blind labeling, a score formula fixed before the first
scored run, a private twin of the golden set, every prediction file published) are in [`METHODOLOGY.md`](METHODOLOGY.md).

## License

Code: MIT ([`LICENSE`](LICENSE)). Data: per set, stated in each set's `MANIFEST.md`.
