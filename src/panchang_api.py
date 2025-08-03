from flask import Flask, request, jsonify
import swisseph as swe
import datetime
import pytz
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

swe.set_ephe_path('.')  # Path where ephemeris files are stored

rashi_names = [
    "મેષ", "વૃષભ", "મિથુન", "કર્ક", "સિંહ", "કન્યા",
    "તુલા", "વૃશ્ચિક", "ધન", "મકર", "કુંભ", "મીન"
]

nakshatra_names = [
    "અશ્વિની", "ભરણી", "કૃતિકા", "રોહિણી", "મૃગશિરા", "આરદ્રા",
    "પુનર્વસુ", "પુષ્ય", "આશ્લેષા", "મઘા", "પૂર્વા ફાલ્ગુની", "ઉત્તરા ફાલ્ગુની",
    "હસ્ત", "ચિત્રા", "સ્વાતિ", "વિશાખા", "અનુરાધા", "જ્યેષ્ઠા",
    "મૂળ", "પૂર્વા ષાઢા", "ઉત્તરા ષાઢા", "શ્રવણ", "ધનિષ્ઠા", "શતભિષા",
    "પૂર્વા ભાદ્રપદ", "ઉત્તરા ભાદ્રપદ", "રેવતી"
]

nakshatra_swamies = [
    "કેતુ", "શુક્ર", "સૂર્ય", "ચંદ્ર", "મંગળ", "રાહુ",
    "ગુરૂ", "શનિ", "બુધ", "કેતુ", "શુક્ર", "સૂર્ય",
    "ચંદ્ર", "મંગળ", "રાહુ", "ગુરૂ", "શનિ", "બુધ",
    "કેતુ", "શુક્ર", "સૂર્ય", "ચંદ્ર", "મંગળ", "રાહુ",
    "ગુરૂ", "શનિ", "બુધ"
]

yoga_names = [
    "વિષ્કુંબ", "પ્રિતિ", "આયુષ્માન", "સૌભાગ્ય", "શોબન", "અતિગંડ",
    "સુકર્મા", "ધૃતિ", "શૂલ", "ગંડ", "વૃદ્ધિ", "ધ્રુવ",
    "વ્યાઘાત", "હરશણ", "વજર", "સિદ્ધિ", "વ્યતિપાત", "વરીયાન",
    "પરિઘ", "શિવ", "સિદ્ધ", "સાધ્ય", "શુભ", "શુક્લ",
    "બ્રહ્મ", "ઇન્દ્ર", "વૈધૃતિ"
]

karana_cycle = [
    "બાવ", "બાલવ", "કૌલવ", "તૈતિલ", "ગરજ", "વણિજ", "વિષ્ટિ",
    "શકુનિ", "ચતુષ્પદ", "નાગ", "કિસ્તુઘ્ન"
] + ["બાવ", "બાલવ", "કૌલવ", "તૈતિલ", "ગરજ", "વણિજ", "વિષ્ટિ"] * 7

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    date_str = data['date']  # yyyy-mm-dd
    time_str = data['time']  # HH:MM
    latitude = float(data['latitude'])
    longitude = float(data['longitude'])
    timezone = float(data['timezone'])

    dt = datetime.datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    dt_utc = dt - datetime.timedelta(hours=timezone)
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute / 60.0)

    # Chandra Rashi
    moon_result = swe.calc_ut(jd, swe.MOON)
    moon_long = moon_result[0][0}
    chandra_rashi = rashi_names[int(moon_long // 30)]


    # Lagna Rashi
    houses, asc = swe.houses(jd, latitude, longitude)
    lagna_rashi = rashi_names[int(asc // 30)]

    # Nakshatra & Swami
    nakshatra_index = int((moon_long * 27) / 360)
    nakshatra = nakshatra_names[nakshatra_index]
    nakshatra_swami = nakshatra_swamies[nakshatra_index]

    # Tithi & Paksha
    sun_long = swe.calc_ut(jd, swe.SUN)[0]
    tithi_float = ((moon_long - sun_long + 360) % 360) / 12
    tithi_index = int(tithi_float)
    tithi_names = [
        "પ્રતિપદા", "દ્વિતિયા", "તૃતિયા", "ચતુર્થી", "પંચમી",
        "ષષ્ઠી", "સપ્તમી", "અષ્ટમી", "નવમી", "દશમી",
        "એકાદશી", "દ્વાદશી", "ત્રયોદશી", "ચતુર્દશી", "પૂર્ણિમા/અમાવસ્યા"
    ]
    tithi = tithi_names[tithi_index % 15]
    paksha = "શુક્લ પક્ષ" if tithi_index < 15 else "કૃષ્ણ પક્ષ"

    # Karana
    karana_index = int((tithi_float % 1) * 2)
    karana_number = tithi_index * 2 + karana_index
    karana_name = karana_cycle[karana_number % 60]

    # Yoga
    total_long = (sun_long + moon_long) % 360
    yoga_index = int((total_long * 27) / 360)
    yoga = yoga_names[yoga_index]

    # Vikram Samvat & Hindu Mahino (placeholder)
    vikram_samvat = dt.year + 57
    mahino = "શ્રાવણ"  # or use more advanced logic later

    return jsonify({
        "tithi": tithi,
        "paksha": paksha,
        "karana": karana_name,
        "yoga": yoga,
        "nakshatra": nakshatra,
        "nakshatra_swami": nakshatra_swami,
        "chandra_rashi": chandra_rashi,
        "lagna_rashi": lagna_rashi,
        "mahino": mahino,
        "vikram_samvat": str(vikram_samvat)
    })

if __name__ == '__main__':
    app.run(debug=True)
