from flask import Flask, request, jsonify
import swisseph as swe
import datetime
import traceback
import os

app = Flask(__name__)
swe.set_ephe_path('.')

@app.route('/calculate', methods=['POST'])
def calculate_panchang():
    try:
        data = request.get_json(force=True)
        print("🔥 Request received:", data)

        # Input parsing
        date_str = data['date']
        time_str = data['time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        timezone = float(data['timezone'])

        # Datetime conversion
        dt = datetime.datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        dt_utc = dt - datetime.timedelta(hours=timezone)
        jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute / 60.0)

        # Planet positions
        sun_long = swe.calc_ut(jd, swe.SUN)[0]
        moon_long = swe.calc_ut(jd, swe.MOON)[0]

        # Tithi
        tithi_deg = (moon_long - sun_long) % 360
        tithi_num = int(tithi_deg / 12)
        tithi_names = [
            "Pratipada", "Dvitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi",
            "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi",
            "Trayodashi", "Chaturdashi", "Purnima", "Pratipada", "Dvitiya", "Tritiya",
            "Chaturthi", "Panchami", "Shashthi", "Saptami", "Ashtami", "Navami",
            "Dashami", "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Amavasya"
        ]
        paksha = "Shukla" if tithi_num < 15 else "Krishna"
        tithi = tithi_names[tithi_num]

        # Nakshatra
        nakshatra_num = int((moon_long % 360) / (360 / 27))
        nakshatra_names = [
            "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
            "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
            "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
            "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
            "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
        ]
        nakshatra = nakshatra_names[nakshatra_num]
        nakshatra_swami = get_nakshatra_lord(nakshatra_num + 1)

        # Yoga
        yoga_num = int(((sun_long + moon_long) % 360) / (360 / 27))
        yoga_names = [
            "Vishkumbha", "Preeti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda", "Sukarma", "Dhriti", "Shoola",
            "Ganda", "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra", "Siddhi", "Vyatipata", "Variyana", "Parigha",
            "Shiva", "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma", "Indra", "Vaidhriti"
        ]
        yoga = yoga_names[yoga_num]

        # Solar Month
        solar_month_names = ["Mesha", "Vrushabh", "Mithun", "Kark", "Sinh", "Kanya", "Tula", "Vrushchik", "Dhanu", "Makar", "Kumbh", "Meen"]
        mahino = f"{solar_month_names[int(sun_long / 30)]} (Solar Month)"
        vikram_samvat = dt.year + 57

        # Rashi Calculations
        moon_rashi = solar_month_names[int(moon_long / 30)]
        asc = get_lagna_rashi(jd, latitude, longitude)
        lagna_rashi = solar_month_names[asc]

        return jsonify({
            "tithi": tithi,
            "paksha": paksha,
            "nakshatra": nakshatra,
            "nakshatra_swami": nakshatra_swami,
            "yoga": yoga,
            "mahino": mahino,
            "vikram_samvat": str(vikram_samvat),
            "chandra_rashi": moon_rashi,
            "lagna_rashi": lagna_rashi
        })

    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

# Utility
def get_nakshatra_lord(nakshatra):
    lords = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
    return lords[(nakshatra - 1) % 9]

def get_lagna_rashi(jd, lat, lon):
    _, ascmc = swe.houses_ex(jd, lat, lon, b'A')
    asc_deg = ascmc[0]  # ASC degree
    return int(asc_deg / 30)

# Start server
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
