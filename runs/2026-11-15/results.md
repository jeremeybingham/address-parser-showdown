## Record accuracy by part (coarse track, 95% Wilson interval)

| Set / part | Role | Records | No parser right | doorplate | libpostal | usaddress |
|---|---|---|---|---|---|---|
| doorplate-suite / hand | scored | 1,000 | 15 | 95.8 (94.4 to 96.9) | 84.0 (81.6 to 86.1) | 91.1 (89.2 to 92.7) |
| doorplate-suite / hard | drawn from the blind spots of two of the three parsers | 2,585 | 145 | 73.4 (71.6 to 75.1) | 69.0 (67.2 to 70.8) | 25.7 (24.1 to 27.4) |
| doorplate-suite / natural | scored | 16,001 | 53 | 98.6 (98.4 to 98.8) | 95.0 (94.6 to 95.3) | 96.5 (96.2 to 96.7) |
| geocode-dev / dev | scored | 60,522 | 830 | 94.4 (94.2 to 94.6) | 79.9 (79.6 to 80.2) | 88.4 (88.1 to 88.6) |
| golden / hard | scored | 556 | 157 | 68.3 (64.4 to 72.1) | 48.7 (44.6 to 52.9) | 66.5 (62.5 to 70.3) |
| golden / hard/ambiguous | one door, several readings (flagged in blind labeling) | 14 | 6 | 42.9 (21.4 to 67.4) | 42.9 (21.4 to 67.4) | 57.1 (32.6 to 78.6) |
| golden / hard/doubtful | doubtful label (the Parser Score is also shown with these records in) | 17 | 13 | 17.6 (6.2 to 41.0) | 5.9 (1.0 to 27.0) | 23.5 (9.6 to 47.3) |
| golden / hard/multi_address | several doors: fields checked, no single door (flagged in blind labeling) | 11 | 0 | 100.0 (74.1 to 100.0) | 90.9 (62.3 to 98.4) | 90.9 (62.3 to 98.4) |
| golden / hard/non_address | not an address (flagged in blind labeling) | 13 | 0 | 100.0 (77.2 to 100.0) | 15.4 (4.3 to 42.2) | 30.8 (12.7 to 57.6) |
| golden / nightmare | scored | 226 | 54 | 62.4 (55.9 to 68.4) | 46.9 (40.5 to 53.4) | 46.0 (39.6 to 52.5) |
| golden / nightmare/ambiguous | one door, several readings (flagged in blind labeling) | 7 | 1 | 42.9 (15.8 to 75.0) | 57.1 (25.0 to 84.2) | 42.9 (15.8 to 75.0) |
| golden / nightmare/doubtful | doubtful label (the Parser Score is also shown with these records in) | 8 | 3 | 37.5 (13.7 to 69.4) | 25.0 (7.1 to 59.1) | 25.0 (7.1 to 59.1) |
| golden / nightmare/intersection | a corner, no door (flagged in blind labeling) | 4 | 3 | 25.0 (4.6 to 69.9) | 0.0 (0.0 to 49.0) | 25.0 (4.6 to 69.9) |
| golden / nightmare/multi_address | several doors: fields checked, no single door (flagged in blind labeling) | 13 | 5 | 23.1 (8.2 to 50.3) | 53.8 (29.1 to 76.8) | 23.1 (8.2 to 50.3) |
| golden / nightmare/non_address | not an address (flagged in blind labeling) | 2 | 1 | 50.0 (9.5 to 90.5) | 0.0 (0.0 to 65.8) | 50.0 (9.5 to 90.5) |
| golden / normal | scored | 1,568 | 64 | 95.0 (93.8 to 95.9) | 91.8 (90.3 to 93.0) | 93.6 (92.2 to 94.7) |
| libpostal-us / us | home set of libpostal (its own test_us_parses) | 53 | 2 | 84.9 (72.9 to 92.1) | 94.3 (84.6 to 98.1) | 88.7 (77.4 to 94.7) |
| senzing-us / bug | cases reported as libpostal bugs | 6 | 0 | 100.0 (61.0 to 100.0) | 100.0 (61.0 to 100.0) | 83.3 (43.6 to 97.0) |
| senzing-us / osm | scored | 2,172 | 6 | 98.1 (97.4 to 98.6) | 98.8 (98.3 to 99.2) | 90.6 (89.3 to 91.7) |
| usaddress-tests / labeled | home set of usaddress (its own regression tests) | 146 | 0 | 81.5 (74.4 to 87.0) | 68.5 (60.6 to 75.5), 1 errors | 100.0 (97.4 to 100.0) |
| usaddress-tests / multi_word_state_addresses | home set of usaddress (its own regression tests) | 5 | 0 | 40.0 (11.8 to 76.9) | 80.0 (37.6 to 96.4) | 100.0 (56.6 to 100.0) |
| usaddress-tests / simple_address_patterns | home set of usaddress (its own regression tests) | 8 | 0 | 87.5 (52.9 to 97.8) | 87.5 (52.9 to 97.8) | 100.0 (67.6 to 100.0) |
| usaddress-tests / synthetic_clean_osm_data | home set of usaddress (its own regression tests) | 4,120 | 6 | 99.8 (99.6 to 99.9) | 99.8 (99.6 to 99.9) | 99.8 (99.6 to 99.9) |
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
| doorplate-suite / hand | street | 96.1 | 89.0 | 96.6 |
| doorplate-suite / hand | unit | 99.8 | 90.5 | 91.2 |
| doorplate-suite / hard | city | 89.2 | 97.3 | 73.4 |
| doorplate-suite / hard | house_number | 99.5 | 89.1 | 87.0 |
| doorplate-suite / hard | po_box | - | - | 0.0 |
| doorplate-suite / hard | postal_code | 100.0 | 99.8 | 100.0 |
| doorplate-suite / hard | state | 99.7 | 99.9 | 96.4 |
| doorplate-suite / hard | street | 80.7 | 72.7 | 50.6 |
| doorplate-suite / hard | unit | 77.2 | 82.0 | 34.3 |
| doorplate-suite / natural | city | 99.3 | 98.8 | 98.6 |
| doorplate-suite / natural | house_number | 100.0 | 99.8 | 99.9 |
| doorplate-suite / natural | po_box | 100.0 | 77.6 | 84.8 |
| doorplate-suite / natural | postal_code | 100.0 | 99.9 | 100.0 |
| doorplate-suite / natural | route | 91.9 | 0.0 | 66.4 |
| doorplate-suite / natural | state | 100.0 | 99.4 | 99.9 |
| doorplate-suite / natural | street | 98.9 | 96.3 | 98.0 |
| doorplate-suite / natural | unit | 97.1 | 91.1 | 92.1 |
| geocode-dev / dev | city | 96.0 | 86.1 | 92.8 |
| geocode-dev / dev | house_number | 100.0 | 99.6 | 99.5 |
| geocode-dev / dev | po_box | - | 0.0 | 0.0 |
| geocode-dev / dev | postal_code | 100.0 | 99.7 | 100.0 |
| geocode-dev / dev | route | 0.0 | - | 0.0 |
| geocode-dev / dev | state | 99.8 | 99.2 | 97.5 |
| geocode-dev / dev | street | 94.6 | 80.6 | 92.2 |
| geocode-dev / dev | unit | 0.0 | 0.0 | 0.0 |
| golden / hard | city | 99.6 | 96.5 | 98.1 |
| golden / hard | house_number | 97.2 | 90.0 | 96.3 |
| golden / hard | po_box | 92.3 | 45.7 | 81.1 |
| golden / hard | postal_code | 99.3 | 98.8 | 99.3 |
| golden / hard | route | 43.3 | 0.0 | 44.4 |
| golden / hard | state | 98.6 | 99.0 | 98.2 |
| golden / hard | street | 76.9 | 63.4 | 77.3 |
| golden / hard | unit | 88.8 | 61.3 | 87.9 |
| golden / hard/ambiguous | city | 85.7 | 88.9 | 92.9 |
| golden / hard/ambiguous | house_number | 90.9 | 81.8 | 87.0 |
| golden / hard/ambiguous | po_box | 66.7 | 50.0 | 80.0 |
| golden / hard/ambiguous | postal_code | 100.0 | 100.0 | 100.0 |
| golden / hard/ambiguous | route | 0.0 | 0.0 | 0.0 |
| golden / hard/ambiguous | state | 100.0 | 100.0 | 100.0 |
| golden / hard/ambiguous | street | 69.6 | 48.0 | 80.0 |
| golden / hard/ambiguous | unit | 57.1 | 50.0 | 50.0 |
| golden / hard/doubtful | city | 70.6 | 66.7 | 74.3 |
| golden / hard/doubtful | house_number | 100.0 | 94.1 | 100.0 |
| golden / hard/doubtful | po_box | 0.0 | 100.0 | 0.0 |
| golden / hard/doubtful | postal_code | 100.0 | 100.0 | 100.0 |
| golden / hard/doubtful | route | 0.0 | 0.0 | 0.0 |
| golden / hard/doubtful | state | 100.0 | 100.0 | 100.0 |
| golden / hard/doubtful | street | 66.7 | 54.5 | 66.7 |
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
| golden / nightmare | house_number | 96.4 | 84.1 | 88.5 |
| golden / nightmare | po_box | 80.0 | 17.1 | 30.3 |
| golden / nightmare | postal_code | 96.7 | 94.4 | 99.1 |
| golden / nightmare | route | 44.8 | 0.0 | 14.3 |
| golden / nightmare | state | 99.3 | 93.7 | 99.3 |
| golden / nightmare | street | 80.2 | 63.9 | 67.8 |
| golden / nightmare | unit | 65.6 | 64.5 | 41.2 |
| golden / nightmare/ambiguous | city | 100.0 | 100.0 | 100.0 |
| golden / nightmare/ambiguous | house_number | 100.0 | 88.9 | 100.0 |
| golden / nightmare/ambiguous | postal_code | 100.0 | 100.0 | 100.0 |
| golden / nightmare/ambiguous | route | 0.0 | 0.0 | 0.0 |
| golden / nightmare/ambiguous | state | 100.0 | 100.0 | 100.0 |
| golden / nightmare/ambiguous | street | 54.5 | 61.5 | 54.5 |
| golden / nightmare/ambiguous | unit | 25.0 | 66.7 | 28.6 |
| golden / nightmare/doubtful | city | 93.3 | 93.3 | 100.0 |
| golden / nightmare/doubtful | house_number | 92.3 | 76.9 | 72.7 |
| golden / nightmare/doubtful | po_box | 0.0 | 100.0 | 100.0 |
| golden / nightmare/doubtful | postal_code | 93.3 | 93.3 | 93.3 |
| golden / nightmare/doubtful | route | 0.0 | 0.0 | 0.0 |
| golden / nightmare/doubtful | state | 100.0 | 93.3 | 100.0 |
| golden / nightmare/doubtful | street | 80.0 | 20.0 | 22.2 |
| golden / nightmare/doubtful | unit | 57.1 | 66.7 | 0.0 |
| golden / nightmare/intersection | city | 100.0 | 100.0 | 100.0 |
| golden / nightmare/intersection | house_number | 100.0 | 100.0 | 80.0 |
| golden / nightmare/intersection | postal_code | 100.0 | 100.0 | 100.0 |
| golden / nightmare/intersection | route | 0.0 | 0.0 | 0.0 |
| golden / nightmare/intersection | state | 100.0 | 100.0 | 100.0 |
| golden / nightmare/intersection | street | 66.7 | 0.0 | 54.5 |
| golden / nightmare/multi_address | city | 100.0 | 96.0 | 96.3 |
| golden / nightmare/multi_address | house_number | 26.1 | 61.5 | 34.8 |
| golden / nightmare/multi_address | postal_code | 100.0 | 100.0 | 100.0 |
| golden / nightmare/multi_address | state | 100.0 | 100.0 | 100.0 |
| golden / nightmare/multi_address | street | 76.9 | 53.8 | 57.1 |
| golden / nightmare/multi_address | unit | 66.7 | 100.0 | 28.6 |
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
| golden / normal | street | 98.4 | 94.9 | 97.8 |
| golden / normal | unit | 84.8 | 80.0 | 81.9 |
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
| senzing-us / osm | street | 99.2 | 98.9 | 97.5 |
| senzing-us / osm | unit | 94.8 | 97.6 | 81.2 |
| usaddress-tests / labeled | city | 93.4 | 91.4 | 100.0 |
| usaddress-tests / labeled | house_number | 98.3 | 98.3 | 100.0 |
| usaddress-tests / labeled | po_box | 69.6 | 63.4 | 100.0 |
| usaddress-tests / labeled | postal_code | 99.5 | 99.5 | 100.0 |
| usaddress-tests / labeled | route | 100.0 | 0.0 | 100.0 |
| usaddress-tests / labeled | state | 99.5 | 97.6 | 100.0 |
| usaddress-tests / labeled | street | 84.3 | 79.2 | 100.0 |
| usaddress-tests / labeled | unit | 73.5 | 88.9 | 100.0 |
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
| usaddress-tests / synthetic_clean_osm_data | unit | 40.0 | 0.0 | 0.0 |
| usaddress-tests / synthetic_osm_data | city | 100.0 | 100.0 | 100.0 |
| usaddress-tests / synthetic_osm_data | house_number | 100.0 | 100.0 | 100.0 |
| usaddress-tests / synthetic_osm_data | postal_code | 100.0 | 100.0 | 100.0 |
| usaddress-tests / synthetic_osm_data | state | 100.0 | 100.0 | 100.0 |
| usaddress-tests / synthetic_osm_data | street | 99.9 | 99.9 | 100.0 |
| usaddress-tests / synthetic_osm_data | unit | 0.0 | - | - |
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
| doorplate-suite / hand | 1,000 of 1,000 | 94.0 | 0.0 | 89.1 |
| doorplate-suite / hard | 2,521 of 2,585 | 70.2 | 0.0 | 23.0 |
| doorplate-suite / natural | 15,982 of 16,001 | 98.1 | 0.0 | 95.9 |
| geocode-dev / dev | 60,522 of 60,522 | 84.3 | 0.0 | 80.3 |
| golden / hard | 556 of 556 | 63.3 | 0.4 | 57.6 |
| golden / hard/ambiguous | 14 of 14 | 42.9 | 7.1 | 42.9 |
| golden / hard/doubtful | 17 of 17 | 23.5 | 0.0 | 23.5 |
| golden / hard/multi_address | 11 of 11 | 100.0 | 0.0 | 90.9 |
| golden / hard/non_address | 13 of 13 | 100.0 | 15.4 | 30.8 |
| golden / nightmare | 226 of 226 | 57.5 | 0.0 | 41.6 |
| golden / nightmare/ambiguous | 7 of 7 | 42.9 | 0.0 | 42.9 |
| golden / nightmare/doubtful | 8 of 8 | 25.0 | 0.0 | 25.0 |
| golden / nightmare/intersection | 4 of 4 | 0.0 | 0.0 | 0.0 |
| golden / nightmare/multi_address | 13 of 13 | 23.1 | 0.0 | 23.1 |
| golden / nightmare/non_address | 2 of 2 | 50.0 | 0.0 | 50.0 |
| golden / normal | 1,568 of 1,568 | 94.4 | 0.0 | 93.0 |
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
| doorplate | 86.0 (84.6 to 87.3) | 96.5 (96.2 to 96.8) |
| libpostal | 76.0 (74.6 to 77.3) | 92.3 (91.8 to 92.8) |
| usaddress | 80.2 (78.8 to 81.5) | 94.7 (94.3 to 95.0) |

## Sensitivity (Parser Score)

| Weights | doorplate | libpostal | usaddress |
|---|---|---|---|
| formula weights | 86.0 | 76.0 | 80.2 | ranking: doorplate > usaddress > libpostal |
| equal weights | 87.5 | 77.9 | 81.8 | ranking: doorplate > usaddress > libpostal |
| with the doubtful records | 85.6 | 75.6 | 79.8 | ranking: doorplate > usaddress > libpostal |
| without doorplate-suite | 82.2 | 71.4 | 75.6 | ranking: doorplate > usaddress > libpostal |
| without geocode-dev | 84.8 | 75.4 | 79.0 | ranking: doorplate > usaddress > libpostal |
| without golden | 96.7 | 89.4 | 91.6 | ranking: doorplate > usaddress > libpostal |
| without senzing-us | 84.2 | 72.7 | 78.7 | ranking: doorplate > usaddress > libpostal |
