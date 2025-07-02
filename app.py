from flask import Flask, request, jsonify
import yfinance as yf

app = Flask(__name__)

@app.route("/options", methods=["GET"])
def get_options():
    ticker = request.args.get("ticker")
    stock = yf.Ticker(ticker)
    current_price = stock.history(period="1d")["Close"].iloc[-1]
    results = []

    for exp in stock.options:
        try:
            calls = stock.option_chain(exp).calls
            for _, row in calls.iterrows():
                if not (row["bid"] and row["ask"] and row["openInterest"] and row["volume"]): continue
                mid = (row["bid"] + row["ask"]) / 2
                otm = ((row["strike"] - current_price) / current_price) * 100

                if 10 <= otm <= 20 and mid <= 0.70 and row["openInterest"] >= 500 and row["volume"] >= 100:
                    results.append({
                        "expiration": exp,
                        "strike": row["strike"],
                        "mid_price": round(mid, 2),
                        "bid": row["bid"],
                        "ask": row["ask"],
                        "volume": row["volume"],
                        "open_interest": row["openInterest"],
                        "otm_pct": round(otm, 2)
                    })
        except:
            continue

    return jsonify(sorted(results, key=lambda x: (-x["volume"], -x["open_interest"]))[:10])

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
