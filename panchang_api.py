from flask import Flask, request, jsonify
import swisseph as swe
import datetime

app = Flask(__name__)

swe.set_ephe_path("/usr/share/ephe")  # adjust path if needed

def get_tithi(jd, moon_lon, sun_lon):
    tithi = int(((moon_lon - sun_lon) % 360) / 12) + 1
    return tithi

def get_nakshatra(moon_lon):
    nakshatra = int(moon_lon / (360 / 27))
    return nakshatra

def get_nakshatra_swami(nakshatra):
    swamis = [
        "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
    ]
    return swamis[nakshatra % 9]

def get_yoga(sun_lon, moon_lon):
    total = (sun_lon + moon_lon) % 360
    yoga = int(total / (360 / 27))
    return yoga

def get_lagna_rashi(jd, lat, lon):
    try:
        houses, ascmc = swe.houses_ex(jd, lat, lon, b'A')
        asc = ascmc[0]
        return int(asc / 30)
    except Exception as e:
        print("Error in get_lagna_rashi:", e)
        return 0  # default to Mesha (0)

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.get_json()

        date = data.get("date")
        time = data.get("time")
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        timezone = float(data.get("timezone"))

        # Combine date and time into datetime object
        dt = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        dt = dt - datetime.timedelta(hours=timezone)
        jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute / 60.0)

        sun = swe.calc_ut(jd, swe.SUN)[0]
        moon = swe.calc_ut(jd, swe.MOON)[0]

        tithi = get_tithi(jd, moon, sun)
        nakshatra_num = get_nakshatra(moon)
        nakshatra_name = f"Nakshatra {nakshatra_num}"
        yoga_num = get_yoga(sun, moon)

        chandra_rashi = int(moon / 30)
        lagna_rashi = get_lagna_rashi(jd, latitude, longitude)

        paksha = "Shukla" if tithi <= 15 else "Krishna"
        vikram_samvat = dt.year + 57
        mahino = "Dhanu (Solar Month)"  # mock for now
        nakshatra_swami = get_nakshatra_swami(nakshatra_num)

        return jsonify({
            "tithi": tithi,
            "nakshatra": nakshatra_name,
            "nakshatra_swami": nakshatra_swami,
            "yoga": f"Yoga {yoga_num}",
            "paksha": paksha,
            "vikram_samvat": vikram_samvat,
            "mahino": mahino,
            "lagna_rashi": f"Rashi {lagna_rashi}",
            "chandra_rashi": f"Rashi {chandra_rashi}"
        })

    except Exception as e:
        print("Exception:", str(e))
        return jsonify({"error": str(e)}), 500

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
