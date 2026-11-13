# tools/label

Hand labeling of the golden set (step 3, issue #4), blind to every parser.

## Practice

```sh
uv run python -m tools.label.practice                 # 50 invented rows, easy first (local-data/practice/)
uv run python -m tools.label.server label 0 --practice
```

Practice labels go to `local-data/practice/labels/`, not the real logs. Delete `local-data/practice/` when done.

## Labeling a round (blind)

```sh
uv run python -m tools.label.server label 1     # then open http://127.0.0.1:8765/
```

The page shows one card at a time (text only; the rounds hold no pre-labels). Drag over characters, or click a word, and
press the label's key (the palette lists them). `=` switches to **accept as alternative**: the next label is recorded as
an extra accepted reading of that span (the per-card conventions). Tab flags the card `doubtful`. Enter saves and moves
on; the page opens at the first unlabeled card, so a stopped session resumes where it ended. Spans may not overlap and
may not start or end on a space; the server refuses a bad card (the error never quotes the text).

Every save is appended to `local-data/labels/round-N.jsonl` (git-ignored; the log keeps the time in ms and the key count
per save). The latest save per card is the label.

## Adjudication (after all rounds are labeled and the parsers have run)

```sh
uv run python -m tools.label.adjudicate 1 2 3 4 5 6   # writes local-data/labels/adjudication.jsonl
uv run python -m tools.label.server adjudicate
```

`adjudicate.py` is the only code here that runs parsers. It lists, per card, each span a parser read that the gold does
not hold (coarse labels from parsers that cannot split a field count as agreeing when they cover the gold's whole
field; accepted alternatives count as agreeing). The page shows the readings with no parser name; "change to this"
applies it, and saving a card in this mode records it as phase `adjudicate`. The gold is never edited from a parser's
output except by the owner's decision on that card.

## Export

```sh
uv run python -c "from tools.label import store; print(store.export_round(1))"
```

Writes `sets/golden/gold/round-N.jsonl` (committed; `id`, `text`, `spans`, `alternatives`, `doubtful`) once every card
of the round is labeled, and returns the counts (cards, doubtful, with alternatives, adjudicated saves) for the manifest.
Only the invented and anonymized text of `sets/golden/rounds/` ever reaches this folder.
