import os
from flask import Flask, render_template, jsonify, request
from app.methods import get_or_set_by_ticker, update_tickers, get_trends


app = Flask(__name__, static_folder="app/static", template_folder="app/templates")


@app.route("/")
def index():
    trends = get_trends()
    return render_template("index.html", trends=trends)


@app.route("/fetch", methods=["POST"])
def data():
    ticker = str(request.headers.get("ticker"))
    days = int(request.headers.get("days"))
    data = get_or_set_by_ticker(ticker=ticker, template="invest", days=days)
    return jsonify(data)


@app.route("/update", methods=["GET"])
def update_tickers_db():
    update_tickers()
    return jsonify({"response": "ok"})



if __name__ == "__main__":
    app.run(
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 5000)),
        debug=bool(os.getenv("DEBUG", True)),
    )
