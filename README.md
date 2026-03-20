# Timing Engineering Intern — Technical Assessment (Option 2)

## How to Run

You'll need Python 3.10+ and pip.
```bash
git clone https://github.com/amansoory/timing-data-assessment.git
cd timing-data-assessment
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

Run the dashboard:
```bash
streamlit run app.py
```

Or view it live: [https://timing-data-assessment.streamlit.app](https://timing-data-assessment.streamlit.app)

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


---

## Bonus — Interactive Dashboard

I built a Streamlit dashboard to visualize the data and make the recommendation engine interactive. It wasn't required for Option 2 but I wanted to show the system actually working in a way you can play with, not just terminal output.

**Features:**
- Full contact table with all 6 contacts displayed
- Search bar that filters by name, email, or role in real time
- Role filter to toggle which relationship types are shown
- Sort by priority, recency, or alphabetically
- Top 3 recommendations generated using the same priority logic from Part 2
- Data quality flags for contacts with missing dates
- Themed to match Timing's brand

The filters and sorting aren't cosmetic — they actually modify the data shown in the table and the recommendations update accordingly. You can verify the priority logic is working correctly by removing roles and watching the recommendations shift.

---



## Part 3 — System Design

See [SYSTEM_DESIGN.md](SYSTEM_DESIGN.md) for the full writeup.


## Design Decisions

- **Separated `parse_date()` into its own function** — I wanted it reusable across both `broken_service.py` and `data_processor.py`, and having it isolated makes it easy to test on its own.
- **Priority map instead of if/else chains** — a dictionary lookup is cleaner and if Timing ever adds new relationship types (like "cofounder" or "recruiter"), you just add one line instead of another elif.
- **Made the threshold configurable** — `get_contacts_to_reach_out()` takes a `threshold` parameter instead of hardcoding 30 days. Different users might want different windows.
- **Logging instead of print statements** — production code uses loggers. It's a small thing but it shows awareness of how real systems work.
- **Built a Streamlit dashboard** — the assessment didn't ask for a UI for Option 2, but I wanted to show that I can go beyond requirements and build something a user could actually interact with. The filters and sorting actually work against the data.

## Assumptions

- Dates follow YYYY-MM-DD format
- Each contact has a single role (not comma-separated like "mentor, investor")
- Missing dates are a data quality issue, not an implicit signal for urgency
- Future dates are data entry mistakes and should be skipped
- The CSV is small enough to fit in memory (no need for streaming or chunked reads)

## What I'd Improve With More Time

- Wire up a FastAPI backend so the recommendation engine runs as a real API
- Connect the Streamlit UI to the API instead of reading directly from the CSV
- Add LLM-powered message generation using Claude's API and click a contact and get a personalized follow-up message
- Build a CI/CD pipeline with GitHub Actions running pytest on every push
- Dockerize the whole thing so it runs consistently anywhere
- Add more CSV format validation (duplicate emails, encoding issues, extremely old dates)
- Expand the test suite with integration tests that run against the full pipeline end to end