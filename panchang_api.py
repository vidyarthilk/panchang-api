from flask import Flask, request, jsonify
import swisseph as swe
import datetime

app = Flask(__name__)
swe.set_ephe_path('.')  # Or path where your Swiss Ephemeris .se1 files are stored

# Lords of each nakshatra (fixed)
nakshatra_lords = [
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"
]

rashi_names = [
    "Mesha", "Vrushabha", "Mithun", "Karka", "Simha", "Kanya",
    "Tula", "Vrushchik", "Dhanu", "Makar", "Kumbh", "Meen"
]

@app.route('/calculate', methods=['POST'])
def calculate_panchang():
    try:
        data = request.get_json(force=True)
        print(f"🔥 Raw request data: {data}")

        date = data['date']
        time = data['time']
        lat = float(data['latitude'])
        lon = float(data['longitude'])
        tz = float(data['timezone'])

        print(f"✅ Parsed date={date}, time={time}, lat={lat}, lon={lon}, tz={tz}")

        # Convert to UTC
        dt = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        utc_dt = dt - datetime.timedelta(hours=tz)
        jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour + utc_dt.minute / 60.0)
        print(f"🧮 Julian Day: {jd}")

        # FIXED SUN & MOON
        sun_long = swe.calc_ut(jd, swe.SUN)[0][0]
        moon_long = swe.calc_ut(jd, swe.MOON)[0][0]
        print(f"☀️ Sun: {sun_long}°, 🌙 Moon: {moon_long}°")

        # Proceed as before...
return jsonify({...})  # final response
    except Exception as e:
    import traceback
    print("❌ Full traceback:\n", traceback.format_exc())
    return jsonify({"error": str(e)}), 500


    # Tithi
    tithi_deg = (moon_long - sun_long) % 360
    tithi_num = int(tithi_deg / 12) + 1
    paksha = "Shukla" if tithi_num <= 15 else "Krishna"

    # Nakshatra
    nakshatra_index = int(moon_long / (360 / 27))
    nakshatra_name = f"Nakshatra {nakshatra_index + 1}"
    nakshatra_lord = nakshatra_lords[nakshatra_index]

    # Yoga
    yoga_index = int(((sun_long + moon_long) % 360) / (360 / 27))
    yoga_name = f"Yoga {yoga_index + 1}"

    # Chandra Rashi
    chandra_rashi_index = int(moon_long / 30)
    chandra_rashi = rashi_names[chandra_rashi_index]

    # Lagna Rashi (approx from sunrise + time)
    sunrise_hour = 6  # assuming 6 AM as sunrise (adjust later with geolocation)
    total_hours = utc_dt.hour + utc_dt.minute / 60.0
    lagna_deg = ((total_hours - sunrise_hour) * 15) % 360
    lagna_rashi_index = int(lagna_deg / 30)
    lagna_rashi = rashi_names[lagna_rashi_index]

    # Vikram Samvat (basic)
    vikram_year = dt.year + 57

    # Mahino (solar)
    mahino_index = int(sun_long / 30)
    mahino = rashi_names[mahino_index] + " (Solar Month)"

    return jsonify({
        "vikram_samvat": vikram_year,
        "tithi": tithi_num,
        "paksha": paksha,
        "mahino": mahino,
        "nakshatra": nakshatra_name,
        "nakshatra_swami": nakshatra_lord,
        "yoga": yoga_name,
        "chandra_rashi": chandra_rashi,
        "lagna_rashi": lagna_rashi
    })

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

