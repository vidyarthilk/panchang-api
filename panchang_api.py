from flask import Flask, request, jsonify
import swisseph as swe
import datetime
import traceback
import os

app = Flask(__name__)
swe.set_ephe_path('.')  # eph files ni path set karo

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

        # Convert local time to UTC
        dt = datetime.datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        dt_utc = dt - datetime.timedelta(hours=timezone)
        jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute / 60.0)

        # Get SUN and MOON longitudes
        sun_calc = swe.calc_ut(jd, swe.SUN)[0]
        moon_calc = swe.calc_ut(jd, swe.MOON)[0]

        tithi_deg = (moon_calc - sun_calc) % 360
        tithi = int(tithi_deg / 12) + 1
        paksha = "Shukla" if tithi <= 15 else "Krishna"

        nakshatra = int((moon_calc % 360) / (360 / 27)) + 1
        nakshatra_swami = get_nakshatra_lord(nakshatra)

        yoga = int(((sun_calc + moon_calc) % 360) / (360 / 27)) + 1
        mahino = get_solar_month(sun_calc)
        vikram_samvat = dt.year + 57

        moon_rashi = int(moon_calc / 30)
        lagna_degree = get_lagna_degree(jd, latitude, longitude)
        lagna_rashi = int(lagna_degree / 30)

        rashi_names = ["Mesha", "Vrushabh", "Mithun", "Kark", "Sinh", "Kanya",
                       "Tula", "Vrushchik", "Dhanu", "Makar", "Kumbh", "Meen"]

        response = {
            "tithi": str(tithi),
            "nakshatra": f"Nakshatra {nakshatra}",
            "nakshatra_swami": nakshatra_swami,
            "yoga": f"Yoga {yoga}",
            "paksha": paksha,
            "vikram_samvat": str(vikram_samvat),
            "mahino": mahino,
            "lagna_rashi": rashi_names[lagna_rashi],
            "chandra_rashi": rashi_names[moon_rashi]
        }

        return jsonify(response)

    except Exception as e:
        print("❌ Exception occurred:\n", traceback.format_exc())
        return jsonify({"error": str(e)}), 500

# Helpers
def get_nakshatra_lord(nakshatra):
    lords = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
    return lords[(nakshatra - 1) % 9]

def get_solar_month(sun_longitude):
    months = ["Mesha", "Vrushabh", "Mithun", "Kark", "Sinh", "Kanya",
              "Tula", "Vrushchik", "Dhanu", "Makar", "Kumbh", "Meen"]
    return f"{months[int(sun_longitude / 30)]} (Solar Month)"

def get_lagna_degree(jd, lat, lon):
    houses, ascmc = swe.houses_ex(jd, lat, lon, b'A')
    return ascmc[0]  # Lagna

# Start
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
