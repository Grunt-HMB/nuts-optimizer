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
st.title("Research Lab Nuts Optimizer")

amount = st.number_input(
    "Amount",
    value=25.0,
    step=1.0,
    min_value=0.0
)

currency = st.radio(
    "Currency",
    ["EUR", "USD", "AUD", "NZD", "INR"]
)

margin = st.number_input(
    "Extra money for more options (same currency)",
    value=0.0,
    step=0.5,
    min_value=0.0
)

# =========================================================
# Calculation
# =========================================================
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
                    cost = a * prices[0] + b * prices[1] + c * prices[2]

                    # ✅ CORE FIX:
                    # always allow "best under budget" (margin=0 works)
                    if cost <= budget_inr + margin_inr:
                        u = a * units[0] + b * units[1] + c * units[2]

                        if best is None or u > best["units"]:
                            best = {
                                "A": a,
                                "B": b,
                                "C": c,
                                "cost": cost,
                                "units": u
                            }

        # =================================================
        # Output
        # =================================================
        if best:
            invest_currency = best["cost"] / rate
            remaining_currency = amount - invest_currency

            st.success("Best combination found")

            st.write(f"Exchange rate: 1 {currency} = {rate:.2f} INR")
            st.write(f"Budget: {budget_inr:.0f} INR")

            st.write("### 📦 Selected packages")
            st.write(f"6000 nuts (205 Rs): {best['A']}×")
            st.write(f"12800 nuts (409 Rs): {best['B']}×")
            st.write(f"34500 nuts (1020 Rs): {best['C']}×")

            st.write(f"**Total nuts:** {best['units']:,}")
            st.write(f"**Total price:** {best['cost']} Rs")

            st.write("### 💰 Investment")
            st.write(f"Invested amount: {invest_currency:.2f} {currency}")

            if remaining_currency >= 0:
                st.write(f"Remaining amount: {remaining_currency:.2f} {currency}")
            else:
                st.write(f"Overspend: {abs(remaining_currency):.2f} {currency}")

        else:
            st.warning("Budget too low for any package.")

    except Exception as e:
        st.error(str(e))
