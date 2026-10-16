from flask import Flask, render_template, request, jsonify
import random
from datetime import datetime

app = Flask(__name__)

# État en mémoire simulant la base de données de l'IoT SNEL
meter_state = {
    "meter_number": "0429-8832-11",
    "current_kwh": 14.5,
    "tariff_per_kwh": 325,
    "latest_token": "4829-1029-3841-5920",
    "history": [
        {
            "date": "24/10/2026 14:22",
            "meter": "0429-8832-11",
            "amount": 10000,
            "kwh": 30.7,
            "operator": "Airtel Money",
            "token": "4829-1029-3841-5920"
        },
        {
            "date": "10/10/2026 09:15",
            "meter": "0429-8832-11",
            "amount": 5000,
            "kwh": 15.3,
            "operator": "M-Pesa",
            "token": "1109-4482-9012-3341"
        },
        {
            "date": "28/09/2026 18:40",
            "meter": "1102-4410-99",
            "amount": 20000,
            "kwh": 61.5,
            "operator": "Orange Money",
            "token": "9938-2102-4481-1029"
        }
    ]
}

@app.route('/')
def index():
    return render_template(
        'index.html',
        current_kwh=round(meter_state["current_kwh"], 1),
        latest_token=meter_state["latest_token"],
        history=meter_state["history"]
    )

@app.route('/api/consume', methods=['POST'])
def consume():
    data = request.get_json() or {}
    amount = float(data.get('amount', 2.5))
    meter_state["current_kwh"] = max(0.0, meter_state["current_kwh"] - amount)
    return jsonify({
        "status": "success",
        "current_kwh": round(meter_state["current_kwh"], 1)
    })

@app.route('/api/recharge', methods=['POST'])
def recharge():
    data = request.get_json() or {}
    meter = data.get('meter', meter_state["meter_number"])
    amount = int(data.get('amount', 10000))
    operator = data.get('operator', 'M-Pesa')
    
    kwh_added = round(amount / meter_state["tariff_per_kwh"], 1)
    meter_state["current_kwh"] += kwh_added
    
    # Génération d'un token aléatoire de 16 chiffres
    token = f"{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
    meter_state["latest_token"] = token
    
    now_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    tx = {
        "date": now_str,
        "meter": meter,
        "amount": amount,
        "kwh": kwh_added,
        "operator": operator,
        "token": token
    }
    meter_state["history"].insert(0, tx)
    
    return jsonify({
        "status": "success",
        "current_kwh": round(meter_state["current_kwh"], 1),
        "token": token,
        "kwh_added": kwh_added,
        "date": now_str
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
