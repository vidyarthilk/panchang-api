from flask import Flask, request, jsonify
import swisseph as swe
import datetime
import traceback

app = Flask(__name__)
swe.set_ephe_path('.')  # Local folder or set to eph file path

@app.route('/calculate', methods=['POST'])
def calculate_panchang():
    try:
        data = request.get_json(force=True)
        print("🔥 Raw request data:", data)

         # Extract input
        date_str = data['date']  # e.g. "2025-07-29"
        time_str = data['time']  # e.g. "12:30"
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        timezone = float(data['timezone'])

        dt = datetime.datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        dt = dt - datetime.timedelta(hours=timezone)  # convert to UTC
        jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute / 60.0)

        print(f"🧮 Julian Day: {jd}")

        # Get sun and moon longitudes
        sun = swe.calc_ut(jd, swe.SUN)[0]
        moon = swe.calc_ut(jd, swe.MOON)[0]

        # Tithi calculation
        tithi_deg = (moon - sun) % 360
        tithi = int(tithi_deg / 12) + 1

        # Nakshatra calculation
        nakshatra = int((moon % 360) / (360 / 27)) + 1
        nakshatra_swami = get_nakshatra_lord(nakshatra)

        # Yoga calculation
        sun_moon_sum = (sun + moon) % 360
        yoga = int(sun_moon_sum / (360 / 27)) + 1

        # Paksha
        paksha = "Shukla" if tithi <= 15 else "Krishna"

        # Vikram Samvat
        vikram_samvat = dt.year + 57

        # Solar month (mahino)
        mahino = get_solar_month(sun)

        # Lagna and Chandra rashi (simplified real version)
        asc = get_lagna_rashi(jd, latitude, longitude)
        moon_rashi = int(moon / 30)

        rashi_names = ["Mesha", "Vrushabh", "Mithun", "Kark", "Sinh", "Kanya",
                       "Tula", "Vrushchik", "Dhanu", "Makar", "Kumbh", "Meen"]

        response = {
            "tithi": tithi,
            "nakshatra": f"Nakshatra {nakshatra}",
            "nakshatra_swami": nakshatra_swami,
            "yoga": f"Yoga {yoga}",
            "paksha": paksha,
            "vikram_samvat": vikram_samvat,
            "mahino": mahino,
            "lagna_rashi": rashi_names[asc],
            "chandra_rashi": rashi_names[moon_rashi]
        }
        return jsonify(response)

        except Exception as e:
        import traceback
        print("❌ Full traceback:\n", traceback.format_exc())
        return jsonify({"error": str(e)}), 500


def get_nakshatra_lord(nakshatra):
    lords = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
    return lords[(nakshatra - 1) % 9]

def get_solar_month(sun_longitude):
    months = ["Mesha", "Vrushabh", "Mithun", "Kark", "Sinh", "Kanya",
              "Tula", "Vrushchik", "Dhanu", "Makar", "Kumbh", "Meen"]
    month_index = int(sun_longitude / 30)
    return f"{months[month_index]} (Solar Month)"

def get_lagna_rashi(jd, lat, lon):
    asc = swe.houses_ex(jd, lat, lon, b'A')[0][0]  # Ascendant
    return int(asc / 30)

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
