## Record accuracy by part (coarse track, 95% Wilson interval)

| Set / part | Role | Records | No parser right | doorplate | libpostal | usaddress |
|---|---|---|---|---|---|---|
| doorplate-suite / hand | scored | 1,000 | 15 | 95.9 (94.5 to 97.0) | 84.0 (81.6 to 86.1) | 91.1 (89.2 to 92.7) |
| doorplate-suite / hard | drawn from the blind spots of two of the three parsers | 2,585 | 146 | 81.2 (79.7 to 82.7) | 69.0 (67.2 to 70.8) | 25.7 (24.1 to 27.4) |
| doorplate-suite / natural | scored | 16,001 | 53 | 98.8 (98.6 to 99.0) | 95.0 (94.6 to 95.3) | 96.5 (96.2 to 96.7) |
| geocode-dev / dev | scored | 60,522 | 830 | 94.5 (94.3 to 94.7) | 79.9 (79.6 to 80.2) | 88.4 (88.1 to 88.6) |
| golden / hard | scored | 556 | 28 | 91.0 (88.3 to 93.1) | 70.9 (67.0 to 74.5) | 88.5 (85.6 to 90.9) |
| golden / hard/ambiguous | one door, several readings (flagged in blind labeling) | 14 | 4 | 57.1 (32.6 to 78.6) | 50.0 (26.8 to 73.2) | 71.4 (45.4 to 88.3) |
| golden / hard/doubtful | doubtful label (the Parser Score is also shown with these records in) | 17 | 10 | 29.4 (13.3 to 53.1) | 23.5 (9.6 to 47.3) | 35.3 (17.3 to 58.7) |
| golden / hard/multi_address | several doors: fields checked, no single door (flagged in blind labeling) | 11 | 0 | 100.0 (74.1 to 100.0) | 90.9 (62.3 to 98.4) | 90.9 (62.3 to 98.4) |
| golden / hard/non_address | not an address (flagged in blind labeling) | 13 | 0 | 100.0 (77.2 to 100.0) | 15.4 (4.3 to 42.2) | 30.8 (12.7 to 57.6) |
| golden / nightmare | scored | 226 | 49 | 60.2 (53.7 to 66.3) | 54.0 (47.5 to 60.4) | 51.3 (44.8 to 57.8) |
| golden / nightmare/ambiguous | one door, several readings (flagged in blind labeling) | 7 | 1 | 28.6 (8.2 to 64.1) | 57.1 (25.0 to 84.2) | 57.1 (25.0 to 84.2) |
| golden / nightmare/doubtful | doubtful label (the Parser Score is also shown with these records in) | 8 | 2 | 25.0 (7.1 to 59.1) | 50.0 (21.5 to 78.5) | 25.0 (7.1 to 59.1) |
| golden / nightmare/intersection | a corner, no door (flagged in blind labeling) | 4 | 1 | 25.0 (4.6 to 69.9) | 0.0 (0.0 to 49.0) | 75.0 (30.1 to 95.4) |
| golden / nightmare/multi_address | several doors: fields checked, no single door (flagged in blind labeling) | 13 | 5 | 15.4 (4.3 to 42.2) | 53.8 (29.1 to 76.8) | 23.1 (8.2 to 50.3) |
| golden / nightmare/non_address | not an address (flagged in blind labeling) | 2 | 1 | 50.0 (9.5 to 90.5) | 0.0 (0.0 to 65.8) | 50.0 (9.5 to 90.5) |
| golden / normal | scored | 1,568 | 69 | 94.6 (93.4 to 95.7) | 91.8 (90.3 to 93.0) | 93.6 (92.2 to 94.7) |
| libpostal-us / us | home set of libpostal (its own test_us_parses) | 53 | 2 | 84.9 (72.9 to 92.1) | 94.3 (84.6 to 98.1) | 88.7 (77.4 to 94.7) |
| senzing-us / bug | cases reported as libpostal bugs | 6 | 0 | 100.0 (61.0 to 100.0) | 100.0 (61.0 to 100.0) | 83.3 (43.6 to 97.0) |
| senzing-us / osm | scored | 2,172 | 6 | 98.3 (97.7 to 98.8) | 98.8 (98.3 to 99.2) | 90.6 (89.3 to 91.7) |
| usaddress-tests / labeled | home set of usaddress (its own regression tests) | 146 | 0 | 82.2 (75.2 to 87.5) | 68.5 (60.6 to 75.5), 1 errors | 100.0 (97.4 to 100.0) |
| usaddress-tests / multi_word_state_addresses | home set of usaddress (its own regression tests) | 5 | 0 | 40.0 (11.8 to 76.9) | 80.0 (37.6 to 96.4) | 100.0 (56.6 to 100.0) |
| usaddress-tests / simple_address_patterns | home set of usaddress (its own regression tests) | 8 | 0 | 87.5 (52.9 to 97.8) | 87.5 (52.9 to 97.8) | 100.0 (67.6 to 100.0) |
| usaddress-tests / synthetic_clean_osm_data | home set of usaddress (its own regression tests) | 4,120 | 7 | 99.8 (99.6 to 99.9) | 99.8 (99.6 to 99.9) | 99.8 (99.6 to 99.9) |
| usaddress-tests / synthetic_osm_data | home set of usaddress (its own regression tests) | 4,122 | 0 | 99.9 (99.8 to 100.0) | 99.9 (99.8 to 100.0) | 100.0 (99.9 to 100.0) |
| usaddress-tests / us50_test_tagged | home set of usaddress (its own regression tests) | 687 | 0 | 96.8 (95.2 to 97.9) | 95.3 (93.5 to 96.7) | 100.0 (99.4 to 100.0) |

