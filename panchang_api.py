from flask import Flask, request, jsonify
import swisseph as swe
import datetime
import os

app = Flask(__name__)
swe.set_ephe_path('.')

# --------------------------------
# Utility Functions
# --------------------------------

RASHI_NAMES = ["Mesha", "Vrushabh", "Mithun", "Kark", "Sinh", "Kanya",
               "Tula", "Vrushchik", "Dhanu", "Makar", "Kumbh", "Meen"]

NAKSHATRA_NAMES = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

NAKSHATRA_LORDS = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]

YOGA_NAMES = [
    "Vishkumbha", "Preeti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda", "Sukarma", "Dhriti", "Shoola",
    "Ganda", "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra", "Siddhi", "Vyatipata", "Variyana",
    "Parigha", "Shiva", "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma", "Indra", "Vaidhriti"
]

LUNAR_MONTHS = [
    "Chaitra", "Vaishakha", "Jyeshtha", "Ashadha", "Shravana", "Bhadrapada",
    "Ashwin", "Kartika", "Margashirsha", "Pausha", "Magha", "Phalguna"
]

def get_lagna_degree(jd, lat, lon):
    _, ascmc = swe.houses_ex(jd, lat, lon, b'A')
    return ascmc[0]

def get_nakshatra_and_lord(moon_long):
    nakshatra_index = int((moon_long % 360) / (360 / 27))
    lord = NAKSHATRA_LORDS[nakshatra_index % 9]
    return NAKSHATRA_NAMES[nakshatra_index], lord

def get_yoga_name(sun_long, moon_long):
    yoga_index = int(((sun_long + moon_long) % 360) / (360 / 27))
    return YOGA_NAMES[yoga_index]

def get_tithi_type(moon_long, sun_long, jd):
    tithi_angle = (moon_long - sun_long) % 360
    current_tithi = int(tithi_angle / 12)
    next_jd = jd + 1
    next_moon = swe.calc_ut(next_jd, swe.MOON)[0]
    next_sun = swe.calc_ut(next_jd, swe.SUN)[0]
    next_tithi = int(((next_moon - next_sun) % 360) / 12)
    
    if next_tithi == current_tithi:
        return "Vriddhi"
    elif next_tithi < current_tithi:
        return "Kshay"
    else:
        return "Normal"

def get_lunar_month(sun_long, moon_long):
    sun_rashi = int(sun_long / 30)
    moon_rashi = int(moon_long / 30)
    diff = (moon_rashi - sun_rashi + 12) % 12
    if diff == 0:
        return f"{LUNAR_MONTHS[sun_rashi]} (Adhik Maas)"
    return LUNAR_MONTHS[(sun_rashi + 1) % 12]

# --------------------------------
# API Endpoint
# --------------------------------

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.get_json()
        date_str = data['date']
        time_str = data['time']
        lat = float(data['latitude'])
        lon = float(data['longitude'])
        tz = float(data['timezone'])

        dt = datetime.datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        dt_utc = dt - datetime.timedelta(hours=tz)
        jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute / 60)

        sun_long = swe.calc_ut(jd, swe.SUN)[0]
        moon_long = swe.calc_ut(jd, swe.MOON)[0]

        # Rashi
        chandra_rashi = RASHI_NAMES[int(moon_long / 30)]
        lagna_degree = get_lagna_degree(jd, lat, lon)
        lagna_rashi = RASHI_NAMES[int(lagna_degree / 30)]

        # Tithi
        tithi_angle = (moon_long - sun_long) % 360
        tithi_number = int(tithi_angle / 12) + 1
        paksha = "Shukla" if tithi_number <= 15 else "Krishna"
        tithi_type = get_tithi_type(moon_long, sun_long, jd)
        tithi_full = f"{tithi_number} ({tithi_type})"

        # Nakshatra
        nakshatra_name, nakshatra_lord = get_nakshatra_and_lord(moon_long)

        # Yoga
        yoga_name = get_yoga_name(sun_long, moon_long)

        # Month
        hindu_month = get_lunar_month(sun_long, moon_long)

        # Vikram Samvat
        samvat = dt.year + 57

        return jsonify({
            "chandra_rashi": chandra_rashi,
            "lagna_rashi": lagna_rashi,
            "tithi": tithi_full,
            "paksha": paksha,
            "nakshatra": nakshatra_name,
            "nakshatra_swami": nakshatra_lord,
            "yoga": yoga_name,
            "mahino": hindu_month,
            "vikram_samvat": str(samvat)
        })

    except Exception as e:
        import traceback
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

# --------------------------------
# Run Server
# --------------------------------

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
