from flask import Flask, request, jsonify
import swisseph as swe
import datetime
import traceback
import os

app = Flask(__name__)
swe.set_ephe_path('.')  # eph file path

rashi_names = ["Mesha", "Vrushabh", "Mithun", "Kark", "Sinh", "Kanya",
               "Tula", "Vrushchik", "Dhanu", "Makar", "Kumbh", "Meen"]

nakshatra_names = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
    "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
    "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati",
    "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
    "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
    "Uttara Bhadrapada", "Revati"
]

yoga_names = [
    "Vishkumbha", "Preeti", "Ayushman", "Saubhagya", "Shobhana",
    "Atiganda", "Sukarman", "Dhriti", "Shoola", "Ganda",
    "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra",
    "Siddhi", "Vyatipata", "Variyana", "Parigha", "Shiva",
    "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma",
    "Indra", "Vaidhriti"
]

@app.route('/calculate', methods=['POST'])
def calculate_panchang():
    try:
        data = request.get_json(force=True)

        date_str = data['date']
        time_str = data['time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        timezone = float(data['timezone'])

        dt = datetime.datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        dt_utc = dt - datetime.timedelta(hours=timezone)
        jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute / 60.0)

        # Sun & Moon
        sun_pos, _ = swe.calc_ut(jd, swe.SUN)
        moon_pos, _ = swe.calc_ut(jd, swe.MOON)

        # Tithi
        tithi_deg = (moon_pos - sun_pos) % 360
        tithi = int(tithi_deg / 12) + 1

        # Nakshatra
        nakshatra_index = int((moon_pos % 360) / (360 / 27))
        nakshatra = nakshatra_names[nakshatra_index]
        nakshatra_swami = get_nakshatra_lord(nakshatra_index + 1)

        # Yoga
        yoga_index = int(((sun_pos + moon_pos) % 360) / (360 / 27))
        yoga = yoga_names[yoga_index]

        # Paksha
        paksha = "Shukla" if tithi <= 15 else "Krishna"
        vikram_samvat = dt.year + 57
        mahino = get_solar_month(sun_pos)

        # Rashi
        moon_rashi = int(moon_pos / 30)
        lagna_rashi = get_lagna_rashi(jd, latitude, longitude)

        response = {
            "tithi": str(tithi),
            "nakshatra": nakshatra,
            "nakshatra_swami": nakshatra_swami,
            "yoga": yoga,
            "paksha": paksha,
            "vikram_samvat": str(vikram_samvat),
            "mahino": mahino,
            "lagna_rashi": rashi_names[lagna_rashi],
            "chandra_rashi": rashi_names[moon_rashi]
        }

        return jsonify(response)

    except Exception as e:
        print("❌ Error:\n", traceback.format_exc())
        return jsonify({"error": str(e)}), 500


def get_nakshatra_lord(nakshatra_num):
    lords = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
    return lords[(nakshatra_num - 1) % 9]

def get_solar_month(sun_longitude):
    months = rashi_names
    index = int(sun_longitude / 30)
    return f"{months[index]} (Solar Month)"

def get_lagna_rashi(jd, lat, lon):
    _, ascmc = swe.houses_ex(jd, lat, lon, b'A')
    asc = ascmc[0]
    return int(asc / 30)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
