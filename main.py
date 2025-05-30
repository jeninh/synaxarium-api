import json
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime
from typing import Optional
import os
import sys
#(yes this is a lot of libraries i know, also github autocomplete is fun)
COPTIC_MONTHS = [
    "Tout", "Baba", "Hator", "Kiahk", "Toba", "Amshir", "Baramhat",
    "Baramouda", "Bashans", "Paona", "Epep", "Mesra", "Nasie"
]

# gregorian to jdn because that's what copilot told me will work
def gregorian_to_jdn(year, month, day):
    # this converts gregorian to julian day number (jdn) which makes it much much easier to convert to coptic, also because gregorian directly to coptic was physically not funtioning for me
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    jdn = day + ((153 * m + 2) // 5) + 365 * y
    jdn += y // 4 - y // 100 + y // 400 - 32045
    return jdn

def jdn_to_coptic(jdn):
    #coptic calendar begun on august 29, 284 AD (Julian)
    coptic_years_start = 1825029  # jdn number for 284 AD August 29
    days_since_start = jdn - coptic_years_start # how many days sine coptic year began to get the year number
    years_passed = days_since_start // 365
    days_left = days_since_start % 365
    leap_days = years_passed // 4
    if days_left < leap_days:
        years_passed -= 1
        days_left += 365
        leap_days = years_passed // 4
    day_of_year = days_left - leap_days + 1
    month_num = (day_of_year - 1) // 30 + 1
    day_num = (day_of_year - 1) % 30 + 1
    return years_passed + 1, month_num, day_num

def gregorian_to_coptic(gregorian_date: datetime):
    year = gregorian_date.year
    month = gregorian_date.month
    day = gregorian_date.day
    jdn = gregorian_to_jdn(year, month, day)
#it was one day ahead so im just gonna move it back, moving on
    coptic_year, coptic_month, coptic_day = jdn_to_coptic(jdn - 1)
    month_name = COPTIC_MONTHS[coptic_month - 1] if 1 <= coptic_month <= 13 else "Nasie"
    return {
        "day": coptic_day,
        "month": coptic_month,
        "monthString": month_name,
        "year": coptic_year
    }

# load the data from synaxarium.json with os hehehehe
SYNAXARIUM_PATH = os.environ.get("SYNAXARIUM_PATH", "synaxarium.json")
if os.path.exists(SYNAXARIUM_PATH):
    with open(SYNAXARIUM_PATH, encoding="utf-8") as f:
        synaxarium_data = json.load(f)
else:
    synaxarium_data = {}

app = FastAPI(title="Coptic Synaxarium API")

# allows pai to be accessed from any website not just the one it's hosted on, idk github copilot said it was a good idea
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory=".")

@app.get("/", response_class=HTMLResponse)
def homepage(request: Request):
    with open("index.html", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.get("/synaxarium")
def get_synaxarium(date_gregorian: Optional[str] = None, date_coptic: Optional[str] = None):
    if date_gregorian:
        try:
            gdate = datetime.strptime(date_gregorian, "%Y-%m-%d")
            coptic = gregorian_to_coptic(gdate)
            key = f"{coptic['day']} {coptic['monthString']}"
        except Exception:
            return JSONResponse({"message": "Invalid Gregorian date format. Use YYYY-MM-DD."}, status_code=400)
        entry = synaxarium_data.get(key)
        response = {
            "coptic_date": {
                "day": coptic["day"],
                "month": coptic["month"],
                "monthString": coptic["monthString"],
                "year": coptic["year"]
            },
            "gregorian_date": date_gregorian,
        }
        if entry:
            response.update(entry)
        else:
            response["message"] = "No Synaxarium entry found for this date."
        return response
    elif date_coptic:
        try:
            # Accepts format like '2+Bashons' (with plus sign)
            parts = date_coptic.strip().replace('+', ' ').split()
            if len(parts) != 2:
                raise ValueError
            day = int(parts[0])
            month = parts[1].capitalize()
            key = f"{day} {month}"
        except Exception:
            return JSONResponse({"message": "Invalid Coptic date format. Use DAY+MONTH, e.g., 20+Bashons."}, status_code=400)
        entry = synaxarium_data.get(key)
        # Try to find the Gregorian date for this Coptic date in the current Coptic year
        today = datetime.today()
        # Find the Coptic year for today
        coptic_today = gregorian_to_coptic(today)
        coptic_year = coptic_today["year"]
        gregorian_date = None # the following stuff is to find the gregorian date from the coptic date
        # Check the current Coptic year and the previous and next years
        for y in [today.year, today.year + 1, today.year - 1]:
            for m in range(1, 13):
                for d in range(1, 32):
                    try:
                        dt = datetime(y, m, d)
                        c = gregorian_to_coptic(dt)
                        if c["day"] == day and c["monthString"].lower() == month.lower():
                            gregorian_date = dt.strftime("%Y-%m-%d")
                            raise StopIteration
                    except (ValueError, StopIteration):
                        if isinstance(sys.exc_info()[1], StopIteration):
                            break
                        continue
                if gregorian_date:
                    break
            if gregorian_date:
                break
        response = {
            "coptic_date": {
                "day": day,
                "month": COPTIC_MONTHS.index(month) + 1 if month in COPTIC_MONTHS else None,
                "monthString": month,
                "year": coptic_year
            },
            "gregorian_date": gregorian_date,
        }
        if entry:
            response.update(entry)
        else:
            response["message"] = "No Synaxarium entry found for this date."
        return response
    else:
        return JSONResponse({"message": "Please provide either date_gregorian or date_coptic."}, status_code=400)
