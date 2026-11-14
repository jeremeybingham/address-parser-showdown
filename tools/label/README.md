# tools/label

Hand labeling of the golden set (step 3, issue #4), blind to every parser.

## Practice

```sh
uv run python -m tools.label.practice                 # 50 invented rows, easy first (local-data/practice/)
uv run python -m tools.label.server label 0 --practice
```

Practice labels go to `local-data/practice/labels/`, not the real logs. Delete `local-data/practice/` when done.

## Labeling a round (blind)

The rounds are labeled on the unmasked text of the same cards (public-record cards show the row's own text, so a hard
card can be looked up on a map). Write it once (git-ignored, `local-data/golden-real/rounds/`):

```sh
uv run python tools/golden/sample.py --confirm --real   # redoes the draw; refuses unless it reproduces sets/golden/rounds/
```

```sh
uv run python -m tools.label.server label 1     # then open http://127.0.0.1:8765/
```

The page shows one card at a time (text only; the rounds hold no pre-labels). Drag over characters, or click a word, and
press the label's key (the palette lists them). `=` switches to **accept as alternative**: the next label is recorded as
an extra accepted reading of that span (the per-card conventions). Tab flags the card `doubtful`. **Copy address** puts the card's text on the clipboard (for a map lookup). The **flag** menu marks a card with no right
reading: `non-address` (leave it with no spans) or `ambiguous` (label one reading and add the others as alternatives); such
a card is reported apart and is in no score (`sets/golden/COMPOSITION.md`, "Difficulty tiers"). Enter saves and moves
on; the page opens at the first unlabeled card, so a stopped session resumes where it ended. Spans may not overlap and
may not start or end on a space; the server refuses a bad card (the error never quotes the text).

Every save is appended to `local-data/labels/round-N.jsonl` (git-ignored; the log keeps the time in ms, the key count
and a hash of the text per save). The latest save per card is the label. A save made on other text (the anonymized
text, before labeling moved to the unmasked text) does not count: the card shows as new again.

## Typo check (any time, no parser)

```sh
uv run python -m tools.label.lint        # all rounds; or: ... lint 3 4
```

Prints, per round, the hits per rule and the card ids (never the text). Rules are in the module docstring: unknown
state, a ZIP that is not 5 digits, ZIP and state that disagree (GeoNames list), a direction span that is not a direction
word, a direction word left inside a street name, parts out of order, a word outside every span. A hit is a reason to
look again, not an error; fix a card by opening it in the labeling page. It runs no parser, so it does not touch the
blind rule.

### Lint review (a repeatable step: now, and again once every round is labeled, before adjudication)

```sh
uv run python -m tools.label.lint --queue        # writes local-data/labels/review-queue.jsonl (round, id, rules)
uv run python -m tools.label.server review       # http://127.0.0.1:8765/ : one queue over all rounds
```

Each queued card opens with your saved labels in place and the rule names that hit it above the text; change what is
wrong, or press Enter to keep it (Enter saves the card as shown). Saves go to the same round log with phase `review`, and
the latest save wins. Re-run `lint --queue` afterwards to see what is left (a card you kept as is still hits: that is
expected for bare numbers). It runs no parser. Run it before adjudication so the parser-disagreement pass starts from
cleaned labels.

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

Writes the private gold `local-data/golden-real/gold/round-N.jsonl` (git-ignored; `id`, `text`, `spans`, `alternatives`, `doubtful`, `flag`) once
every card of the round is labeled, and returns the counts (cards, doubtful, flagged, with alternatives, adjudicated
saves) for the manifest. The tier is not stored here: `tools/sets/golden.py` adds it from the shape class when it
converts the gold for the scorer (`tools/golden/tiers.py`).
Then make the shipped gold, with invented values in place of the private ones and the spans unchanged:

```sh
uv run python -m tools.golden.derive 1    # -> sets/golden/gold/round-1.jsonl (committed); counts and held card ids only
```

It holds back a card that would ship a real word (label that word, often as `other`, and run it again) and writes a
side-by-side review file, `local-data/golden-real/review/round-N.md`, to read before committing.
Only invented or anonymized text ever reaches `sets/golden/gold/`.
