from flask import Flask, request, jsonify, send_from_directory
import os
import requests
import mysql.connector

app = Flask(__name__)


# ==========================================
# FRONTEND FOLDER
# ==========================================

frontend_folder = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "frontend"
    )
)


# ==========================================
# TOMTOM API KEY
# ==========================================

TOMTOM_API_KEY = "YOUR_TOMTOM_API_KEY"


# ==========================================
# MYSQL DATABASE CONNECTION
# ==========================================

def get_db_connection():

    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Asiy@123.",
        database="accident_ai"
    )


# ==========================================
# HOME PAGE
# ==========================================

@app.route("/")
def home():

    return send_from_directory(
        frontend_folder,
        "index.html"
    )


# ==========================================
# FRONTEND FILES
# ==========================================

@app.route("/<path:filename>")
def frontend_files(filename):

    return send_from_directory(
        frontend_folder,
        filename
    )


# ==========================================
# AUTOMATIC WEATHER
# Open-Meteo - No API Key Required
# ==========================================

@app.route("/weather", methods=["GET"])
def weather():

    latitude = request.args.get("latitude")
    longitude = request.args.get("longitude")

    if not latitude or not longitude:

        return jsonify({
            "error": "Latitude and longitude are required"
        }), 400

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,weather_code",
        "timezone": "auto"
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        print("WEATHER STATUS:", response.status_code)
        print("WEATHER RESPONSE:", response.text)

        if response.status_code != 200:

            return jsonify({
                "error": "Unable to get weather"
            }), 500

        data = response.json()

        current = data.get("current", {})

        temperature = current.get(
            "temperature_2m",
            0
        )

        weather_code = current.get(
            "weather_code",
            0
        )

        if weather_code in [
            51, 53, 55,
            56, 57,
            61, 63, 65,
            66, 67,
            80, 81, 82,
            95, 96, 99
        ]:

            weather_type = "Rainy"

        elif weather_code in [
            45, 48
        ]:

            weather_type = "Foggy"

        else:

            weather_type = "Clear"

        return jsonify({

            "weather": weather_type,

            "temperature": temperature

        })

    except Exception as e:

        print("WEATHER ERROR:", str(e))

        return jsonify({

            "error": str(e)

        }), 500


# ==========================================
# AUTOMATIC TRAFFIC
# ==========================================

@app.route("/traffic", methods=["GET"])
def traffic():

    latitude = request.args.get("latitude")
    longitude = request.args.get("longitude")

    if not latitude or not longitude:

        return jsonify({

            "error":
                "Latitude and longitude are required"

        }), 400


    # ======================================
    # DEMO TRAFFIC IF API KEY NOT ADDED
    # ======================================

    if TOMTOM_API_KEY == "YOUR_TOMTOM_API_KEY":

        return jsonify({

            "traffic_density":
                "Medium",

            "current_speed":
                0,

            "free_flow_speed":
                0,

            "message":
                "Demo traffic value used"

        })


    url = (
        "https://api.tomtom.com/"
        "traffic/services/"
        "4/flowSegmentData/"
        "absolute/10/json"
    )


    params = {

        "key":
            TOMTOM_API_KEY,

        "point":
            f"{latitude},{longitude}",

        "unit":
            "kmph"

    }


    try:

        response = requests.get(

            url,

            params=params,

            timeout=10

        )


        print(
            "TRAFFIC STATUS:",
            response.status_code
        )

        print(
            "TRAFFIC RESPONSE:",
            response.text
        )


        if response.status_code != 200:

            return jsonify({

                "error":
                    "Traffic API failed",

                "traffic_density":
                    "Medium"

            }), 200


        data = response.json()


        flow = data.get(
            "flowSegmentData",
            {}
        )


        current_speed = flow.get(
            "currentSpeed",
            0
        )


        free_flow_speed = flow.get(
            "freeFlowSpeed",
            0
        )


        if free_flow_speed <= 0:

            traffic_density = "Medium"

        else:

            ratio = (
                current_speed /
                free_flow_speed
            )


            if ratio < 0.40:

                traffic_density = "High"

            elif ratio < 0.70:

                traffic_density = "Medium"

            else:

                traffic_density = "Low"


        return jsonify({

            "traffic_density":
                traffic_density,

            "current_speed":
                current_speed,

            "free_flow_speed":
                free_flow_speed

        })


    except Exception as e:

        print(
            "TRAFFIC ERROR:",
            str(e)
        )


        return jsonify({

            "error":
                str(e),

            "traffic_density":
                "Medium"

        }), 200


