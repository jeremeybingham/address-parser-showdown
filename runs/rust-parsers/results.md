## Record accuracy by part (coarse track, 95% Wilson interval)

| Set / part | Role | Records | No parser right | doorplate | usaddress | libpostal | address_parser | addrust | us_address_parser |
|---|---|---|---|---|---|---|---|---|---|
| doorplate-suite / hand | scored | 1,000 | 10 | 96.3 (94.9 to 97.3) | 91.1 (89.2 to 92.7) | 84.0 (81.6 to 86.1) | 26.3 (23.7 to 29.1) | 18.8 (16.5 to 21.3) | 0.0 (0.0 to 0.4) |
| doorplate-suite / hard | drawn from the blind spots of two of the three parsers | 2,585 | 120 | 73.4 (71.7 to 75.1) | 25.7 (24.1 to 27.4) | 69.0 (67.2 to 70.8) | 2.4 (1.9 to 3.1) | 18.8 (17.3 to 20.4) | 0.0 (0.0 to 0.1) |
| doorplate-suite / natural | scored | 16,001 | 51 | 98.6 (98.4 to 98.8) | 96.5 (96.2 to 96.7) | 95.0 (94.6 to 95.3) | 6.7 (6.3 to 7.1) | 40.1 (39.4 to 40.9) | 0.0 (0.0 to 0.0) |
| geocode-dev / dev | scored | 60,522 | 671 | 94.4 (94.2 to 94.6) | 88.4 (88.1 to 88.6) | 79.9 (79.6 to 80.2) | 64.3 (63.9 to 64.7) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| golden / hard | scored | 556 | 25 | 92.4 (89.9 to 94.4) | 88.5 (85.6 to 90.9) | 70.9 (67.0 to 74.5) | 37.6 (33.7 to 41.7) | 11.3 (9.0 to 14.2) | 0.0 (0.0 to 0.7) |
| golden / hard/ambiguous | one door, several readings (flagged in blind labeling) | 14 | 4 | 50.0 (26.8 to 73.2) | 71.4 (45.4 to 88.3) | 50.0 (26.8 to 73.2) | 35.7 (16.3 to 61.2) | 7.1 (1.3 to 31.5) | 0.0 (0.0 to 21.5) |
| golden / hard/doubtful | doubtful label (the Parser Score is also shown with these records in) | 17 | 9 | 29.4 (13.3 to 53.1) | 35.3 (17.3 to 58.7) | 23.5 (9.6 to 47.3) | 23.5 (9.6 to 47.3) | 5.9 (1.0 to 27.0) | 0.0 (0.0 to 18.4) |
| golden / hard/multi_address | several doors: fields checked, no single door (flagged in blind labeling) | 11 | 0 | 100.0 (74.1 to 100.0) | 90.9 (62.3 to 98.4) | 90.9 (62.3 to 98.4) | 0.0 (0.0 to 25.9) | 0.0 (0.0 to 25.9) | 0.0 (0.0 to 25.9) |
| golden / hard/non_address | not an address (flagged in blind labeling) | 13 | 0 | 100.0 (77.2 to 100.0) | 30.8 (12.7 to 57.6) | 15.4 (4.3 to 42.2) | 0.0 (0.0 to 22.8) | 30.8 (12.7 to 57.6) | 0.0 (0.0 to 22.8) |
| golden / nightmare | scored | 226 | 28 | 73.0 (66.9 to 78.4) | 51.3 (44.8 to 57.8) | 54.0 (47.5 to 60.4) | 30.1 (24.5 to 36.4) | 15.9 (11.7 to 21.3) | 0.0 (0.0 to 1.7) |
| golden / nightmare/ambiguous | one door, several readings (flagged in blind labeling) | 7 | 0 | 42.9 (15.8 to 75.0) | 57.1 (25.0 to 84.2) | 57.1 (25.0 to 84.2) | 14.3 (2.6 to 51.3) | 0.0 (0.0 to 35.4) | 0.0 (0.0 to 35.4) |
| golden / nightmare/doubtful | doubtful label (the Parser Score is also shown with these records in) | 8 | 1 | 37.5 (13.7 to 69.4) | 25.0 (7.1 to 59.1) | 50.0 (21.5 to 78.5) | 50.0 (21.5 to 78.5) | 25.0 (7.1 to 59.1) | 0.0 (0.0 to 32.4) |
| golden / nightmare/intersection | a corner, no door (flagged in blind labeling) | 4 | 1 | 25.0 (4.6 to 69.9) | 75.0 (30.1 to 95.4) | 0.0 (0.0 to 49.0) | 0.0 (0.0 to 49.0) | 0.0 (0.0 to 49.0) | 0.0 (0.0 to 49.0) |
| golden / nightmare/multi_address | several doors: fields checked, no single door (flagged in blind labeling) | 13 | 3 | 38.5 (17.7 to 64.5) | 23.1 (8.2 to 50.3) | 53.8 (29.1 to 76.8) | 7.7 (1.4 to 33.3) | 0.0 (0.0 to 22.8) | 0.0 (0.0 to 22.8) |
| golden / nightmare/non_address | not an address (flagged in blind labeling) | 2 | 1 | 50.0 (9.5 to 90.5) | 50.0 (9.5 to 90.5) | 0.0 (0.0 to 65.8) | 0.0 (0.0 to 65.8) | 0.0 (0.0 to 65.8) | 0.0 (0.0 to 65.8) |
| golden / normal | scored | 1,568 | 64 | 94.9 (93.7 to 95.9) | 93.6 (92.2 to 94.7) | 91.8 (90.3 to 93.0) | 33.0 (30.8 to 35.4) | 35.6 (33.3 to 38.0) | 0.0 (0.0 to 0.2) |
| libpostal-us / us | home set of libpostal (its own test_us_parses) | 53 | 2 | 84.9 (72.9 to 92.1) | 88.7 (77.4 to 94.7) | 94.3 (84.6 to 98.1) | 30.2 (19.5 to 43.5) | 9.4 (4.1 to 20.3) | 3.8 (1.0 to 12.8) |
| senzing-us / bug | cases reported as libpostal bugs | 6 | 0 | 100.0 (61.0 to 100.0) | 83.3 (43.6 to 97.0) | 100.0 (61.0 to 100.0) | 33.3 (9.7 to 70.0) | 16.7 (3.0 to 56.4) | 0.0 (0.0 to 39.0) |
| senzing-us / osm | scored | 2,172 | 6 | 98.1 (97.4 to 98.6) | 90.6 (89.3 to 91.7) | 98.8 (98.3 to 99.2) | 3.4 (2.7 to 4.2) | 49.2 (47.1 to 51.3) | 0.0 (0.0 to 0.2) |
| usaddress-tests / labeled | home set of usaddress (its own regression tests) | 146 | 0 | 82.9 (75.9 to 88.1) | 100.0 (97.4 to 100.0) | 68.5 (60.6 to 75.5), 1 errors | 26.0 (19.6 to 33.7) | 9.6 (5.8 to 15.5) | 7.5 (4.3 to 13.0) |
| usaddress-tests / multi_word_state_addresses | home set of usaddress (its own regression tests) | 5 | 0 | 40.0 (11.8 to 76.9) | 100.0 (56.6 to 100.0) | 80.0 (37.6 to 96.4) | 0.0 (0.0 to 43.4) | 0.0 (0.0 to 43.4) | 0.0 (0.0 to 43.4) |
| usaddress-tests / simple_address_patterns | home set of usaddress (its own regression tests) | 8 | 0 | 87.5 (52.9 to 97.8) | 100.0 (67.6 to 100.0) | 87.5 (52.9 to 97.8) | 0.0 (0.0 to 32.4) | 50.0 (21.5 to 78.5) | 0.0 (0.0 to 32.4) |
| usaddress-tests / synthetic_clean_osm_data | home set of usaddress (its own regression tests) | 4,120 | 6 | 99.8 (99.6 to 99.9) | 99.8 (99.6 to 99.9) | 99.8 (99.6 to 99.9) | 0.0 (0.0 to 0.1) | 0.2 (0.1 to 0.4) | 0.0 (0.0 to 0.1) |
| usaddress-tests / synthetic_osm_data | home set of usaddress (its own regression tests) | 4,122 | 0 | 99.9 (99.8 to 100.0) | 100.0 (99.9 to 100.0) | 99.9 (99.8 to 100.0) | 0.0 (0.0 to 0.1) | 0.1 (0.1 to 0.3) | 0.0 (0.0 to 0.1) |
| usaddress-tests / us50_test_tagged | home set of usaddress (its own regression tests) | 687 | 0 | 96.8 (95.2 to 97.9) | 100.0 (99.4 to 100.0) | 95.3 (93.5 to 96.7) | 5.1 (3.7 to 7.0) | 45.1 (41.4 to 48.9) | 0.0 (0.0 to 0.6) |

