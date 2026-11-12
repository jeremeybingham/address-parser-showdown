# adapters

One module per parser. Not written yet (step 1).

**Contract:** a string goes in; a list of `(start, end, label)` character spans in the parser's own labels comes out.
Each adapter has a mapping file from its labels to the canonical schema (`schema/`). A conformance test (a few dozen
invented strings) checks that an adapter's spans cover the input and that its mapping is complete.

Adding a parser: write the module and its mapping, pass the conformance test, pin the version. (Full steps to come.)
