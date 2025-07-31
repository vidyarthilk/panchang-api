from flask import Flask, request, jsonify
import swisseph as swe
import datetime
import os

app = Flask(__name__)
swe.set_ephe_path(".")

@app.route("/calculate", methods=["POST"])
def calculate_panchang():
    try:
        data = request.get_json(force=True)
        date_str = data["date"]
        time_str = data["time"]
        latitude = float(data["latitude"])
        longitude = float(data["longitude"])
        timezone = float(data["timezone"])

        dt = datetime.datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        dt_utc = dt - datetime.timedelta(hours=timezone)
        jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute / 60)

        sun_long = swe.calc_ut(jd, swe.SUN)[0][0]
        moon_long = swe.calc_ut(jd, swe.MOON)[0][0]

        # Tithi Calculation
        tithi_deg = (moon_long - sun_long) % 360
        tithi_num = int(tithi_deg / 12)
        tithi_name = tithi_list[tithi_num]

        # Paksha
        paksha = "Shukla" if tithi_num < 15 else "Krishna"

        # Nakshatra
        nak_num = int((moon_long % 360) / (360 / 27))
        nakshatra_name = nakshatra_list[nak_num]
        nakshatra_swami = get_nakshatra_lord(nak_num + 1)

        # Yoga
        yoga_sum = (sun_long + moon_long) % 360
        yoga_num = int(yoga_sum / (360 / 27))
        yoga_name = yoga_list[yoga_num]

        # Solar Month
        mahino = f"{rashi_names[int(sun_long / 30)]} (Solar Month)"

        # Vikram Samvat
        vikram_samvat = dt.year + 57

        # Lagna
        ascmc = swe.houses(jd, latitude, longitude)[1]
        lagna_deg = ascmc[0]
        lagna_rashi = rashi_names[int(lagna_deg / 30)]

        # Chandra Rashi
        chandra_rashi = rashi_names[int(moon_long / 30)]

        return jsonify({
            "tithi": tithi_name,
            "paksha": paksha,
            "nakshatra": nakshatra_name,
            "nakshatra_swami": nakshatra_swami,
            "yoga": yoga_name,
            "mahino": mahino,
            "vikram_samvat": str(vikram_samvat),
            "lagna_rashi": lagna_rashi,
            "chandra_rashi": chandra_rashi
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Lists
rashi_names = ["Mesha", "Vrushabh", "Mithun", "Kark", "Sinh", "Kanya", "Tula", "Vrushchik", "Dhanu", "Makar", "Kumbh", "Meen"]

tithi_list = [
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashti",
    "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi",
    "Trayodashi", "Chaturdashi", "Purnima", "Pratipada", "Dwitiya", "Tritiya",
    "Chaturthi", "Panchami", "Shashti", "Saptami", "Ashtami", "Navami",
    "Dashami", "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Amavasya"
]

nakshatra_list = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula",
    "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

yoga_list = [
    "Vishkumbha", "Preeti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda",
    "Sukarma", "Dhriti", "Shoola", "Ganda", "Vriddhi", "Dhruva", "Vyaghata",
    "Harshana", "Vajra", "Siddhi", "Vyatipata", "Variyana", "Parigha",
    "Shiva", "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma", "Indra", "Vaidhriti"
]

def get_nakshatra_lord(nak_num):
    lords = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
    return lords[(nak_num - 1) % 9]

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
