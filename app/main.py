from fastapi import FastAPI, HTTPException, Query
import swisseph as swe
from math import ceil
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Setup Swiss Ephemeris path
swe.set_ephe_path('/usr/share/ephe')  # Change if needed

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def norm360(angle):
    return angle % 360

def solar_longitude(jd):
    return norm360(swe.calc_ut(jd, swe.SUN, swe.FLG_SWIEPH)[0][0])

def lunar_longitude(jd):
    return norm360(swe.calc_ut(jd, swe.MOON, swe.FLG_SWIEPH)[0][0])

def gregorian_to_jd(year, month, day, hour=0):
    return swe.julday(year, month, day, hour)

@app.get("/panchang/")
def get_panchang(
    year: int = Query(..., ge=1900),
    month: int = Query(..., ge=1, le=12),
    day: int = Query(..., ge=1, le=31),
    lat: float = Query(...),
    lon: float = Query(...),
    timezone: float = Query(5.5)
):
    try:
        jd = gregorian_to_jd(year, month, day) - timezone / 24.0

        sun_long = solar_longitude(jd)
        moon_long = lunar_longitude(jd)
        moon_sun_diff = (moon_long - sun_long) % 360

        tithi = int(ceil(moon_sun_diff / 12))
        nakshatra = int(ceil(moon_long * 27 / 360))
        yoga = int(ceil((sun_long + moon_long) % 360 * 27 / 360))

        result = {
            "date": f"{year}-{month:02}-{day:02}",
            "latitude": lat,
            "longitude": lon,
            "timezone": timezone,
            "tithi": tithi,
            "nakshatra": nakshatra,
            "yoga": yoga,
            "sun_longitude": sun_long,
            "moon_longitude": moon_long
        }

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
