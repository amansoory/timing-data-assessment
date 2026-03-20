# Timing Engineering Intern — Technical Assessment (Option 2)

## How to Run

You'll need Python 3.10+ and pip.
```bash
git clone https://github.com/amansoory/timing-assessment.git
cd timing-assessment
python -m venv venv

# Windows
.\venv\Scripts\Activate

# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

Run the tests:
```bash
pytest test_service.py -v
```

Run the data processor:
```bash
python data_processor.py
```

---

## Part 1 — Debugging broken_service.py

The original function had a few issues that would crash it before it could do anything useful. Here's what I found:

**1. String subtraction** — `datetime.now() - contact["last_contacted"]` doesn't work because `last_contacted` comes in as a string like `"2024-01-10"`, not an actual datetime. I added a `parse_date()` helper that converts it using `strptime()`.

**2. Comparing timedelta to an int** — Even after fixing the parsing, `days > 30` still breaks because subtracting two datetimes gives you a `timedelta` object, not a number. You need `days.days` to pull out the actual number.

**3. Missing dates** — Christopher Johnson has no `last_contacted` value in the CSV. The original code would just crash on that. My `parse_date()` function handles empty strings, None values, and malformed dates by returning None instead of blowing up.

**4. Missing keys** — If a contact dictionary doesn't even have a `last_contacted` key, `contact["last_contacted"]` throws a KeyError. Switched to `.get()` with a default.

**5. Future dates** — If someone accidentally enters a date in the future, the math gives you negative days. I added a check to skip those and log a warning since it's almost certainly a data entry error.

I wrote 14 unit tests to cover all of this — the standard cases plus edge cases like exact boundary (exactly 30 days), empty contact lists, whitespace-only dates, and custom thresholds. The assignment asked for 1 test but I added 14 tests based on what errors I could think of getting. I used pytest as my testing framework.

---

## Part 2 — Data Processing Script

`data_processor.py` reads the CSV, scores each contact by their role priority and how long it's been since you talked to them, and returns the top 2.

Priority order:
1. Investor
2. Mentor
3. Advisor
4. Friend
5. Everything else

If two contacts share the same role priority, the one you haven't talked to in longer wins. I noticed Christopher Johnson had no last contact date, so I separated contacts with missing dates into their own "data quality flags" section instead of ranking them. Whether a missing date means "urgent, reach out now" or "bad data, fix it first" really depends on the use case, so I left it flexible rather than assuming one way or the other.

Output:

Trisha Rodriguez — Investor — 836 days
Sarah Chen — Mentor — 440 days

DATA QUALITY FLAGS:

Christopher Johnson (Mentor) — No valid last contact date




## Part 3 — System Design

See [SYSTEM_DESIGN.md](SYSTEM_DESIGN.md) for the full writeup.