No parser right is a count only: it never drops or moves a record.

## Records reported apart from scored parts (marked when over 15% of the part)

| Set / part | In the score | Reported apart | Share apart |
|---|---|---|---|
| golden / hard | 556 | ambiguous 14, doubtful 17, multi_address 11, non_address 13 | 9.0% |
| golden / nightmare | 226 | ambiguous 7, doubtful 8, intersection 4, multi_address 13, non_address 2 | 13.1% |

## Field F1 by coarse field (micro over each set's scored parts and parts reported apart)

| Set / part | Field | doorplate | libpostal | usaddress |
|---|---|---|---|---|
| doorplate-suite / hand | city | 98.8 | 97.7 | 98.2 |
| doorplate-suite / hand | house_number | 99.6 | 97.8 | 98.7 |
| doorplate-suite / hand | po_box | 100.0 | 66.2 | 79.8 |
| doorplate-suite / hand | postal_code | 100.0 | 99.4 | 100.0 |
| doorplate-suite / hand | route | 96.3 | 0.0 | 71.8 |
| doorplate-suite / hand | state | 100.0 | 98.4 | 99.8 |
| doorplate-suite / hand | street | 96.3 | 89.0 | 96.6 |
| doorplate-suite / hand | unit | 100.0 | 90.5 | 91.2 |
| doorplate-suite / hard | city | 89.1 | 97.3 | 73.4 |
| doorplate-suite / hard | house_number | 99.5 | 89.1 | 87.0 |
| doorplate-suite / hard | po_box | - | - | 0.0 |
| doorplate-suite / hard | postal_code | 100.0 | 99.8 | 100.0 |
| doorplate-suite / hard | state | 99.7 | 99.9 | 96.4 |
| doorplate-suite / hard | street | 88.7 | 72.7 | 50.6 |
| doorplate-suite / hard | unit | 84.7 | 82.0 | 34.3 |
| doorplate-suite / natural | city | 99.3 | 98.8 | 98.6 |
| doorplate-suite / natural | house_number | 100.0 | 99.8 | 99.9 |
| doorplate-suite / natural | po_box | 100.0 | 77.6 | 84.8 |
| doorplate-suite / natural | postal_code | 100.0 | 99.9 | 100.0 |
| doorplate-suite / natural | route | 91.9 | 0.0 | 66.4 |
| doorplate-suite / natural | state | 100.0 | 99.4 | 99.9 |
| doorplate-suite / natural | street | 99.1 | 96.3 | 98.0 |
| doorplate-suite / natural | unit | 98.1 | 91.1 | 92.1 |
| geocode-dev / dev | city | 96.0 | 86.1 | 92.8 |
| geocode-dev / dev | house_number | 100.0 | 99.6 | 99.5 |
| geocode-dev / dev | po_box | - | 0.0 | 0.0 |
| geocode-dev / dev | postal_code | 100.0 | 99.7 | 100.0 |
| geocode-dev / dev | route | 0.0 | - | 0.0 |
| geocode-dev / dev | state | 99.8 | 99.2 | 97.5 |
| geocode-dev / dev | street | 94.7 | 80.6 | 92.2 |
| geocode-dev / dev | unit | 0.0 | 0.0 | 0.0 |
| golden / hard | city | 99.6 | 96.5 | 98.1 |
| golden / hard | house_number | 97.2 | 90.0 | 96.3 |
| golden / hard | po_box | 92.3 | 45.7 | 81.1 |
| golden / hard | postal_code | 99.3 | 98.8 | 99.3 |
| golden / hard | route | 94.0 | 0.0 | 93.5 |
| golden / hard | state | 98.6 | 99.0 | 98.2 |
| golden / hard | street | 92.3 | 78.4 | 92.3 |
| golden / hard | unit | 88.2 | 61.3 | 87.9 |
| golden / hard/ambiguous | city | 85.7 | 88.9 | 92.9 |
| golden / hard/ambiguous | house_number | 90.9 | 81.8 | 87.0 |
| golden / hard/ambiguous | po_box | 66.7 | 50.0 | 80.0 |
| golden / hard/ambiguous | postal_code | 100.0 | 100.0 | 100.0 |
| golden / hard/ambiguous | route | 0.0 | 0.0 | - |
| golden / hard/ambiguous | state | 100.0 | 100.0 | 100.0 |
| golden / hard/ambiguous | street | 83.3 | 53.8 | 88.9 |
| golden / hard/ambiguous | unit | 50.0 | 50.0 | 50.0 |
| golden / hard/doubtful | city | 70.6 | 66.7 | 74.3 |
| golden / hard/doubtful | house_number | 100.0 | 94.1 | 100.0 |
| golden / hard/doubtful | po_box | 0.0 | 100.0 | 0.0 |
| golden / hard/doubtful | postal_code | 100.0 | 100.0 | 100.0 |
| golden / hard/doubtful | route | 0.0 | - | 0.0 |
| golden / hard/doubtful | state | 100.0 | 100.0 | 100.0 |
| golden / hard/doubtful | street | 78.8 | 64.7 | 78.8 |
| golden / hard/doubtful | unit | 18.2 | 18.2 | 16.7 |
| golden / hard/multi_address | city | 100.0 | 100.0 | 100.0 |
| golden / hard/multi_address | house_number | 100.0 | 100.0 | 100.0 |
| golden / hard/multi_address | po_box | 100.0 | 95.2 | 95.2 |
| golden / hard/multi_address | postal_code | 100.0 | 100.0 | 100.0 |
| golden / hard/multi_address | state | 100.0 | 100.0 | 100.0 |
| golden / hard/multi_address | street | 100.0 | 95.7 | 100.0 |
| golden / hard/multi_address | unit | - | - | 0.0 |
| golden / hard/non_address | city | 100.0 | 91.7 | 92.3 |
| golden / hard/non_address | po_box | 100.0 | 0.0 | 0.0 |
| golden / hard/non_address | postal_code | 100.0 | 91.7 | 100.0 |
| golden / hard/non_address | state | 100.0 | 91.7 | 100.0 |
| golden / hard/non_address | street | 0.0 | 0.0 | - |
| golden / nightmare | city | 97.1 | 91.7 | 96.9 |
| golden / nightmare | house_number | 94.2 | 84.1 | 88.5 |
| golden / nightmare | po_box | 80.0 | 17.1 | 30.3 |
| golden / nightmare | postal_code | 95.3 | 94.4 | 99.1 |
| golden / nightmare | route | 62.5 | 0.0 | 19.5 |
| golden / nightmare | state | 99.3 | 93.7 | 99.3 |
| golden / nightmare | street | 76.4 | 69.5 | 72.1 |
| golden / nightmare | unit | 54.4 | 64.5 | 41.2 |
| golden / nightmare/ambiguous | city | 100.0 | 100.0 | 100.0 |
| golden / nightmare/ambiguous | house_number | 100.0 | 88.9 | 100.0 |
| golden / nightmare/ambiguous | postal_code | 100.0 | 100.0 | 100.0 |
| golden / nightmare/ambiguous | route | 0.0 | - | - |
| golden / nightmare/ambiguous | state | 100.0 | 100.0 | 100.0 |
| golden / nightmare/ambiguous | street | 36.4 | 71.4 | 66.7 |
| golden / nightmare/ambiguous | unit | 0.0 | 66.7 | 28.6 |
| golden / nightmare/doubtful | city | 100.0 | 93.3 | 100.0 |
| golden / nightmare/doubtful | house_number | 92.3 | 76.9 | 72.7 |
| golden / nightmare/doubtful | po_box | 0.0 | 100.0 | 100.0 |
| golden / nightmare/doubtful | postal_code | 93.3 | 93.3 | 93.3 |
| golden / nightmare/doubtful | route | 0.0 | 0.0 | 0.0 |
| golden / nightmare/doubtful | state | 100.0 | 93.3 | 100.0 |
| golden / nightmare/doubtful | street | 40.0 | 50.0 | 22.2 |
| golden / nightmare/doubtful | unit | 0.0 | 66.7 | 0.0 |
| golden / nightmare/intersection | city | 100.0 | 100.0 | 100.0 |
| golden / nightmare/intersection | house_number | 100.0 | 100.0 | 80.0 |
| golden / nightmare/intersection | postal_code | 100.0 | 100.0 | 100.0 |
| golden / nightmare/intersection | route | 0.0 | 0.0 | - |
| golden / nightmare/intersection | state | 100.0 | 100.0 | 100.0 |
| golden / nightmare/intersection | street | 66.7 | 0.0 | 93.3 |
| golden / nightmare/multi_address | city | 100.0 | 96.0 | 96.3 |
| golden / nightmare/multi_address | house_number | 26.1 | 61.5 | 34.8 |
| golden / nightmare/multi_address | postal_code | 100.0 | 100.0 | 100.0 |
| golden / nightmare/multi_address | state | 100.0 | 100.0 | 100.0 |
| golden / nightmare/multi_address | street | 61.5 | 53.8 | 57.1 |
| golden / nightmare/multi_address | unit | 0.0 | 100.0 | 28.6 |
| golden / nightmare/non_address | city | 100.0 | 66.7 | 100.0 |
| golden / nightmare/non_address | po_box | - | 0.0 | 0.0 |
| golden / nightmare/non_address | postal_code | 100.0 | 66.7 | 100.0 |
| golden / nightmare/non_address | route | 0.0 | 0.0 | 0.0 |
| golden / nightmare/non_address | state | 100.0 | 66.7 | 100.0 |
| golden / nightmare/non_address | street | 0.0 | 0.0 | - |
| golden / nightmare/non_address | unit | 100.0 | 0.0 | 66.7 |
| golden / normal | city | 99.5 | 98.9 | 98.7 |
| golden / normal | house_number | 98.7 | 97.4 | 98.6 |
| golden / normal | po_box | 100.0 | 98.9 | 99.5 |
| golden / normal | postal_code | 100.0 | 99.9 | 100.0 |
| golden / normal | state | 99.9 | 99.9 | 99.6 |
| golden / normal | street | 98.1 | 94.9 | 97.8 |
| golden / normal | unit | 83.4 | 80.0 | 81.9 |
| libpostal-us / us | city | 88.9 | 95.9 | 90.7 |
| libpostal-us / us | house_number | 98.6 | 100.0 | 100.0 |
| libpostal-us / us | po_box | 100.0 | 100.0 | 100.0 |
| libpostal-us / us | postal_code | 100.0 | 100.0 | 100.0 |
| libpostal-us / us | state | 97.7 | 98.8 | 97.7 |
| libpostal-us / us | street | 92.5 | 97.4 | 98.7 |
| libpostal-us / us | unit | 80.0 | 96.0 | 92.3 |
| senzing-us / bug | city | 100.0 | 100.0 | 90.9 |
| senzing-us / bug | house_number | 100.0 | 100.0 | 100.0 |
| senzing-us / bug | postal_code | 100.0 | 100.0 | 100.0 |
| senzing-us / bug | state | 100.0 | 100.0 | 90.9 |
| senzing-us / bug | street | 100.0 | 100.0 | 92.3 |
| senzing-us / bug | unit | 100.0 | 100.0 | 100.0 |
| senzing-us / osm | city | 99.4 | 99.6 | 94.4 |
| senzing-us / osm | house_number | 99.9 | 99.9 | 99.8 |
| senzing-us / osm | postal_code | 100.0 | 100.0 | 100.0 |
| senzing-us / osm | state | 99.3 | 100.0 | 95.3 |
| senzing-us / osm | street | 99.4 | 98.9 | 97.5 |
| senzing-us / osm | unit | 96.2 | 97.6 | 81.2 |
| usaddress-tests / labeled | city | 93.4 | 91.4 | 100.0 |
| usaddress-tests / labeled | house_number | 98.3 | 98.3 | 100.0 |
| usaddress-tests / labeled | po_box | 69.6 | 63.4 | 100.0 |
| usaddress-tests / labeled | postal_code | 99.5 | 99.5 | 100.0 |
| usaddress-tests / labeled | route | 100.0 | 0.0 | 100.0 |
| usaddress-tests / labeled | state | 99.5 | 97.6 | 100.0 |
| usaddress-tests / labeled | street | 85.1 | 79.2 | 100.0 |
| usaddress-tests / labeled | unit | 74.6 | 88.9 | 100.0 |
| usaddress-tests / multi_word_state_addresses | city | 57.1 | 80.0 | 100.0 |
| usaddress-tests / multi_word_state_addresses | house_number | 100.0 | 100.0 | 100.0 |
| usaddress-tests / multi_word_state_addresses | postal_code | 100.0 | 100.0 | 100.0 |
| usaddress-tests / multi_word_state_addresses | state | 100.0 | 80.0 | 100.0 |
| usaddress-tests / multi_word_state_addresses | street | 40.0 | 100.0 | 100.0 |
| usaddress-tests / simple_address_patterns | city | 100.0 | 100.0 | 100.0 |
| usaddress-tests / simple_address_patterns | house_number | 100.0 | 100.0 | 100.0 |
| usaddress-tests / simple_address_patterns | po_box | 0.0 | 0.0 | 100.0 |
| usaddress-tests / simple_address_patterns | postal_code | 100.0 | 100.0 | 100.0 |
| usaddress-tests / simple_address_patterns | state | 100.0 | 100.0 | 100.0 |
| usaddress-tests / simple_address_patterns | street | 93.3 | 100.0 | 100.0 |
| usaddress-tests / simple_address_patterns | unit | 0.0 | - | - |
| usaddress-tests / synthetic_clean_osm_data | city | 100.0 | 100.0 | 100.0 |
| usaddress-tests / synthetic_clean_osm_data | house_number | 99.9 | 99.9 | 99.9 |
| usaddress-tests / synthetic_clean_osm_data | postal_code | 100.0 | 100.0 | 100.0 |
| usaddress-tests / synthetic_clean_osm_data | state | 99.3 | 98.6 | 99.3 |
| usaddress-tests / synthetic_clean_osm_data | street | 100.0 | 99.9 | 100.0 |
| usaddress-tests / synthetic_clean_osm_data | unit | 0.0 | 0.0 | 0.0 |
| usaddress-tests / synthetic_osm_data | city | 100.0 | 100.0 | 100.0 |
| usaddress-tests / synthetic_osm_data | house_number | 100.0 | 100.0 | 100.0 |
| usaddress-tests / synthetic_osm_data | postal_code | 100.0 | 100.0 | 100.0 |
| usaddress-tests / synthetic_osm_data | state | 100.0 | 100.0 | 100.0 |
| usaddress-tests / synthetic_osm_data | street | 99.9 | 99.9 | 100.0 |
| usaddress-tests / us50_test_tagged | city | 100.0 | 99.3 | 100.0 |
| usaddress-tests / us50_test_tagged | house_number | 99.7 | 99.6 | 100.0 |
| usaddress-tests / us50_test_tagged | po_box | 44.4 | 30.8 | 100.0 |
| usaddress-tests / us50_test_tagged | postal_code | 100.0 | 100.0 | 100.0 |
| usaddress-tests / us50_test_tagged | route | 0.0 | 0.0 | 100.0 |
| usaddress-tests / us50_test_tagged | state | 100.0 | 100.0 | 100.0 |
| usaddress-tests / us50_test_tagged | street | 95.4 | 95.6 | 100.0 |
| usaddress-tests / us50_test_tagged | unit | 70.0 | 77.8 | 100.0 |

