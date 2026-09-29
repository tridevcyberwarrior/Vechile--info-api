from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

def get_acko_data(vnum, product_type):
    url = "https://www.acko.com/motororchestrator/api/v2/proposals"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Mobile Safari/537.36',
        'Content-Type': 'application/json',
        'origin': 'https://www.acko.com',
        'referer': f'https://www.acko.com/gi/lp/{product_type}-insurance/new/'
    }
    
    payload = {
        "registration_number": vnum.upper(),
        "mobile_no": "9991577415", # Default mobile
        "origin": "acko_bike" if product_type == "bike" else "acko",
        "product": product_type,
        "is_new": False
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None

@app.route('/acko', methods=['GET'])
def acko_api():
    vnum = request.args.get('vnum')
    
    if not vnum:
        return jsonify({"error": "Please provide vnum parameter"}), 400

    # Auto-detection logic: Aksar registration numbers me patterns hote hain, 
    # par yahan hum simple try-catch ya sequential check laga sakte hain.
    # Pehle Bike try karte hain, agar result nahi mila toh Car.
    
    data = get_acko_data(vnum, "bike")
    
    # Agar bike me data nahi mila ya product detect galat hua
    if not data or not data.get('vehicle', {}).get('make_name'):
        data = get_acko_data(vnum, "car")

    if data:
        vehicle = data.get('vehicle', {})
        user = data.get('user', {})
        
        # Simplified Response
        result = {
            "status": "success",
            "product": data.get('product'),
            "owner_name": user.get('name') or vehicle.get('owner_name') or "Not Found",
            "vehicle_name": vehicle.get('car_name'),
            "make": vehicle.get('make_name'),
            "model": vehicle.get('model_name'),
            "variant": vehicle.get('variant_name'),
            "engine_number": vehicle.get('engine_number_unmasked'),
            "chassis_number": vehicle.get('chassis_number_unmasked'),
            "registration_date": vehicle.get('registration_date'),
            "fuel_type": vehicle.get('fuel_type'),
            "cc": vehicle.get('cc'),
            "mfg_date": vehicle.get('manufacturing_date'),
            "previous_insurer": vehicle.get('previous_policy', {}).get('insurer_name')
        }
        return jsonify(result)
    else:
        return jsonify({"status": "failed", "message": "Data not found or API blocked"}), 404

# Vercel requires this
def handler(event, context):
    return app(event, context)

if __name__ == '__main__':
    app.run(debug=True)
