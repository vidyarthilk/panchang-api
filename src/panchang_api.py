from flask import Flask, request, jsonify
import swisseph as swe
import datetime
import pytz
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

swe.set_ephe_path('.')  # or your actual ephemeris path

rashi_names = [
    "મેષ", "વૃષભ", "મિથુન", "કર્ક", "સિંહ", "કન્યા",
    "તુલા", "વૃશ્ચિક", "ધન", "મકર", "કુંભ", "મીન"
]

nakshatra_names = [
    "અશ્વિની", "ભરણી", "કૃતિકા", "રોહિણી", "મૃગશિરા", "આરદ્રા",
    "પુનર્વસુ", "પુષ્ય", "આશ્લેષા", "મઘા", "પૂર્વા ફાલ્ગુની", "ઉત્તરા ફાલ્ગુની",
    "હસ્ત", "ચિત્રા", "स्वાતિ", "વિશાખા", "અનુરાધા", "જ્યેષ્ઠા",
    "મૂળ", "પૂર્વા ષાઢા", "ઉત્તરા ષાઢા", "શ્રવણ", "ધનિષ્ઠા", "શતભિષા",
    "પૂર્વા ભાદ્રપદ", "ઉત્તરા ભાદ્રપદ", "રેવતી"
]

nakshatra_swamies = [
    "કેતુ", "શુક્ર", "સૂર્ય", "ચંદ્ર", "મંગળ", "રાહુ",
    "ગુરુ", "શનિ", "બુધ", "કેતુ", "શુક્ર", "સૂર્ય",
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
    "બાવ", "બાલવ", "કૌલવ", "તૈતિલ", "ગરજ", "વણિજ", "વિષ્ટિ",  # 0–6
    "બાવ", "બાલવ", "કૌલવ", "તૈતિલ", "ગરજ", "વણિજ", "વિષ્ટિ",  # 7–13
    "બાવ", "બાલવ", "કૌલવ", "તૈતિલ", "ગરજ", "વણિજ", "વિષ્ટિ",  # 14–20
    "બાવ", "બાલવ", "કૌલવ", "તૈતિલ", "ગરજ", "વણિજ", "વિષ્ટિ",  # 21–27
    "બાવ", "બાલવ", "કૌલવ", "તૈતિલ", "ગરજ", "વણિજ", "વિષ્ટિ",  # 28–34
    "બાવ", "બાલવ", "કૌલવ", "તૈતિલ", "ગરજ", "વણિજ", "વિષ્ટિ",  # 35–41
    "બાવ", "બાલવ", "કૌલવ", "તૈતિલ", "ગરજ", "વણિજ", "વિષ્ટિ",  # 42–48
    "બાવ", "બાલવ", "કૌલવ", "તૈતિલ", "ગરજ", "વણિજ", "વિષ્ટિ",  # 49–55
    "શકુનિ", "ચતુષ્પદ", "નાગ", "કિસ્તુઘ્ન"                    # 56–59
]


@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    date_str = data['date']  # format: yyyy-mm-dd
    time_str = data['time']  # format: hh:mm
    latitude = float(data['latitude'])
    longitude = float(data['longitude'])
    timezone = float(data['timezone'])

    dt = datetime.datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    dt_utc = dt - datetime.timedelta(hours=timezone)
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute / 60.0)

    # Moon for Chandra Rashi
    moon_long = swe.calc_ut(jd, swe.MOON)[0]
    chandra_rashi = rashi_names[int(moon_long // 30)]

    # Ascendant (Lagna) sign
    lagna = swe.houses_ex(jd, latitude, longitude, b'A')[1][0]
    lagna_rashi = rashi_names[int(lagna // 30)]

    # Nakshatra
    nakshatra_index = int((moon_long * 27) / 360)
    nakshatra = nakshatra_names[nakshatra_index]
    nakshatra_swami = nakshatra_swamies[nakshatra_index]

    # Tithi
    sun_long = swe.calc_ut(jd, swe.SUN)[0]
    tithi_float = (moon_long - sun_long) % 360 / 12
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

    # Vikram Samvat & Month (approx)
    vikram_samvat = dt.year + 57
    mahino = swe.get_month_name(dt.month) if hasattr(swe, 'get_month_name') else "શ્રાવણ"

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