## Fine track (reported apart; every gold leaf label counts for every parser; gold fully fine-labeled)

| Set / part | Records | doorplate record accuracy | libpostal record accuracy | usaddress record accuracy |
|---|---|---|---|---|
| doorplate-suite / hand | 1,000 of 1,000 | 93.3 | 0.0 | 89.1 |
| doorplate-suite / hard | 2,521 of 2,585 | 55.9 | 0.0 | 23.0 |
| doorplate-suite / natural | 15,982 of 16,001 | 97.9 | 0.0 | 95.9 |
| geocode-dev / dev | 60,522 of 60,522 | 84.2 | 0.0 | 80.3 |
| golden / hard | 556 of 556 | 64.9 | 0.4 | 58.5 |
| golden / hard/ambiguous | 14 of 14 | 35.7 | 7.1 | 42.9 |
| golden / hard/doubtful | 17 of 17 | 23.5 | 0.0 | 23.5 |
| golden / hard/multi_address | 11 of 11 | 100.0 | 0.0 | 90.9 |
| golden / hard/non_address | 13 of 13 | 100.0 | 15.4 | 30.8 |
| golden / nightmare | 226 of 226 | 46.0 | 0.0 | 43.4 |
| golden / nightmare/ambiguous | 7 of 7 | 28.6 | 0.0 | 42.9 |
| golden / nightmare/doubtful | 8 of 8 | 12.5 | 0.0 | 25.0 |
| golden / nightmare/intersection | 4 of 4 | 0.0 | 0.0 | 0.0 |
| golden / nightmare/multi_address | 13 of 13 | 15.4 | 0.0 | 23.1 |
| golden / nightmare/non_address | 2 of 2 | 50.0 | 0.0 | 50.0 |
| golden / normal | 1,568 of 1,568 | 94.2 | 0.0 | 93.0 |
| libpostal-us / us | 11 of 53 | 81.8 | 90.9 | 72.7 |
| senzing-us / bug | 0 of 6 | - | - | - |
| senzing-us / osm | 0 of 2,172 | - | - | - |
| usaddress-tests / labeled | 146 of 146 | 72.6 | 0.0 | 100.0 |
| usaddress-tests / multi_word_state_addresses | 5 of 5 | 40.0 | 0.0 | 100.0 |
| usaddress-tests / simple_address_patterns | 8 of 8 | 87.5 | 0.0 | 100.0 |
| usaddress-tests / synthetic_clean_osm_data | 4,120 of 4,120 | 99.8 | 0.0 | 99.8 |
| usaddress-tests / synthetic_osm_data | 4,122 of 4,122 | 99.8 | 0.0 | 100.0 |
| usaddress-tests / us50_test_tagged | 687 of 687 | 9.5 | 6.7 | 9.9 |
- doorplate produces these fine labels: building_name, city, country, house_number_prefix, house_number_suffix, house_number_value, po_box_type, po_box_value, postal_code, recipient, route_box_type, route_box_value, route_type, route_value, state, street_name, street_post_direction, street_post_type, street_pre_direction, street_pre_type, unit_type, unit_value. A field it labels only as a whole counts as a miss here.
- libpostal produces these fine labels: building_name, city, country, postal_code, state. A field it labels only as a whole counts as a miss here.
- usaddress produces these fine labels: building_name, city, country, house_number_prefix, house_number_suffix, house_number_value, po_box_type, po_box_value, postal_code, recipient, route_box_type, route_box_value, route_type, route_value, state, street_name, street_post_direction, street_post_type, street_pre_direction, street_pre_type, unit_type, unit_value. A field it labels only as a whole counts as a miss here.