No parser right is a count only: it never drops or moves a record.

## Records reported apart from scored parts (marked when over 15% of the part)

| Set / part | In the score | Reported apart | Share apart |
|---|---|---|---|
| golden / hard | 556 | ambiguous 14, doubtful 17, multi_address 11, non_address 13 | 9.0% |
| golden / nightmare | 226 | ambiguous 7, doubtful 8, intersection 4, multi_address 13, non_address 2 | 13.1% |

## Field F1 by coarse field (micro over each set's scored parts and parts reported apart)

| Set / part | Field | doorplate | usaddress | libpostal | address_parser | addrust | us_address_parser |
|---|---|---|---|---|---|---|---|
| doorplate-suite / hand | city | 99.3 | 98.2 | 97.7 | 78.1 | 70.7 | 0.0 |
| doorplate-suite / hand | house_number | 99.9 | 98.7 | 97.8 | 90.8 | 88.4 | 88.8 |
| doorplate-suite / hand | po_box | 100.0 | 79.8 | 66.2 | 0.0 | 39.2 | 0.0 |
| doorplate-suite / hand | postal_code | 100.0 | 100.0 | 99.4 | 81.8 | 71.7 | 0.0 |
| doorplate-suite / hand | route | 96.3 | 71.8 | 0.0 | 0.0 | 0.0 | 0.0 |
| doorplate-suite / hand | state | 100.0 | 99.8 | 98.4 | 81.1 | 70.3 | 0.0 |
| doorplate-suite / hand | street | 96.4 | 96.6 | 89.0 | 40.2 | 22.1 | 1.5 |
| doorplate-suite / hand | unit | 99.8 | 91.2 | 90.5 | 60.7 | 26.2 | 0.0 |
| doorplate-suite / hard | city | 89.2 | 73.4 | 97.3 | 68.8 | 58.3 | 0.0 |
| doorplate-suite / hard | house_number | 99.5 | 87.0 | 89.1 | 83.3 | 90.2 | 83.7 |
| doorplate-suite / hard | po_box | - | 0.0 | - | - | - | - |
| doorplate-suite / hard | postal_code | 100.0 | 100.0 | 99.8 | 84.5 | 60.9 | 0.0 |
| doorplate-suite / hard | state | 99.7 | 96.4 | 99.9 | 83.5 | 60.7 | 0.0 |
| doorplate-suite / hard | street | 80.7 | 50.6 | 72.7 | 5.2 | 25.6 | 0.4 |
| doorplate-suite / hard | unit | 77.0 | 34.3 | 82.0 | 46.2 | 37.2 | 0.0 |
| doorplate-suite / natural | city | 99.3 | 98.6 | 98.8 | 90.4 | 74.7 | 0.0 |
| doorplate-suite / natural | house_number | 100.0 | 99.9 | 99.8 | 96.7 | 98.0 | 97.6 |
| doorplate-suite / natural | po_box | 100.0 | 84.8 | 77.6 | 0.0 | 52.7 | 0.0 |
| doorplate-suite / natural | postal_code | 100.0 | 100.0 | 99.9 | 94.6 | 76.4 | 0.0 |
| doorplate-suite / natural | route | 91.9 | 66.4 | 0.0 | 0.0 | 0.0 | 0.0 |
| doorplate-suite / natural | state | 100.0 | 99.9 | 99.4 | 94.5 | 75.8 | 0.0 |
| doorplate-suite / natural | street | 98.9 | 98.0 | 96.3 | 8.1 | 40.6 | 0.9 |
| doorplate-suite / natural | unit | 97.1 | 92.1 | 91.1 | 59.9 | 26.0 | 0.0 |
| geocode-dev / dev | city | 96.0 | 92.8 | 86.1 | 75.5 | 0.0 | 0.0 |
| geocode-dev / dev | house_number | 100.0 | 99.5 | 99.6 | 99.2 | 97.6 | 99.3 |
| geocode-dev / dev | po_box | - | 0.0 | 0.0 | - | - | - |
| geocode-dev / dev | postal_code | 100.0 | 100.0 | 99.7 | 93.8 | 0.0 | 0.0 |
| geocode-dev / dev | route | 0.0 | 0.0 | - | - | - | - |
| geocode-dev / dev | state | 99.8 | 97.5 | 99.2 | 90.8 | 0.0 | 0.0 |
| geocode-dev / dev | street | 94.6 | 92.2 | 80.6 | 72.3 | 0.4 | 0.8 |
| geocode-dev / dev | unit | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| golden / hard | city | 99.6 | 98.1 | 96.5 | 81.4 | 89.0 | 0.0 |
| golden / hard | house_number | 97.2 | 96.3 | 90.0 | 81.6 | 81.2 | 78.2 |
| golden / hard | po_box | 92.3 | 81.1 | 45.7 | 0.0 | 18.6 | 0.0 |
| golden / hard | postal_code | 99.3 | 99.3 | 98.8 | 78.4 | 90.6 | 0.0 |
| golden / hard | route | 94.0 | 93.5 | 0.0 | 0.0 | 0.0 | 0.0 |
| golden / hard | state | 98.6 | 98.2 | 99.0 | 80.2 | 88.2 | 0.0 |
| golden / hard | street | 94.0 | 92.3 | 78.4 | 64.5 | 19.9 | 1.0 |
| golden / hard | unit | 92.6 | 87.9 | 61.3 | 50.0 | 22.7 | 0.0 |
| golden / hard/ambiguous | city | 85.7 | 92.9 | 88.9 | 75.0 | 69.6 | 0.0 |
| golden / hard/ambiguous | house_number | 90.9 | 87.0 | 81.8 | 90.0 | 87.0 | 90.0 |
| golden / hard/ambiguous | po_box | 85.7 | 80.0 | 50.0 | 0.0 | 0.0 | 0.0 |
| golden / hard/ambiguous | postal_code | 100.0 | 100.0 | 100.0 | 81.8 | 81.8 | 0.0 |
| golden / hard/ambiguous | route | 0.0 | - | 0.0 | 0.0 | 0.0 | 0.0 |
| golden / hard/ambiguous | state | 100.0 | 100.0 | 100.0 | 83.3 | 78.3 | 0.0 |
| golden / hard/ambiguous | street | 78.3 | 88.9 | 53.8 | 72.7 | 17.4 | 0.0 |
| golden / hard/ambiguous | unit | 57.1 | 50.0 | 50.0 | 0.0 | 0.0 | 0.0 |
| golden / hard/doubtful | city | 70.6 | 74.3 | 66.7 | 68.8 | 69.0 | 0.0 |
| golden / hard/doubtful | house_number | 100.0 | 100.0 | 94.1 | 96.8 | 97.0 | 100.0 |
| golden / hard/doubtful | po_box | 0.0 | 0.0 | 100.0 | 0.0 | 100.0 | 0.0 |
| golden / hard/doubtful | postal_code | 100.0 | 100.0 | 100.0 | 90.3 | 82.8 | 0.0 |
| golden / hard/doubtful | route | 0.0 | 0.0 | - | 0.0 | 0.0 | 0.0 |
| golden / hard/doubtful | state | 100.0 | 100.0 | 100.0 | 93.8 | 82.8 | 0.0 |
| golden / hard/doubtful | street | 78.8 | 78.8 | 64.7 | 32.3 | 17.6 | 0.0 |
| golden / hard/doubtful | unit | 18.2 | 16.7 | 18.2 | 22.2 | 22.2 | 0.0 |
| golden / hard/multi_address | city | 100.0 | 100.0 | 100.0 | 70.6 | 95.2 | 0.0 |
| golden / hard/multi_address | house_number | 100.0 | 100.0 | 100.0 | 70.6 | 100.0 | 66.7 |
| golden / hard/multi_address | po_box | 100.0 | 95.2 | 95.2 | 0.0 | 18.2 | 0.0 |
| golden / hard/multi_address | postal_code | 100.0 | 100.0 | 100.0 | 70.6 | 95.2 | 0.0 |
| golden / hard/multi_address | state | 100.0 | 100.0 | 100.0 | 70.6 | 95.2 | 0.0 |
| golden / hard/multi_address | street | 100.0 | 100.0 | 95.7 | 70.6 | 27.3 | 0.0 |
| golden / hard/multi_address | unit | - | 0.0 | - | 0.0 | 0.0 | 0.0 |
| golden / hard/non_address | city | 100.0 | 92.3 | 91.7 | 0.0 | 47.1 | 0.0 |
| golden / hard/non_address | house_number | - | - | - | - | 0.0 | - |
| golden / hard/non_address | po_box | 100.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| golden / hard/non_address | postal_code | 100.0 | 100.0 | 91.7 | 0.0 | 47.1 | 0.0 |
| golden / hard/non_address | state | 100.0 | 100.0 | 91.7 | 0.0 | 47.1 | 0.0 |
| golden / hard/non_address | street | 0.0 | - | 0.0 | - | 0.0 | 0.0 |
| golden / hard/non_address | unit | - | - | - | - | 0.0 | - |
| golden / nightmare | city | 97.8 | 96.9 | 91.7 | 78.3 | 89.1 | 0.0 |
| golden / nightmare | house_number | 96.1 | 88.5 | 84.1 | 79.1 | 75.9 | 80.5 |
| golden / nightmare | po_box | 94.1 | 30.3 | 17.1 | 0.0 | 11.1 | 0.0 |
| golden / nightmare | postal_code | 97.3 | 99.1 | 94.4 | 80.4 | 90.6 | 0.0 |
| golden / nightmare | route | 60.0 | 19.5 | 0.0 | 0.0 | 0.0 | 0.0 |
| golden / nightmare | state | 100.0 | 99.3 | 93.7 | 80.4 | 90.6 | 0.0 |
| golden / nightmare | street | 87.4 | 72.1 | 69.5 | 43.4 | 23.8 | 0.0 |
| golden / nightmare | unit | 69.3 | 41.2 | 64.5 | 51.6 | 42.3 | 0.0 |
| golden / nightmare/ambiguous | city | 100.0 | 100.0 | 100.0 | 60.0 | 100.0 | 0.0 |
| golden / nightmare/ambiguous | house_number | 100.0 | 100.0 | 88.9 | 85.7 | 72.7 | 66.7 |
| golden / nightmare/ambiguous | postal_code | 100.0 | 100.0 | 100.0 | 60.0 | 100.0 | 0.0 |
| golden / nightmare/ambiguous | route | 0.0 | - | - | 0.0 | 0.0 | 0.0 |
| golden / nightmare/ambiguous | state | 100.0 | 100.0 | 100.0 | 60.0 | 100.0 | 0.0 |
| golden / nightmare/ambiguous | street | 54.5 | 66.7 | 71.4 | 22.2 | 0.0 | 0.0 |
| golden / nightmare/ambiguous | unit | 25.0 | 28.6 | 66.7 | 0.0 | 57.1 | 0.0 |
| golden / nightmare/doubtful | city | 93.3 | 100.0 | 93.3 | 85.7 | 93.3 | 0.0 |
| golden / nightmare/doubtful | house_number | 92.3 | 72.7 | 76.9 | 92.3 | 71.4 | 83.3 |
| golden / nightmare/doubtful | po_box | 0.0 | 100.0 | 100.0 | 0.0 | 100.0 | 0.0 |
| golden / nightmare/doubtful | postal_code | 93.3 | 93.3 | 93.3 | 92.3 | 100.0 | 0.0 |
| golden / nightmare/doubtful | route | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| golden / nightmare/doubtful | state | 100.0 | 100.0 | 93.3 | 85.7 | 93.3 | 0.0 |
| golden / nightmare/doubtful | street | 80.0 | 22.2 | 50.0 | 66.7 | 22.2 | 0.0 |
| golden / nightmare/doubtful | unit | 57.1 | 0.0 | 66.7 | 0.0 | 0.0 | 0.0 |
| golden / nightmare/intersection | city | 100.0 | 100.0 | 100.0 | 66.7 | 100.0 | 0.0 |
| golden / nightmare/intersection | house_number | 100.0 | 80.0 | 100.0 | 100.0 | 100.0 | 100.0 |
| golden / nightmare/intersection | postal_code | 100.0 | 100.0 | 100.0 | 66.7 | 100.0 | 0.0 |
| golden / nightmare/intersection | route | 0.0 | - | 0.0 | 0.0 | 0.0 | 0.0 |
| golden / nightmare/intersection | state | 100.0 | 100.0 | 100.0 | 66.7 | 100.0 | 0.0 |
| golden / nightmare/intersection | street | 66.7 | 93.3 | 0.0 | 0.0 | 0.0 | 0.0 |
| golden / nightmare/multi_address | city | 100.0 | 96.3 | 96.0 | 100.0 | 100.0 | 0.0 |
| golden / nightmare/multi_address | house_number | 40.0 | 34.8 | 61.5 | 23.1 | 0.0 | 0.0 |
| golden / nightmare/multi_address | postal_code | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 0.0 |
| golden / nightmare/multi_address | state | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 0.0 |
| golden / nightmare/multi_address | street | 92.3 | 57.1 | 53.8 | 7.7 | 0.0 | 0.0 |
| golden / nightmare/multi_address | unit | 66.7 | 28.6 | 100.0 | 0.0 | 0.0 | 0.0 |
| golden / nightmare/non_address | city | 100.0 | 100.0 | 66.7 | 0.0 | 66.7 | 0.0 |
| golden / nightmare/non_address | house_number | - | - | - | - | 0.0 | 0.0 |
| golden / nightmare/non_address | po_box | - | 0.0 | 0.0 | - | 0.0 | - |
| golden / nightmare/non_address | postal_code | 100.0 | 100.0 | 66.7 | 0.0 | 66.7 | 0.0 |
| golden / nightmare/non_address | route | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| golden / nightmare/non_address | state | 100.0 | 100.0 | 66.7 | 0.0 | 66.7 | 0.0 |
| golden / nightmare/non_address | street | 0.0 | - | 0.0 | - | 0.0 | 0.0 |
| golden / nightmare/non_address | unit | 100.0 | 66.7 | 0.0 | 0.0 | 0.0 | 0.0 |
| golden / normal | city | 99.5 | 98.7 | 98.9 | 94.7 | 91.2 | 0.0 |
| golden / normal | house_number | 98.7 | 98.6 | 97.4 | 98.1 | 98.0 | 97.4 |
| golden / normal | po_box | 100.0 | 99.5 | 98.9 | 0.0 | 49.7 | 0.0 |
| golden / normal | postal_code | 100.0 | 100.0 | 99.9 | 96.0 | 92.2 | 0.0 |
| golden / normal | route | - | - | - | 0.0 | 0.0 | - |
| golden / normal | state | 99.9 | 99.6 | 99.9 | 96.3 | 92.1 | 0.0 |
| golden / normal | street | 98.4 | 97.8 | 94.9 | 38.8 | 36.0 | 0.3 |
| golden / normal | unit | 84.3 | 81.9 | 80.0 | 62.6 | 41.5 | 0.0 |
| libpostal-us / us | city | 88.9 | 90.7 | 95.9 | 59.5 | 45.5 | 0.0 |
| libpostal-us / us | house_number | 98.6 | 100.0 | 100.0 | 76.7 | 85.3 | 83.1 |
| libpostal-us / us | po_box | 100.0 | 100.0 | 100.0 | 0.0 | 66.7 | 0.0 |
| libpostal-us / us | postal_code | 100.0 | 100.0 | 100.0 | 77.8 | 65.3 | 0.0 |
| libpostal-us / us | state | 97.7 | 97.7 | 98.8 | 67.7 | 49.1 | 0.0 |
| libpostal-us / us | street | 92.5 | 98.7 | 97.4 | 57.1 | 4.3 | 4.3 |
| libpostal-us / us | unit | 80.0 | 92.3 | 96.0 | 70.0 | 13.3 | 0.0 |
| senzing-us / bug | city | 100.0 | 90.9 | 100.0 | 66.7 | 75.0 | 0.0 |
| senzing-us / bug | house_number | 100.0 | 100.0 | 100.0 | 80.0 | 100.0 | 100.0 |
| senzing-us / bug | postal_code | 100.0 | 100.0 | 100.0 | 88.9 | 75.0 | 0.0 |
| senzing-us / bug | state | 100.0 | 90.9 | 100.0 | 80.0 | 66.7 | 0.0 |
| senzing-us / bug | street | 100.0 | 92.3 | 100.0 | 40.0 | 14.3 | 0.0 |
| senzing-us / bug | unit | 100.0 | 100.0 | 100.0 | 50.0 | 40.0 | 0.0 |
| senzing-us / osm | city | 99.4 | 94.4 | 99.6 | 80.1 | 78.5 | 0.0 |
| senzing-us / osm | house_number | 99.9 | 99.8 | 99.9 | 80.3 | 99.6 | 99.6 |
| senzing-us / osm | postal_code | 100.0 | 100.0 | 100.0 | 80.1 | 80.2 | 0.0 |
| senzing-us / osm | state | 99.3 | 95.3 | 100.0 | 94.5 | 92.5 | 0.0 |
| senzing-us / osm | street | 99.2 | 97.5 | 98.9 | 4.2 | 49.8 | 0.4 |
| senzing-us / osm | unit | 94.8 | 81.2 | 97.6 | 6.5 | 25.4 | 0.0 |
| usaddress-tests / labeled | city | 96.2 | 100.0 | 91.4 | 64.1 | 35.1 | 0.0 |
| usaddress-tests / labeled | house_number | 98.3 | 100.0 | 98.3 | 83.7 | 89.7 | 94.3 |
| usaddress-tests / labeled | po_box | 69.6 | 100.0 | 63.4 | 0.0 | 30.8 | 0.0 |
| usaddress-tests / labeled | postal_code | 99.5 | 100.0 | 99.5 | 81.9 | 38.0 | 0.0 |
| usaddress-tests / labeled | route | 100.0 | 100.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| usaddress-tests / labeled | state | 99.5 | 100.0 | 97.6 | 77.6 | 34.9 | 0.0 |
| usaddress-tests / labeled | street | 84.3 | 100.0 | 79.2 | 42.3 | 8.5 | 8.8 |
| usaddress-tests / labeled | unit | 78.9 | 100.0 | 88.9 | 57.1 | 11.8 | 0.0 |
| usaddress-tests / multi_word_state_addresses | city | 57.1 | 100.0 | 80.0 | 0.0 | 0.0 | 0.0 |
| usaddress-tests / multi_word_state_addresses | house_number | 100.0 | 100.0 | 100.0 | 0.0 | 100.0 | 100.0 |
| usaddress-tests / multi_word_state_addresses | postal_code | 100.0 | 100.0 | 100.0 | 0.0 | 0.0 | 0.0 |
| usaddress-tests / multi_word_state_addresses | state | 100.0 | 100.0 | 80.0 | 0.0 | 0.0 | 0.0 |
| usaddress-tests / multi_word_state_addresses | street | 40.0 | 100.0 | 100.0 | 0.0 | 0.0 | 0.0 |
| usaddress-tests / simple_address_patterns | city | 100.0 | 100.0 | 100.0 | 85.7 | 93.3 | 0.0 |
| usaddress-tests / simple_address_patterns | house_number | 100.0 | 100.0 | 100.0 | 92.3 | 100.0 | 100.0 |
| usaddress-tests / simple_address_patterns | po_box | 0.0 | 100.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| usaddress-tests / simple_address_patterns | postal_code | 100.0 | 100.0 | 100.0 | 85.7 | 93.3 | 0.0 |
| usaddress-tests / simple_address_patterns | state | 100.0 | 100.0 | 100.0 | 92.3 | 100.0 | 0.0 |
| usaddress-tests / simple_address_patterns | street | 93.3 | 100.0 | 100.0 | 0.0 | 53.3 | 0.0 |
| usaddress-tests / simple_address_patterns | unit | 0.0 | - | - | - | 0.0 | - |
| usaddress-tests / synthetic_clean_osm_data | city | 100.0 | 100.0 | 100.0 | 1.9 | 1.3 | 0.0 |
| usaddress-tests / synthetic_clean_osm_data | house_number | 99.9 | 99.9 | 99.9 | 21.6 | 97.9 | 97.9 |
| usaddress-tests / synthetic_clean_osm_data | postal_code | 100.0 | 100.0 | 100.0 | 20.7 | 1.2 | 0.0 |
| usaddress-tests / synthetic_clean_osm_data | state | 99.3 | 99.3 | 98.6 | 98.6 | 48.9 | 0.0 |
| usaddress-tests / synthetic_clean_osm_data | street | 100.0 | 100.0 | 99.9 | 0.0 | 0.3 | 0.9 |
| usaddress-tests / synthetic_clean_osm_data | unit | 40.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| usaddress-tests / synthetic_osm_data | city | 100.0 | 100.0 | 100.0 | 1.8 | 1.5 | 0.0 |
| usaddress-tests / synthetic_osm_data | house_number | 100.0 | 100.0 | 100.0 | 21.7 | 97.9 | 97.9 |
| usaddress-tests / synthetic_osm_data | postal_code | 100.0 | 100.0 | 100.0 | 20.8 | 1.3 | 0.0 |
| usaddress-tests / synthetic_osm_data | state | 100.0 | 100.0 | 100.0 | 98.7 | 49.5 | 0.0 |
| usaddress-tests / synthetic_osm_data | street | 99.9 | 100.0 | 99.9 | 0.0 | 0.2 | 1.1 |
| usaddress-tests / synthetic_osm_data | unit | 0.0 | - | - | - | 0.0 | 0.0 |
| usaddress-tests / us50_test_tagged | city | 100.0 | 100.0 | 99.3 | 92.3 | 99.1 | 0.0 |
| usaddress-tests / us50_test_tagged | house_number | 99.7 | 100.0 | 99.6 | 99.4 | 97.5 | 98.5 |
| usaddress-tests / us50_test_tagged | po_box | 44.4 | 100.0 | 30.8 | 0.0 | 30.8 | 0.0 |
| usaddress-tests / us50_test_tagged | postal_code | 100.0 | 100.0 | 100.0 | 92.7 | 99.6 | 0.0 |
| usaddress-tests / us50_test_tagged | route | 0.0 | 100.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| usaddress-tests / us50_test_tagged | state | 100.0 | 100.0 | 100.0 | 92.7 | 99.6 | 0.0 |
| usaddress-tests / us50_test_tagged | street | 95.4 | 100.0 | 95.6 | 5.7 | 41.9 | 1.3 |
| usaddress-tests / us50_test_tagged | unit | 70.0 | 100.0 | 77.8 | 96.6 | 61.5 | 0.0 |

