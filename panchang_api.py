from flask import Flask, request, jsonify
import swisseph as swe
import datetime
import traceback
import os

app = Flask(__name__)
swe.set_ephe_path('.')  # Set correct path for eph files

@app.route('/calculate', methods=['POST'])
def calculate_panchang():
    try:
        data = request.get_json(force=True)
        print("🔥 Request received:", data)

        # Extract input
        date_str = data['date']
        time_str = data['time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        timezone = float(data['timezone'])

        # Parse datetime
        dt = datetime.datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        dt = dt - datetime.timedelta(hours=timezone)
        jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute / 60.0)

        # Get longitudes (✅ Fixed unpacking)
        sun_long = swe.calc_ut(jd, swe.SUN)[0][0]
        moon_calc = swe.calc_ut(jd, swe.MOON)
        moon_long = moon_calc[0] if isinstance(moon_calc[0], float) else moon_calc[0][0]

        # Panchang Calculations
        tithi_deg = (moon_long - sun_long) % 360
        tithi = int(tithi_deg / 12) + 1

        nakshatra = int((moon_long % 360) / (360 / 27)) + 1
        nakshatra_swami = get_nakshatra_lord(nakshatra)

        yoga = int(((sun_long + moon_long) % 360) / (360 / 27)) + 1

        paksha = "Shukla" if tithi <= 15 else "Krishna"
        vikram_samvat = dt.year + 57
        mahino = get_solar_month(sun_long)

        lagna_degree = get_lagna_degree(jd, latitude, longitude)
        asc = int(lagna_degree / 30)
        moon_rashi = int(moon_long / 30)

        rashi_names = ["Mesha", "Vrushabh", "Mithun", "Kark", "Sinh", "Kanya",
                      "Tula", "Vrushchik", "Dhanu", "Makar", "Kumbh", "Meen
        response = {
            "tithi": str(tithi),
            "nakshatra": get_nakshatra_name(nakshatra),
            "nakshatra_swami": nakshatra_swami,
            "yoga": get_yoga_name(yoga),
            "paksha": paksha,
            "vikram_samvat": str(vikram_samvat),
            "mahino": mahino,
            "lagna_rashi": rashi_names[asc],
            "chandra_rashi": rashi_names[moon_rashi]
        }

        return jsonify(response)

    except Exception as e:
        print("❌ Exception occurred:\n", traceback.format_exc())
        return jsonify({"error": str(e)}), 500

# Utility functions
def get_nakshatra_name(index):
    names = [
        "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashirsha", "Ardra",
        "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
        "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula",
        "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
        "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
    ]
    return names[(index - 1) % 27]

def get_yoga_name(index):
    names = [
        "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda", "Sukarman",
        "Dhriti", "Shoola", "Ganda", "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra",
        "Siddhi", "Vyatipata", "Variyan", "Parigha", "Shiva", "Siddha", "Sadhya",
        "Shubha", "Shukla", "Brahma", "Indra", "Vaidhriti"
    ]
    return names[(index - 1) % 27]

def get_nakshatra_lord(nakshatra):
    lords = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
    return lords[(nakshatra - 1) % 9]

def get_solar_month(sun_longitude):
    months = ["Mesha", "Vrushabh", "Mithun", "Kark", "Sinh", "Kanya",
              "Tula", "Vrushchik", "Dhanu", "Makar", "Kumbh", "Meen"]
    month_index = int(sun_longitude / 30)
    return f"{months[month_index]} (Solar Month)"

def get_lagna_rashi(jd, lat, lon):
    # houses_ex returns (houses, ascmc) — ascmc[0] is ASC (Lagna degree)
    result = swe.houses_ex(jd, lat, lon, b'A')
    asc = result[1][0]  # Safe access to ASC value
    return int(asc / 30)  # 360° divided into 12 signs


# Main entry
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
