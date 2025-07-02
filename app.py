from flask import Flask, request, jsonify
import yfinance as yf

app = Flask(__name__)

@app.route("/options", methods=["GET"])
def get_options():
    ticker = request.args.get("ticker")
    try:
        stock = yf.Ticker(ticker)
        expirations = stock.options
        data = {}
        for exp in expirations[:1]:  # limit to first expiry to reduce rate limit hit
            opt_chain = stock.option_chain(exp)
            data[exp] = {
                "calls": [call._asdict() for call in opt_chain.calls.itertuples()],
                "puts": [put._asdict() for put in opt_chain.puts.itertuples()]
            }
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