Per fine label F1 is in `results.json` (`fine_f1`).

## Parser Score

Parts used: golden/normal, golden/hard, golden/nightmare, doorplate-suite/natural, doorplate-suite/hand, senzing-us/osm, geocode-dev/dev. Bootstrap: 1000 resamples, seed 20261113.

| Parser | Parser Score (95% interval) | Field F1 score (95% interval) |
|---|---|---|
| doorplate | 89.4 (88.2 to 90.6) | 97.2 (96.9 to 97.5) |
| libpostal | 80.8 (79.5 to 82.2) | 93.4 (92.8 to 93.9) |
| usaddress | 84.7 (83.4 to 86.0) | 95.7 (95.3 to 96.1) |

## Sensitivity (Parser Score)

| Weights | doorplate | libpostal | usaddress |
|---|---|---|---|
| formula weights | 89.4 | 80.8 | 84.7 | ranking: doorplate > usaddress > libpostal |
| equal weights | 90.5 | 82.1 | 85.7 | ranking: doorplate > usaddress > libpostal |
| with the doubtful records | 88.9 | 80.6 | 84.3 | ranking: doorplate > usaddress > libpostal |
| without doorplate-suite | 86.8 | 77.9 | 81.7 | ranking: doorplate > usaddress > libpostal |
| without geocode-dev | 88.7 | 80.9 | 84.2 | ranking: doorplate > usaddress > libpostal |
| without golden | 96.9 | 89.4 | 91.6 | ranking: doorplate > usaddress > libpostal |
| without senzing-us | 88.1 | 78.2 | 83.9 | ranking: doorplate > usaddress > libpostal |