## Fine track (reported apart; every gold leaf label counts for every parser; gold fully fine-labeled)

| Set / part | Records | doorplate record accuracy | usaddress record accuracy | libpostal record accuracy | address_parser record accuracy | addrust record accuracy | us_address_parser record accuracy |
|---|---|---|---|---|---|---|---|
| doorplate-suite / hand | 1,000 of 1,000 | 94.5 | 89.1 | 0.0 | 0.0 | 0.0 | 0.0 |
| doorplate-suite / hard | 2,521 of 2,585 | 70.2 | 23.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| doorplate-suite / natural | 15,982 of 16,001 | 98.1 | 95.9 | 0.0 | 0.0 | 0.0 | 0.0 |
| geocode-dev / dev | 60,522 of 60,522 | 84.3 | 80.3 | 0.0 | 0.0 | 0.0 | 0.0 |
| golden / hard | 556 of 556 | 66.2 | 58.5 | 0.4 | 0.2 | 0.4 | 0.0 |
| golden / hard/ambiguous | 14 of 14 | 42.9 | 42.9 | 7.1 | 0.0 | 0.0 | 0.0 |
| golden / hard/doubtful | 17 of 17 | 23.5 | 23.5 | 0.0 | 0.0 | 0.0 | 0.0 |
| golden / hard/multi_address | 11 of 11 | 100.0 | 90.9 | 0.0 | 0.0 | 0.0 | 0.0 |
| golden / hard/non_address | 13 of 13 | 100.0 | 30.8 | 15.4 | 0.0 | 30.8 | 0.0 |
| golden / nightmare | 226 of 226 | 62.4 | 43.4 | 0.0 | 0.0 | 0.0 | 0.0 |
| golden / nightmare/ambiguous | 7 of 7 | 42.9 | 42.9 | 0.0 | 0.0 | 0.0 | 0.0 |
| golden / nightmare/doubtful | 8 of 8 | 25.0 | 25.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| golden / nightmare/intersection | 4 of 4 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| golden / nightmare/multi_address | 13 of 13 | 38.5 | 23.1 | 0.0 | 0.0 | 0.0 | 0.0 |
| golden / nightmare/non_address | 2 of 2 | 50.0 | 50.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| golden / normal | 1,568 of 1,568 | 94.4 | 93.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| libpostal-us / us | 11 of 53 | 81.8 | 72.7 | 90.9 | 0.0 | 9.1 | 0.0 |
| senzing-us / bug | 0 of 6 | - | - | - | - | - | - |
| senzing-us / osm | 0 of 2,172 | - | - | - | - | - | - |
| usaddress-tests / labeled | 146 of 146 | 73.3 | 100.0 | 0.0 | 0.0 | 0.0 | 4.1 |
| usaddress-tests / multi_word_state_addresses | 5 of 5 | 40.0 | 100.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| usaddress-tests / simple_address_patterns | 8 of 8 | 87.5 | 100.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| usaddress-tests / synthetic_clean_osm_data | 4,120 of 4,120 | 99.8 | 99.8 | 0.0 | 0.0 | 0.0 | 0.0 |
| usaddress-tests / synthetic_osm_data | 4,122 of 4,122 | 99.8 | 100.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| usaddress-tests / us50_test_tagged | 687 of 687 | 9.5 | 9.9 | 6.7 | 0.0 | 6.3 | 0.0 |
- doorplate produces these fine labels: building_name, city, country, house_number_prefix, house_number_suffix, house_number_value, po_box_type, po_box_value, postal_code, recipient, route_box_type, route_box_value, route_type, route_value, state, street_name, street_post_direction, street_post_type, street_pre_direction, street_pre_type, unit_type, unit_value. A field it labels only as a whole counts as a miss here.
- usaddress produces these fine labels: building_name, city, country, house_number_prefix, house_number_suffix, house_number_value, po_box_type, po_box_value, postal_code, recipient, route_box_type, route_box_value, route_type, route_value, state, street_name, street_post_direction, street_post_type, street_pre_direction, street_pre_type, unit_type, unit_value. A field it labels only as a whole counts as a miss here.
- libpostal produces these fine labels: building_name, city, country, postal_code, state. A field it labels only as a whole counts as a miss here.
- address_parser produces these fine labels: city, postal_code, state, street_name, street_post_direction, street_post_type, street_pre_direction, unit_type, unit_value. A field it labels only as a whole counts as a miss here.
- addrust produces these fine labels: building_name, city, postal_code, state, street_name, street_post_direction, street_post_type, street_pre_direction, unit_type, unit_value. A field it labels only as a whole counts as a miss here.
- us_address_parser produces these fine labels: house_number_value, street_name, street_post_direction, street_post_type, street_pre_direction, unit_type, unit_value. A field it labels only as a whole counts as a miss here.

