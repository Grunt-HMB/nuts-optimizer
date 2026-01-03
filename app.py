import requests
import streamlit as st

# =========================================================
# Live FX → INR
# =========================================================
def get_rate_to_inr(currency: str) -> float:
    currency = currency.upper()
    if currency == "INR":
        return 1.0

    try:
        r = requests.get(
            "https://api.frankfurter.app/latest",
            params={"from": currency, "to": "INR"},
            timeout=10
        )
        r.raise_for_status()
        data = r.json()
        return data["rates"]["INR"]
    except Exception:
        r = requests.get(
            f"https://open.er-api.com/v6/latest/{currency}",
            timeout=10
        )
        r.raise_for_status()
        data = r.json()
        return data["rates"]["INR"]

# =========================================================
# UI
# =========================================================
st.title("Nut Optimizer")

amount = st.number_input("Amount", value=25.0, step=1.0)
currency = st.radio("Currency", ["EUR", "USD", "AUD", "NZD", "INR"])
margin = st.number_input("Margin (same currency)", value=2.0, step=0.5)

if st.button("Calculate"):
    try:
        rate = get_rate_to_inr(currency)
        budget_inr = amount * rate
        margin_inr = margin * rate

        prices = [205, 409, 1020]     # INR
        units  = [6000, 12800, 34500]

        best = None
        max_c = int(budget_inr // prices[2])

        for c in range(max_c - 5, max_c + 6):
            if c < 0:
                continue
            for b in range(0, 20):
                for a in range(0, 20):
                    cost = a*prices[0] + b*prices[1] + c*prices[2]
                    if budget_inr - margin_inr <= cost <= budget_inr + margin_inr:
                        u = a*units[0] + b*units[1] + c*units[2]
                        if best is None or u > best["units"]:
                            best = {"A": a, "B": b, "C": c, "cost": cost, "units": u}

        if best:
            st.success("Best combination found")
            st.write(f"Exchange rate: 1 {currency} = {rate:.2f} INR")
            st.write(f"Budget: {budget_inr:.0f} INR ± {margin_inr:.0f}")
            st.write("### Result")
            st.write(f"6000 nuts (205 Rs): {best['A']}×")
            st.write(f"12800 nuts (409 Rs): {best['B']}×")
            st.write(f"34500 nuts (1020 Rs): {best['C']}×")
            st.write(f"**Total nuts:** {best['units']:,}")
            st.write(f"**Total price:** {best['cost']} Rs")
        else:
            st.warning("No valid combination found")

    except Exception as e:
        st.error(str(e))
