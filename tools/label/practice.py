"""A throwaway practice round of 50 invented addresses, easy first, then harder, for learning the labeling page.

    uv run python -m tools.label.practice      # writes local-data/practice/round-0.jsonl (git-ignored)
    uv run python -m tools.label.server label 0 --practice

Every string is invented. Practice labels go to `local-data/practice/labels/`, never to the real logs.
"""

import json
from pathlib import Path

ROWS = [
    # 1-10: plain number, street, city, state, ZIP
    "214 Maple Street, Tampa, FL 33601",
    "88 Cedar Ave, Austin, TX 78701",
    "1500 Lakeview Drive, Reno, NV 89501",
    "7 Harbor Road, Portland, ME 04101",
    "320 Birch Lane, Springfield, IL 62704",
    "45 Willow Court, Boise, ID 83702",
    "9012 Sunset Boulevard, Denver, CO 80202",
    "63 Pine Way, Madison, WI 53703",
    "410 Orchard Place, Columbus, OH 43215",
    "27 Mill Circle, Raleigh, NC 27601",
    # 11-20: directions, multi-word names, no commas, ZIP+4, case
    "216 N Maple Street, Tampa, FL 33601",
    "1500 East Lakeview Drive, Reno, NV 89501",
    "88 Cedar Ave SW, Austin, TX 78701",
    "512 W Old Mill Road, Boise, ID 83702",
    "340 Park Ridge Terrace, Madison, WI 53703-1234",
    "77 Little River Trail Tampa FL 33601",
    "1200 S Harbor View Pkwy, Portland, ME 04101",
    "9 NORTH ORCHARD PLACE, COLUMBUS, OH 43215",
    "oak hollow drive 42, raleigh, nc 27601",
    "1801 NE 5th Street, Denver, CO 80202",
    # 21-30: units, one and two
    "214 Maple Street Apt 4B, Tampa, FL 33601",
    "88 Cedar Ave, Suite 300, Austin, TX 78701",
    "1500 Lakeview Drive Unit 12, Reno, NV 89501",
    "7 Harbor Road Floor 3, Portland, ME 04101",
    "320 Birch Lane Bldg 2 Apt 9, Springfield, IL 62704",
    "45 Willow Court Rm 101, Boise, ID 83702",
    "9012 Sunset Blvd Ste 5 Fl 2, Denver, CO 80202",
    "63 Pine Way Lot 14, Madison, WI 53703",
    "410 Orchard Place Basement, Columbus, OH 43215",
    "27 Mill Circle Apt C, Raleigh, NC 27601",
    # 31-38: PO boxes, rural routes, highways, military-style routes
    "PO Box 1187, Tampa, FL 33601",
    "P.O. Box 42, Austin, TX 78701",
    "Post Office Box 9, Reno, NV 89501",
    "RR 2 Box 145, Boise, ID 83702",
    "Rural Route 4 Box 22A, Madison, WI 53703",
    "HC 68 Box 23, Columbus, OH 43215",
    "State Highway 41, Raleigh, NC 27601",
    "1200 US Hwy 19 N, Tampa, FL 33601",
    # 39-44: the two conventions
    "123 B Elm Street, Springfield, IL 62704",
    "56 A Orchard Place, Columbus, OH 43215",
    "214 Maple Street # 4, Tampa, FL 33601",
    "88 Cedar Ave #12B, Austin, TX 78701",
    "9012 Sunset Blvd Apt #3, Denver, CO 80202",
    "410 Orchard Place # APT 8, Columbus, OH 43215",
    # 45-50: complex
    "N165 W2123 Old Mill Road, Madison, WI 53703",
    "3200 Avenue C, Tampa, FL 33601",
    "17 Saint Charles St S Elgin, IL 60177",
    "Maria Torres, 4th Floor, 77 Harbor Rd Ext, Portland, ME 04101",
    "1850 1/2 Birch Ln Unit 2 Rear, Springfield, IL 62704",
    "92 Cedr Stret Apt 5, Raliegh NC 27601",
]


def main() -> None:
    assert len(ROWS) == 50
    out = Path(__file__).resolve().parents[2] / "local-data" / "practice"
    out.mkdir(parents=True, exist_ok=True)
    (out / "round-0.jsonl").write_text(
        "".join(json.dumps({"id": f"p{i:02d}", "text": t}) + "\n" for i, t in enumerate(ROWS, 1))
    )
    print(f"50 practice rows in {out / 'round-0.jsonl'}")


if __name__ == "__main__":
    main()
