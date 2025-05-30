# Coptic Synaxarium API

This project provides an open-source API for accessing the Coptic Synaxarium—the daily record of saints, martyrs, feasts, and events in the Coptic Orthodox Church. You can search by either Gregorian (regular) date or Coptic date, and receive a structured JSON response with the relevant story, feasts, and both date formats.

## Features

- Query by Gregorian date (`/synaxarium?date_gregorian=YYYY-MM-DD`)
- Query by Coptic date (`/synaxarium?date_coptic=DAY+MONTH`, e.g., `20+Bashons`)
- FastAPI backend for modern, asynchronous performance
- CORS enabled for easy integration with any frontend or tool
- Simple HTML homepage for trying out the API in your browser
- Loads Synaxarium data from a JSON file at startup
- Accurate date conversion using Julian Day Number (JDN) calculations

## How it Works

- **Data Loading:** The API loads all Synaxarium data from `synaxarium.json` when it starts.
- **Gregorian → Coptic:** The API converts your Gregorian date to a Julian Day Number (JDN), then calculates how many days have passed since the Coptic calendar began (August 29, 284 AD, Julian). It then determines the Coptic year, month, and day, handling leap years according to the Coptic system (every 4th year, no exceptions).
- **Coptic → Gregorian:** The API searches for the Gregorian date that matches the given Coptic date by checking every day in the current, previous, and next year. This approach is simple and reliable for most use cases.
- **Homepage:** The included homepage allows you to try the API directly in your browser.

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/jeninh/synaxarium-api.git
   cd synaxarium-api
   ```
2. **Install dependencies**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Add the Synaxarium JSON file**
   Place your Synaxarium data file as `synaxarium.json` in the project root.
4. **Run the API**
   ```bash
   uvicorn main:app --reload
   ```
5. **Visit the homepage**
   Open [http://localhost:8000](http://localhost:8000) in your browser.

## API Endpoints

- `/synaxarium?date_gregorian=YYYY-MM-DD` — Query by Gregorian date
- `/synaxarium?date_coptic=DAY+MONTH` — Query by Coptic date (e.g., `20+Bashons`)

### Example Response

```json
{
  "coptic_date": { "day": 22, "month": 8, "monthString": "Bashans", "year": 1741 },
  "gregorian_date": "2025-05-30",
  "feasts": ["The Departure of St. Erastus, the Apostle."],
  "description": "<p>On this day, St. Erastus..." 
}
```
If no entry is found:
```json
{ "coptic_date": {...}, "gregorian_date": "...", "message": "No Synaxarium entry found for this date." }
```

## Technical Details

- **Language:** Python 3.12
- **Framework:** FastAPI
- **Server:** Uvicorn
- **Frontend:** Plain HTML + JavaScript
- **Date Conversion:** Uses Julian Day Number (JDN) calculations and Coptic calendar math (see `main.py` for details)
- **CORS:** Enabled for all origins
- **Dependencies:** fastapi, uvicorn, python-multipart, jinja2
- **Source:** [github.com/jeninh/synaxarium-api](https://github.com/jeninh/synaxarium-api)

## Credits

- [randogoth/coptic-synaxarium](https://github.com/randogoth/coptic-synaxarium) — Original JSON data source, the readings themselves
- [abanobmikaeel/coptic.io](https://github.com/abanobmikaeel/coptic.io) — Calendar conversion logic (adapted to Python)

## License

MIT
