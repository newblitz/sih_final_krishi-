# api.py
from flask import Flask, jsonify, request
from data_fetcher import get_data

app = Flask(__name__)

@app.route("/prices", methods=["GET"])
def prices():
    """
    Query params:
      crop - optional crop name (string)
      market - optional market name (string)
    """
    df = get_data()
    crop = request.args.get("crop")
    market = request.args.get("market")
    res = df.copy()
    if crop:
        res = res[res["crop"].str.lower() == crop.lower()]
    if market:
        res = res[res["market"].str.lower() == market.lower()]
    # to json
    return jsonify(res.to_dict(orient="records"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