Per fine label F1 is in `results.json` (`fine_f1`).

## Parser Score

Parts used: golden/normal, golden/hard, golden/nightmare, doorplate-suite/natural, doorplate-suite/hand, senzing-us/osm, geocode-dev/dev. Bootstrap: 1000 resamples, seed 20261113.

| Parser | Parser Score (95% interval) | Field F1 score (95% interval) |
|---|---|---|
| doorplate | 91.8 (90.7 to 92.9) | 97.9 (97.6 to 98.1) |
| usaddress | 84.7 (83.4 to 86.0) | 95.7 (95.3 to 96.1) |
| libpostal | 80.8 (79.5 to 82.2) | 93.4 (92.8 to 93.9) |
| address_parser | 29.4 (28.1 to 30.7) | 75.6 (74.7 to 76.4) |
| addrust | 24.0 (23.0 to 25.1) | 65.2 (64.4 to 65.9) |
| us_address_parser | 0.0 (0.0 to 0.0) | 23.1 (22.8 to 23.4) |

## Sensitivity (Parser Score)

| Weights | doorplate | usaddress | libpostal | address_parser | addrust | us_address_parser |
|---|---|---|---|---|---|---|
| formula weights | 91.8 | 84.7 | 80.8 | 29.4 | 24.0 | 0.0 | ranking: doorplate > usaddress > libpostal > address_parser > addrust > us_address_parser |
| equal weights | 92.5 | 85.7 | 82.1 | 28.8 | 24.4 | 0.0 | ranking: doorplate > usaddress > libpostal > address_parser > addrust > us_address_parser |
| with the doubtful records | 91.3 | 84.3 | 80.6 | 29.4 | 24.0 | 0.0 | ranking: doorplate > usaddress > libpostal > address_parser > addrust > us_address_parser |
| without doorplate-suite | 89.9 | 81.7 | 77.9 | 33.7 | 22.2 | 0.0 | ranking: doorplate > usaddress > libpostal > address_parser > addrust > us_address_parser |
| without geocode-dev | 91.4 | 84.2 | 80.9 | 24.4 | 27.4 | 0.0 | ranking: doorplate > usaddress > libpostal > addrust > address_parser > us_address_parser |
| without golden | 96.8 | 91.6 | 89.4 | 25.2 | 27.0 | 0.0 | ranking: doorplate > usaddress > libpostal > addrust > address_parser > us_address_parser |
| without senzing-us | 90.9 | 83.9 | 78.2 | 33.1 | 20.4 | 0.0 | ranking: doorplate > usaddress > libpostal > address_parser > addrust > us_address_parser |
