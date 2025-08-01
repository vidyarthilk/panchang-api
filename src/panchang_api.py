from flask import Flask, request, jsonify
import swisseph as swe
import datetime
import traceback
import os 

app = Flask(__name__)

RASHI_NAMES = ['મેષ', 'વૃષભ', 'મિથુન', 'કર્ક', 'સિંહ', 'કન્યા',
               'તુલા', 'વૃશ્ચિક', 'ધન', 'મકર', 'કુંભ', 'મીન']

NAKSHATRA_NAMES = ['અશ્વિની', 'ભરણી', 'કૃતિકા', 'રોહિણી', 'મૃગશિર્ષ', 'આર્દ્રા',
                   'પુનર્વસુ', 'પુષ્ય', 'આશ્લેષા', 'મઘા', 'પૂર્વા ફાલ્ગુની', 'ઉત્તરા ફાલ્ગુની',
                   'હસ્ત', 'ચિત્રા', 'સ્વાતિ', 'વિશાખા', 'અનુરાધા', 'જ્યેષ્ઠા',
                   'મૂળ', 'પૂર્વાષાઢા', 'ઉત્તરાષાઢા', 'શ્રવણ', 'ધનિષ્ઠા', 'શતભિષા',
                   'પૂર્વા ભાદ્રપદ', 'ઉત્તરા ભાદ્રપદ', 'રેવતી']

YOGA_NAMES = ['વિષ્કુંબ', 'પ્રિતી', 'આયુષ્માન', 'સૌભાગ્ય', 'શોબન', 'અતિગંડ',
              'સુકર્મા', 'ધૃતિ', 'શૂલ', 'ગંડ', 'વૃદ્ધિ', 'ધ્રુવ', 'વ્યાઘાત', 'હરષણ',
              'વજર', 'સિદ્ધિ', 'વ્યતિપાત', 'વારિયાણ', 'પરિઘ', 'શિવ', 'સિદ્ધ', 'સાધ્ય',
              'શુભ', 'શુક્લ', 'બ્રહ્મ', 'ઇન્દ્ર', ' વૈધૃતિ']

TITHI_NAMES = ['પ્રથમા', 'દ્વિતીયા', 'તૃતીયા', 'ચતુર્થી', 'પંચમી', 'ષષ્ટી', 'સપ્તમી',
               'અષ્ટમી', 'નવમી', 'દશમી', 'એકાદશી', 'દ્વાદશી', 'ત્રયોદશી', 'ચતુર્દશી', 'પૂર્ણિમા/અમાવસ્યા']

@app.route("/")
def home():
    return "Panchang API is running", 200
  
@app.route("/calculate", methods=["POST"])
def calculate():
    try:
        print("===== DEBUG START =====")
        print("HEADERS:", request.headers)
        print("RAW BODY:", request.data)
        data = request.get_json(force=True)
        print("JSON PARSED:", data)
        print("===== DEBUG END =====")
      
        data = request.get_json()

        date_str = data["date"]  # "YYYY-MM-DD"
        time_str = data["time"]  # "HH:MM"
        latitude = float(data["latitude"])
        longitude = float(data["longitude"])
        timezone = float(data["timezone"])  # e.g., 5.5

        # Convert to UTC
        dt = datetime.datetime.strptime(date_str + " " + time_str, "%Y-%m-%d %H:%M")
        dt_utc = dt - datetime.timedelta(hours=timezone)

        year = dt_utc.year
        month = dt_utc.month
        day = dt_utc.day
        hour = dt_utc.hour + dt_utc.minute / 60.0

        jd = swe.julday(year, month, day, hour)
        swe.set_topo(longitude, latitude, 0)
        swe.set_sid_mode(swe.SIDM_LAHIRI)

        # Tithi
        sun_long = swe.calc_ut(jd, swe.SUN)[0]
        moon_long = swe.calc_ut(jd, swe.MOON)[0]
      
        print("DEBUG sun_long:", sun_long, type(sun_long))
        print("DEBUG moon_long:", moon_long, type(moon_long))

        jd = swe.julday(year, month, day, hour)

        tithi_float = ((moon_long - sun_long) % 360) / 12
        tithi_index = int(tithi_float)
        tithi_name = TITHI_NAMES[tithi_index % 15]

        # Nakshatra
        nakshatra_float = (moon_long % 360) / (360 / 27)
        nakshatra_index = int(nakshatra_float)
        nakshatra_name = NAKSHATRA_NAMES[nakshatra_index]

        # Yoga
        yoga_float = ((sun_long + moon_long) % 360) / (360 / 27)
        yoga_index = int(yoga_float)
        yoga_name = YOGA_NAMES[yoga_index]

        # Karana
        karana_index = int((tithi_float % 1) * 2)
        karana_name = "કરણ " + str(karana_index + 1)

        # Chandra Rashi
        chandra_rashi_index = int(moon_long / 30)
        chandra_rashi = RASHI_NAMES[chandra_rashi_index]

        # Lagna Rashi
        asc = swe.houses(jd, latitude, longitude, 'P')[0][0]
        lagna_rashi_index = int(asc / 30)
        lagna_rashi = RASHI_NAMES[lagna_rashi_index]

        return jsonify({
            "tithi": tithi_name,
            "nakshatra": nakshatra_name,
            "yoga": yoga_name,
            "karana": karana_name,
            "chandra_rashi": chandra_rashi,
            "lagna_rashi": lagna_rashi
        })

    except Exception as e:
        return jsonify({
            "error": str(e),
            "trace": traceback.format_exc()
        })
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

