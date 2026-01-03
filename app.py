import requests
import streamlit as st

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Research Lab Nuts Optimizer",
    layout="wide"
)

# =========================================================
# LAYOUT CSS (compact desktop)
# =========================================================
st.markdown(
    """
    <style>
    .block-container {
        max-width: 950px;
        margin: auto;
    }

    .logo {
        margin-top: 10px;
    }

    @media (max-width: 768px) {
        .block-container {
            max-width: 100%;
            padding: 1rem;
        }
        .logo {
            margin-top: 0;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# FX helpers (cached)
# =========================================================
@st.cache_data(ttl=300)
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
        return r.json()["rates"]["INR"]
    except Exception:
        r = requests.get(
            f"https://open.er-api.com/v6/latest/{currency}",
            timeout=10
        )
        r.raise_for_status()
        return r.json()["rates"]["INR"]

# =========================================================
# TITLE + IMAGE (¼ WIDTH)
# =========================================================
col_title, col_img = st.columns([3, 1])

with col_title:
    st.title("Research Lab Nuts Optimizer")

with col_img:
    st.image(
        "hcr2.png",
        use_column_width=True
    )

# =========================================================
# INPUTS
# =========================================================
col_amount, col_currency = st.columns([2, 3])

with col_amount:
    amount = st.number_input(
        "Amount",
        value=25.0,
        step=1.0,
        min_value=0.0
    )

with col_currency:
    currency = st.radio(
        "Currency",
        ["EUR", "USD", "AUD", "NZD", "INR"],
        horizontal=True,
        label_visibility="collapsed"
    )

margin = st.number_input(
    "Extra money for more options (same currency)",
    value=0.0,
    step=0.5,
    min_value=0.0
)

# =========================================================
# AUTO CALC
# =========================================================
if amount > 0:
    rate = get_rate_to_inr(currency)
    budget_inr = amount * rate
    margin_inr = margin * rate

    prices = [205, 409, 1020]
    units  = [6000, 12800, 34500]

    best = None
    max_c = int(budget_inr // prices[2])

    for c in range(max_c - 5, max_c + 6):
        if c < 0:
            continue
        for b in range(0, 20):
            for a in range(0, 20):
                cost = a*prices[0] + b*prices[1] + c*prices[2]
                if cost <= budget_inr + margin_inr:
                    u = a*units[0] + b*units[1] + c*units[2]
                    if best is None or u > best["units"]:
                        best = {
                            "A": a,
                            "B": b,
                            "C": c,
                            "cost": cost,
                            "units": u
                        }

    if best:
        invest_currency = best["cost"] / rate
        remaining_currency = amount - invest_currency

        st.success("Best combination found")

        col_l, col_r = st.columns(2)
        with col_l:
            st.caption(f"Exchange rate ({currency} → INR)")
            st.write(f"{rate:.2f}")
        with col_r:
            st.caption("Budget (INR)")
            st.write(f"{budget_inr:.0f}")

        # =================================================
        # PACKAGES + LOGO
        # =================================================
        col_text, col_logo = st.columns([4, 2])

        with col_text:
            st.write("### 📦 Packages")
            st.write(f"6000 nuts (205 INR): {best['A']}×")
            st.write(f"12800 nuts (409 INR): {best['B']}×")
            st.write(f"34500 nuts (1020 INR): {best['C']}×")

            col_nuts, col_price = st.columns(2)
            with col_nuts:
                st.write(f"**Total nuts:** {best['units']:,}")
            with col_price:
                st.write(f"**Total price:** {best['cost']} INR")

            st.write("### 💰 Investment")

            col_inv, col_rem = st.columns(2)
            with col_inv:
                st.write(f"Invested amount: {invest_currency:.2f} {currency}")
            with col_rem:
                st.write(f"Remaining amount: {remaining_currency:.2f} {currency}")

        with col_logo:
            st.markdown("<div class='logo'>", unsafe_allow_html=True)
            st.image("hmb.webp", width=260)
            st.markdown("</div>", unsafe_allow_html=True)