# ==========================================
# ACCIDENT PREDICTION
# ==========================================

@app.route("/predict", methods=["POST"])
def predict():

    data = request.get_json()


    if not data:

        return jsonify({

            "error":
                "No data received"

        }), 400


    latitude = data.get(
        "latitude"
    )

    longitude = data.get(
        "longitude"
    )

    weather = data.get(
        "weather",
        "Clear"
    )

    traffic_density = data.get(
        "traffic_density",
        "Medium"
    )

    road_condition = data.get(
        "road_condition"
    )

    vehicle_speed = data.get(
        "vehicle_speed"
    )

    time = data.get(
        "time"
    )


    # ==========================================
    # RISK SCORE
    # ==========================================

    risk_score = 0


    # ==========================================
    # TRAFFIC
    # ==========================================

    if traffic_density == "High":

        risk_score += 3

    elif traffic_density == "Medium":

        risk_score += 2


    # ==========================================
    # ROAD CONDITION
    # ==========================================

    if road_condition == "Poor":

        risk_score += 3

    elif road_condition == "Average":

        risk_score += 2


    # ==========================================
    # VEHICLE SPEED
    # ==========================================

    try:

        vehicle_speed = float(
            vehicle_speed
        )

    except:

        vehicle_speed = 0


    if vehicle_speed > 80:

        risk_score += 3

    elif vehicle_speed > 60:

        risk_score += 2


    # ==========================================
    # WEATHER
    # ==========================================

    if weather == "Rainy":

        risk_score += 2

    elif weather == "Foggy":

        risk_score += 2


    # ==========================================
    # NIGHT
    # ==========================================

    if time == "Night":

        risk_score += 2


    # ==========================================
    # FINAL PREDICTION
    # ==========================================

    if risk_score >= 7:

        prediction = "High Risk"

    elif risk_score >= 4:

        prediction = "Medium Risk"

    else:

        prediction = "Low Risk"


    # ==========================================
    # SAVE TO MYSQL
    # ==========================================

    database_saved = False


    try:

        db = get_db_connection()

        cursor = db.cursor()


        sql = """
        INSERT INTO accident_ai.predictions
        (
            latitude,
            longitude,
            weather,
            traffic_density,
            road_condition,
            vehicle_speed,
            time_period,
            risk_level,
            risk_score
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        """


        values = (

            latitude,

            longitude,

            weather,

            traffic_density,

            road_condition,

            vehicle_speed,

            time,

            prediction,

            risk_score

        )


        cursor.execute(
            sql,
            values
        )


        db.commit()


        cursor.close()

        db.close()


        database_saved = True


        print(
            "DATABASE: Prediction saved successfully"
        )


    except Exception as e:

        print(
            "DATABASE ERROR:",
            str(e)
        )


    # ==========================================
    # TERMINAL OUTPUT
    # ==========================================

    print("--------------------------------")

    print(
        "Prediction:",
        prediction
    )

    print(
        "Risk Score:",
        risk_score
    )

    print(
        "Weather:",
        weather
    )

    print(
        "Traffic:",
        traffic_density
    )

    print(
        "Database Saved:",
        database_saved
    )

    print("--------------------------------")


    # ==========================================
    # SEND RESPONSE TO FRONTEND
    # ==========================================

    return jsonify({

        "prediction":
            prediction,

        "risk_score":
            risk_score,

        "latitude":
            latitude,

        "longitude":
            longitude,

        "weather":
            weather,

        "traffic_density":
            traffic_density,

        "database_saved":
            database_saved

    })


# ==========================================
# RUN SERVER
# ==========================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )