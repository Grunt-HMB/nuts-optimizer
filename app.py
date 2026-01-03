import requests
import streamlit as st

# =========================================================
# Live FX → INR (robuust, met fallback)
# =========================================================
def get_rate_to_inr(currency: str) -> float:
    currency = currency.upper()

    if currency == "INR":
        return 1.0

    # Primary: Frankfurter (ECB)
    try:
        r = requests.get(
            "https://api.frankfurter.app/latest",
            params={"from": currency, "to": "INR"},
            timeout=10
        )
        r.raise_for_status()
        data = r.json()
        if "rates" in data and "INR" in data["rates"]:
            return data["rates"]["INR"]
    except Exception:
        pass

    # Fallback: open.er-api.com
    r = requests.get(
        f"https://open.er-api.com/v6/latest/{currency}",
        timeout=10
    )
    r.raise_for_status()
    data = r.json()
    if data.get("result") == "success" and "INR" in data["rates"]:
        return data["rates"]["INR"]

    raise RuntimeError("Live exchange rate could not be retrieved")

# =========================================================
# UI
# =========================================================
st.set_page_config(page_title="Research Labs Nuts Optimizer", layout="centered")

st.title("Nut Optimizer")

amount = st.number_input(
    "Amount to deposit",
    value=25.0,
    step=1.0,
    min_value=0.0
)

currency = st.radio(
    "Currency",
    ["EUR", "USD", "AUD", "NZD", "INR"],
    horizontal=True
)

margin = st.number_input(
    "Extra money for more options (same currency)",
    value=0,
    step=0.5,
    min_value=0.0
)

# =========================================================
# Calculation
# =========================================================
if st.button("Calculate"):
    try:
        # FX conversion
        rate = get_rate_to_inr(currency)
        budget_inr = amount * rate
        margin_inr = margin * rate

        # Packages (INR)
        prices = [205, 409, 1020]       # Rs
        units  = [6000, 12800, 34500]

        best = None
        max_c = int(budget_inr // prices[2])

        # Optimization
        for c in range(max_c - 5, max_c + 6):
            if c < 0:
                continue
            for b in range(0, 20):
                for a in range(0, 20):
                    total_cost = a*prices[0] + b*prices[1] + c*prices[2]

                    if budget_inr - margin_inr <= total_cost <= budget_inr + margin_inr:
                        total_units = a*units[0] + b*units[1] + c*units[2]

                        if best is None or total_units > best["units"]:
                            best = {
                                "A": a,
                                "B": b,
                                "C": c,
                                "cost": total_cost,
                                "units": total_units
                            }

        # =================================================
        # Output
        # =================================================
        if best:
            cost_in_currency = best["cost"] / rate
            unused_amount = max(0.0, amount - cost_in_currency)

            st.success("Best combination found")

            st.markdown(f"""
### 💰 Deposit & Spend Summary

**A. Amount to deposit (input):**  
{amount:.2f} **{currency}**

**B. Effective amount used:**  
{best['cost']} INR  
≈ **{cost_in_currency:.2f} {currency}**

**Unused / remaining amount:**  
≈ **{unused_amount:.2f} {currency}**

---

### 📦 Selected Packages
- 6000 nuts (205 Rs): **{best['A']}×**
- 12800 nuts (409 Rs): **{best['B']}×**
- 34500 nuts (1020 Rs): **{best['C']}×**

**Total nuts:** {best['units']:,}
""")
        else:
            st.warning("No valid combination found within this budget.")

    except Exception as e:
        st.error(f"Error: {e}")
