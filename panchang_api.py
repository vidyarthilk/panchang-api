from flask import Flask, request, jsonify
import swisseph as swe
import datetime
import traceback
import os

app = Flask(__name__)
swe.set_ephe_path("/usr/share/ephe")  # or "." if eph files are in the same folder

def get_tithi(moon_lon, sun_lon):
    tithi = int(((moon_lon - sun_lon) % 360) / 12) + 1
    return tithi

def get_nakshatra(moon_lon):
    return int((moon_lon % 360) / (360 / 27)) + 1

def get_yoga(moon_lon, sun_lon):
    total = (moon_lon + sun_lon) % 360
    return int(total / (360 / 27)) + 1

def get_nakshatra_swami(nakshatra):
    lords = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
    return lords[(nakshatra - 1) % 9]

def get_lagna_rashi(jd, lat, lon):
    try:
        houses, ascmc = swe.houses_ex(jd, lat, lon, b'A')
        asc = ascmc[0]
        return int(asc / 30)
    except Exception as e:
        print("Error in get_lagna_rashi:", e)
        return 0

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.get_json()

        date = data.get("date")
        time = data.get("time")
        latitude = float(data.get("latitude"))
        longitude = float(data.get("longitude"))
        timezone = float(data.get("timezone"))

        # Convert to UTC
        dt = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        dt -= datetime.timedelta(hours=timezone)

        jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute / 60.0)

        sun_lon = swe.calc_ut(jd, swe.SUN)[0][0]
        moon_lon = swe.calc_ut(jd, swe.MOON)[0][0]

        tithi = get_tithi(moon_lon, sun_lon)
        nakshatra = get_nakshatra(moon_lon)
        yoga = get_yoga(moon_lon, sun_lon)
        paksha = "Shukla" if tithi <= 15 else "Krishna"
        vikram_samvat = dt.year + 57
        mahino = "Dhanu (Solar Month)"  # placeholder
        nakshatra_swami = get_nakshatra_swami(nakshatra)
        lagna_rashi = get_lagna_rashi(jd, latitude, longitude)
        chandra_rashi = int(moon_lon / 30)

        rashi_names = ["Mesha", "Vrushabh", "Mithun", "Kark", "Sinh", "Kanya",
                       "Tula", "Vrushchik", "Dhanu", "Makar", "Kumbh", "Meen"]

        return jsonify({
            "tithi": str(tithi),
            "nakshatra": f"Nakshatra {nakshatra}",
            "nakshatra_swami": nakshatra_swami,
            "yoga": f"Yoga {yoga}",
            "paksha": paksha,
            "vikram_samvat": str(vikram_samvat),
            "mahino": mahino,
            "lagna_rashi": rashi_names[lagna_rashi],
            "chandra_rashi": rashi_names[chandra_rashi]
        })

    except Exception as e:
        print("❌ Error:", str(e))
        print("❌ Traceback:", traceback.format_exc())
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
