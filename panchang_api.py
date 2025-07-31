from flask import Flask, request, jsonify
import swisseph as swe
import datetime
import traceback
import os

app = Flask(__name__)
swe.set_ephe_path('.')  # eph files ni path

@app.route('/calculate', methods=['POST'])
def calculate_panchang():
    try:
        data = request.get_json(force=True)
        print("🔥 Request received:", data)

        # Input extract
        date_str = data['date']
        time_str = data['time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        timezone = float(data['timezone'])

        # Convert to UTC datetime
        dt_local = datetime.datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        dt_utc = dt_local - datetime.timedelta(hours=timezone)
        jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute / 60.0)

        # Longitudes of Sun & Moon
        sun_long = swe.calc_ut(jd, swe.SUN)[0]
        moon_long = swe.calc_ut(jd, swe.MOON)[0]

        # Tithi
        tithi_deg = (moon_long - sun_long) % 360
        tithi = int(tithi_deg / 12) + 1
        paksha = "Shukla" if tithi <= 15 else "Krishna"

        # Nakshatra
        nakshatra = int((moon_long % 360) / (360 / 27)) + 1
        nakshatra_swami = get_nakshatra_lord(nakshatra)

        # Yoga
        yoga = int(((sun_long + moon_long) % 360) / (360 / 27)) + 1

        # Vikram Samvat and Solar Month
        vikram_samvat = dt_local.year + 57
        mahino = get_solar_month(sun_long)

        # Chandra Rashi (Moon Sign)
        moon_rashi = int(moon_long / 30)

        # Lagna Rashi (Ascendant)
        asc_data = swe.houses_ex(jd, latitude, longitude, b'A')
        lagna_degree = asc_data[1][0]  # ascmc[0] = Ascendant degree
        lagna_rashi = int(lagna_degree / 30)

        rashi_names = ["Mesha", "Vrushabh", "Mithun", "Kark", "Sinh", "Kanya",
                       "Tula", "Vrushchik", "Dhanu", "Makar", "Kumbh", "Meen"]

        result = {
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

        return jsonify(result)

    except Exception as e:
        print("❌ Error:\n", traceback.format_exc())
        return jsonify({"error": str(e)}), 500

# Utility Functions
def get_nakshatra_lord(nakshatra):
    lords = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
    return lords[(nakshatra - 1) % 9]

def get_solar_month(sun_long):
    months = ["Mesha", "Vrushabh", "Mithun", "Kark", "Sinh", "Kanya",
              "Tula", "Vrushchik", "Dhanu", "Makar", "Kumbh", "Meen"]
    return f"{months[int(sun_long / 30)]} (Solar Month)"

# Main
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
