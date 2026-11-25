let automaticWeather = "";
let automaticTraffic = "";

function goToPrediction() {
    document.getElementById("prediction").scrollIntoView({
        behavior: "smooth"
    });
}


// ===============================
// CURRENT TIME + PERIOD
// ===============================

function getTimePeriod() {
    const hour = new Date().getHours();

    if (hour >= 5 && hour < 12) {
        return "Morning";
    } 
    else if (hour >= 12 && hour < 17) {
        return "Afternoon";
    } 
    else if (hour >= 17 && hour < 21) {
        return "Evening";
    } 
    else {
        return "Night";
    }
}

function getAutomaticTime() {

    const now = new Date();

    let hours = now.getHours();
    let minutes = now.getMinutes();

    let ampm = hours >= 12 ? "PM" : "AM";

    let displayHours = hours % 12;

    if (displayHours === 0) {
        displayHours = 12;
    }

    minutes = minutes.toString().padStart(2, "0");

    const period = getTimePeriod();

    const fullTime =
        displayHours + ":" + minutes + " " + ampm + " - " + period;

    const timeBox = document.getElementById("time");

    if (timeBox) {
        timeBox.value = fullTime;
    }
}


// Run immediately
getAutomaticTime();

// Update every 1 minute
setInterval(getAutomaticTime, 60000);


// ===============================
// LIVE LOCATION
// ===============================

document.getElementById("locationBtn").addEventListener("click", function () {

    const status = document.getElementById("locationStatus");

    if (!navigator.geolocation) {
        status.innerText = "Geolocation is not supported by your browser.";
        return;
    }

    status.innerText = "Detecting live location...";

    navigator.geolocation.getCurrentPosition(

        function (position) {

            const latitude = position.coords.latitude;
            const longitude = position.coords.longitude;

            document.getElementById("latitude").value =
                latitude.toFixed(6);

            document.getElementById("longitude").value =
                longitude.toFixed(6);

            status.innerText =
                "Location detected successfully ✅";

            getWeather(latitude, longitude);
            getTraffic(latitude, longitude);
        },

        function (error) {

            status.innerText =
                "Unable to get location. Please allow location permission.";
        }
    );
});


// ===============================
// WEATHER
// ===============================

function getWeather(latitude, longitude) {

    fetch(
        `/weather?latitude=${latitude}&longitude=${longitude}`
    )

    .then(response => response.json())

    .then(data => {

        if (data.weather) {
            automaticWeather = data.weather;
        } 
        else {
            automaticWeather = "Clear";
        }

        document.getElementById("weather").value =
            automaticWeather;
    })

    .catch(error => {

        console.log("Weather error:", error);

        automaticWeather = "Clear";

        document.getElementById("weather").value =
            automaticWeather;
    });
}


// ===============================
// TRAFFIC
// ===============================

function getTraffic(latitude, longitude) {

    fetch(
        `/traffic?latitude=${latitude}&longitude=${longitude}`
    )

    .then(response => response.json())

    .then(data => {

        if (data.traffic_density) {
            automaticTraffic = data.traffic_density;
        } 
        else {
            automaticTraffic = "Low";
        }

        document.getElementById("traffic_density").value =
            automaticTraffic;
    })

    .catch(error => {

        console.log("Traffic error:", error);

        automaticTraffic = "Low";

        document.getElementById("traffic_density").value =
            automaticTraffic;
    });
}


// ===============================
// PREDICTION
// ===============================

document.getElementById("predictBtn").addEventListener("click", function () {

    const latitude =
        document.getElementById("latitude").value;

    const longitude =
        document.getElementById("longitude").value;

    const roadCondition =
        document.getElementById("road_condition").value;

    const vehicleSpeed =
        document.getElementById("vehicle_speed").value;

    const resultBox =
        document.getElementById("result");

    if (!latitude || !longitude) {

        resultBox.innerHTML =
            "⚠️ Please click Use Live Location first.";

        return;
    }

    if (!roadCondition) {

        resultBox.innerHTML =
            "⚠️ Please select Road Condition.";

        return;
    }

    if (!vehicleSpeed) {

        resultBox.innerHTML =
            "⚠️ Please enter Vehicle Speed.";

        return;
    }


    // Get period separately for backend
    const timePeriod = getTimePeriod();


    const data = {

        latitude: parseFloat(latitude),

        longitude: parseFloat(longitude),

        weather: automaticWeather || "Clear",

        traffic_density: automaticTraffic || "Low",

        road_condition: roadCondition,

        vehicle_speed: parseFloat(vehicleSpeed),

        time: timePeriod
    };


    resultBox.innerHTML =
        "⏳ Predicting accident risk...";


    fetch("/predict", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify(data)

    })

    .then(response => response.json())

    .then(result => {

        if (result.error) {

            resultBox.innerHTML =
                "❌ " + result.error;

            return;
        }


        resultBox.innerHTML = `
            <h2>Prediction Result</h2>
            <p>
                <b>Risk Level:</b>
                ${result.prediction}
            </p>
            <p>
                <b>Risk Score:</b>
                ${result.risk_score || "N/A"}
            </p>
        `;


        // Emergency Alert
        if (
            result.prediction &&
            result.prediction.toLowerCase().includes("high")
        ) {

            showEmergencyAlert(latitude, longitude);

        } 
        else {

            document.getElementById("emergencyAlert").style.display =
                "none";
        }

    })

    .catch(error => {

        console.log(error);

        resultBox.innerHTML =
            "❌ Something went wrong. Please try again.";
    });

});


// ===============================
// EMERGENCY ALERT
// ===============================

function showEmergencyAlert(latitude, longitude) {

    const alertBox =
        document.getElementById("emergencyAlert");

    alertBox.style.display = "block";


    document.getElementById("alertLatitude").innerText =
        latitude;

    document.getElementById("alertLongitude").innerText =
        longitude;


    document.getElementById("coordinates").innerText =
        `Location: ${latitude}, ${longitude}`;


    // Google Maps
    document.getElementById("mapsBtn").onclick =
        function () {

            const mapsURL =
                `https://www.google.com/maps?q=${latitude},${longitude}`;

            window.open(mapsURL, "_blank");
        };


    // Family Call
    document.getElementById("callBtn").onclick =
        function () {

            window.location.href =
                "tel:9999999999";
        };
}


// ===============================
// NAVIGATION
// ===============================

document.querySelectorAll(".nav-links a").forEach(function (link) {

    link.addEventListener("click", function (event) {

        const target =
            this.getAttribute("href");

        if (target === "#emergencyAlert") {

            event.preventDefault();

            const alertBox =
                document.getElementById("emergencyAlert");

            if (alertBox.style.display === "block") {

                alertBox.scrollIntoView({
                    behavior: "smooth"
                });

            } 
            else {

                alert(
                    "Emergency Alert will appear automatically when High Risk is detected."
                );
            }
        }
    });
});