# Round 8 (`nightmare`) survey: covered and adjacent variants

Survey step of issue #22 (part of #14). Nothing here is drawn or built. Every string is invented from the shape the
issue describes, and each must still pass the exclusion check before use. Doorplate is never run to confirm a variant.

**Sources read (2026-11-13).** doorplate: closed issues of milestones 0.5.0, 0.5.x, 0.6.0, 0.6.x (about 130 rule issues)
and its open `Later` and `0.7.0` issues (D#n). usaddress: issues 57 to 413 (U#n). libpostal: 508 issues, searched for
US shapes (L#n). Numbers refer to `jeremeybingham/doorplate`, `datamade/usaddress` and `openvenues/libpostal`.

**Tag rule (from #22).** `covered` is the rule's own form: a closed issue whose fix landed. `adjacent` is a nearby form the
issue says is left out or still open. For an outside parser the same holds: a closed issue gives `covered`, an open one
`adjacent`. A usaddress or libpostal issue is closed by that project's own decision, so `covered` there says only that the
shape was fixed or accepted, not that the parser now gets it right.

**Caveat on reading these.** Doorplate's closed issues were closed when the rule merged, and its `Later` issues are open
by choice (not yet measured), so "adjacent" there means "no rule", not "known failure". The label comes from the issue
text only. Expect some adjacent cards to be `ambiguous` or `doubtful` (rule 4 of #22).

## 1. The seven classes already in the class table

| Class | `covered` (rule's form) | `adjacent` (left out or open) | Sources |
|---|---|---|---|
| `second-number` | a building and a unit, `31 208 Birch Ln` (#591); a close same-parity pair, `7310 7312 Oak Dr` (#590) | two numbers joined by `&`, `3 & 5 E 41st St` (D#274; L#85 closed for libpostal); the second number's warning (D#617) | D#590, #591, #274, #617, #544; L#85 |
| `letter-before-street` | a letter A to D, then a name: `46 B Linden Ave` is a unit (D#487, decision D#270) | a letter outside A to D, then a direction letter, then a name: `9311 J W Clay Blvd`, an initial (D#360); a letter before the number, `G 215 County Road 9` (D#312); initial in a street named for a person (U#245) | D#487, #270, #360, #312; U#245 |
| `no-so-direction` | `464 NO Maple Ave` and `84 Elmhurst Pl SO` (D#470, #269) | `County Rd SO` with no number: direction or road name? (D#643); a name that is a direction word, `250 South St E` (U#402) | D#470, #269, #643; U#402 |
| `county-road-compass` | `4410 County Road SE 1234`, number is the unit (D#642); `88 East TR 56` as road `TR 56` (D#388) | `<Name> Road <n>` outside the closed list of states and words (D#593, #315); `Farm Road 1110` (U#315, open); `2000 S East Loop 410` (U#247, open); `18778 RM 1431` vs `FM 1431` (U#364, open) | D#642, #388, #593; U#100 (closed), #315, #247, #364 |
| `zip4-cut` | `75001-12` and the unhyphenated `7500112` repaired to `75001` (D#275, #606) | a ZIP+4 with a space, `33000 1234` (D#519); a four-digit ZIP with the zero lost and a space before the `+4`, `Newark NJ 7102 -1234` (D#275, partly) ; ZIP before state, `Oakland 94610-2737 CA` (L#382) | D#275, #606, #541, #519; L#382 |
| `unit-before-street` | `12-40 Suite 9 Delmar Blvd`, a suffix word follows (D#296) | `242 Apt B Example` with no suffix; `Apt S` plus street, value on line 2 (D#529, #498) | D#296, #529, #498; U#208 |
| `paren-unit` | `12 Elm St (3rd Fl)` at the edge of a segment (D#291) | a parenthesized group that is not a unit, `(Rear Entrance)` (D#644); a parenthesis inside a name, `Martin (Luther King Blvd` (D#645); closed: unclosed `(` (D#516) is covered | D#291, #516, #644, #645 |

## 2. The eight outside classes already in the class table

The doorplate-side figures above came from rule issues. The outside classes were written from USPS Publication 28, so
they lack an issue source. This pass finds one for each, or says so.

| Class | `covered` | `adjacent` | Sources |
|---|---|---|---|
| `military` | `PSC 1234 Box 56, APO AE 09012` (Pub 28 form) | the three military images left in Pub 28 (D#92, open) | D#92. **Thin**: no usaddress or libpostal issue found; prison and DOC lines (U#239, open) are a near neighbor |
| `urbanization` | `URB Las Flores` on its own line before the street | `URB` after the street, `27 Calle Luna URB Las Palmas` (D#318); street-first Puerto Rico forms (D#319); Texas `PR 462` private road (D#314) | D#318, #319, #314, #332. Covered form has no closed issue; from Pub 28 |
| `grid` | `640 E 3780 S`-style with directionals (D#269, closed); `W148 N9748 Tree Tops Dr` (U#92, closed) | the same Wisconsin form for doorplate (D#311, #242, open in 0.7.0); a grid system the schema has no field for (L#295) | D#311, #269; U#92; L#295. **Split this class** into two shapes: Utah-style (`E 400 S`) and Wisconsin-style (`N45 W2210`) |
| `spelled-number` | `One Marlow Park Ave` before a suffix-word name (D#221) | a lone `ONE` on line 2 (D#559); a spelled number with commas, `Twelve, Elm St` (D#601); spelled-out numbers in a street (U#194, open) | D#221, #559, #601; U#194 |
| `intersection` | `1176 Town & Country Cmns` is not an intersection (U#85, closed); `72 Rolfe & Arcadia Ave` (L#84, closed) | `Oak St / 3rd Ave` with a slash (U#218, open); a non-numeric building and an intersection (U#230, #312, #357, open) | U#85, #218, #230, #312, #357; L#84. Doorplate has no field (D#35 Won't Do) so it is a pure outside class |
| `highway-lettered` | `United States Highway 27` (D#543); `State Rd QQ` keeps the letters (D#589) | `Old United States Highway 41-45` (D#608); `Business` routes (U#186, closed); a lot on a state highway, `Lot 2-B MN Hwy 108` (L#452, open); multiple highways in one line (U#206, open) | D#543, #608, #589; U#186, #206; L#452, #238 |
| `milepost` | no source found | no source found | **No issue in any of the three trackers mentions a mile marker.** Keep as an unpaired class from Pub 28, or drop it; the owner decides |
| `non-address-nightmare` | placeholder in the street field, `No Address On File` (D#273); `NaN` in city (D#419) | boilerplate before the street (D#483); a foreign address, line 2 ends in a country (D#361); prison inmate line (U#239) | D#273, #419, #483, #361; U#262 (open), U#239 |

## 3. Candidate classes found by the survey (not in the table)

Each would replace `milepost` or one of the thinner classes, or join `nightmare`. Sizes are not estimated here.

| Candidate | `covered` | `adjacent` | Sources |
|---|---|---|---|
| `box-glued` | `Campus Box 4521`, `Northfield CPO #1234` (D#373, #384); `PO Box` before a place called Box Elder (U#124) | `POBOX481`, `HCR75 BOX 12D`, `P O BOX2284` (D#304); `PO Drawer C` (D#598); `PO Box NA` (D#358) | D#373, #384, #304, #598, #358; U#124; L#21 |
| `fraction-form` | `1 2 N Main St`, a half with no slash (D#247, #387) | a Unicode half or a quarter after the number, `537½` (L#191); `4422 1/4 Lincoln Ave` (U#151, open) | D#247, #387; L#191; U#151, #79 |
| `lot-trailer-site` | `Pier 39 Lot 12` (U#139, closed); `Msc 518` after the street (D#375, open) is adjacent for doorplate | `5th Street Trailer 30` (U#349); `Lot 2-B MN Hwy 108` (L#452); a pier at the end of a street name (D#327) | U#139, #349; D#375, #327; L#452 |
| `separator-after-suffix` | `St - 2210`, `Ave / 4C` (D#308, #309) | `Rd - Oak Twp` place or unit (D#341); a spaced hyphen between building and street (D#310) | D#308, #309, #341, #310 |
| `suffix-chain-unit` | `Rd St 3-204`, ST for SUITE after a suffix (D#288) | two suffix words then a unit, `Pkwy Ave Fleet 10-20` (D#243); a unit value that is a suffix code, `Suite LA` (D#272); suite plus unit (U#334, #392 closed) | D#288, #243, #272; U#334, #392 |
| `place-looks-like-state` | `North Carolina` is not a street (U#126, closed) | a city that starts with a state name, `Virginia Beach 99999` (D#480); a region phrase as the state (D#482); `La` in `La Quinta` (U#205, #358) | U#126, #205, #358; D#480, #482; L#364 |
| `number-pair-by-state` | Queens, Hawaii and Massachusetts spaced pairs, `31 14 90th Ave` (D#313; U#101 closed) | five-digit number as two parts, `12 345 Elm St` (D#501); thousands comma, `20,000 Example Rd` (D#560) | D#313, #501, #560; U#101 |
| `care-of` | `C/O Jane Doe` with no separator (D#259, #473) | `CO Harbor 2100 Oak St` over a `%` line (D#367); a person or business on line 2 (D#472) | D#259, #473, #367, #472 |

`care-of` is already a `hard` class in the base set; here it would move up only in its adjacent variant. Treat the rest
as proposals.

## 4. What this means for round 8

- **Pairing works for 12 of the 15 classes** (7 doorplate-research plus `grid`, `spelled-number`, `intersection`,
  `highway-lettered`, `non-address-nightmare`) with a real source for both variants. `military` and `urbanization` have
  an adjacent source (open issue) but a covered form from Pub 28 only. `milepost` has no source at all.
- **Bias check.** Of the sources above, doorplate's leftovers dominate (they are the best documented). For symmetry the
  outside half draws its `adjacent` forms from usaddress open issues (U#151, #218, #247, #315, #349, #364, #402) and
  libpostal open issues (L#191, #238, #382, #452, #580, #671), and its `covered` forms from their closed ones. A usaddress
  or libpostal issue is a report of one failing string, not a measured rule, so those variants are looser than
  doorplate's. Two caveats follow:
  - Some adjacent cards from an outside tracker are known failures **of that parser**; the same class's covered card is
    one the parser was reported to read wrong and later accepted. That is symmetric across parsers only if each tracker
    contributes similar numbers. A fixed cap per origin (state it in `COMPOSITION.md`) keeps this honest.
  - The libpostal and usaddress trackers are mostly non-US or install problems; the usable US shapes are about 20 issues
    each, so the outside half stays small. This supports reporting at tier level, not per class.
- **Cell size.** 15 classes by 2 variants in about 300 records is about 10 cards a cell. Still too few for per-class
  intervals; report the covered-versus-adjacent gap at tier level (as #22 suggests).

## 5. Decisions for the owner

1. **Which classes.** Drop `milepost` (no source) or keep it unpaired as `neutral`? Add any of section 3 (suggested:
   `box-glued`, `fraction-form`, `lot-trailer-site`, which have sources in all three trackers)?
2. **Split `grid`** into Utah-style and Wisconsin-style (suggested), since their covered and adjacent forms differ.
3. **Variant split:** equal (suggested) or weighted to `adjacent`.
4. **Cap per origin** for outside-tracker cards (so no parser's own tracker supplies most of its `adjacent` cards).
5. **Size of `nightmare`:** stay at about 300 and report at tier level (suggested), or grow it.
6. **Thin classes** (`military`, `urbanization`): keep with a Pub 28 covered form and an open-issue adjacent form, or find
   another source first.

After the owner settles these: the class table gets `variant` and `source`, `COMPOSITION.md` states the shares, then the
draw (the remaining steps of #22).

## 6. Decisions taken (2026-11-13, owner accepted the suggested defaults)

1. `milepost` dropped; `box-glued`, `fraction-form`, `lot-trailer-site` added.
2. `grid` split into `grid-utah` and `grid-wisconsin`.
3. Variants split equally.
4. Cap: no parser's own tracker supplies more than a third of the outside `adjacent` records.
5. `nightmare` stays at about 300; the gap is reported at tier level.
6. `military` and `urbanization` kept with a Pub 28 covered form (thin; noted in their `source`).

Recorded in `CLASSES` (`tools/golden/tiers.py`) and `sets/golden/COMPOSITION.md`.
