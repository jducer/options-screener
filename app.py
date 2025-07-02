@app.route("/options", methods=["GET"])
def get_options():
    ticker = request.args.get("ticker")
    try:
        stock = yf.Ticker(ticker)
        options_dates = stock.options
    except Exception as e:
        return jsonify({"error": "Rate limited or ticker invalid", "details": str(e)}), 500

    try:
        history = stock.history(period="1d")
        if history.empty or "Close" not in history:
            return jsonify({"error": "Could not retrieve stock price"}), 500
        current_price = history["Close"].iloc[-1]
    except:
        return jsonify({"error": "Failed to fetch historical price"}), 500

    results = []

    for exp in options_dates:
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
