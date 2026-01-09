import streamlit as st
import pandas as pd
import numpy as np
import os

# --- Configuration ---
DATA_FILE = "investment_ml_data.csv"

# Ensure the data file exists
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=[
        "P0","D","E","Tx","Si","t","M",
        "BankLoan","BankRate",
        "MaxInvestment","InvestorReturn",
        "OwnerReturn","RiskProbability"
    ]).to_csv(DATA_FILE, index=False)

# --- Functions (remain mostly unchanged) ---

def monte_carlo(P0, D, E, Tx, Si, t, sims=1000):
    """Performs Monte Carlo simulation for risk assessment."""
    success = 0
    for _ in range(sims):
        d = np.random.normal(D, D*0.3)
        e = np.random.normal(E, E*0.2)
        Rt = P0 * (1 + max(d, -0.9))**t
        NG = (Rt - P0 - e*t)*(1-Tx)
        if Si * NG > 0:
            success += 1
    return success / sims

def save_data(data_dict):
    """Appends successful investment data to the CSV file."""
    df = pd.read_csv(DATA_FILE)
    df.loc[len(df)] = data_dict.values()
    df.to_csv(DATA_FILE, index=False)

# --- Streamlit UI ---

st.title("Advanced Investment Intelligence System")

# Define default values for inputs
defaults = {
    "P0": 80000.0,  # Added .0 to make it a float
    "D": 4.0, 
    "E": 20000.0, 
    "Tx": 15.0, 
    "Si": 30.0,
    "t": 24,        # Kept as int for "Time (months)"
    "M": 1.4, 
    "Bank": 300000.0, 
    "BankRate": 12.0
}


# Use Streamlit columns for a better layout
col1, col2 = st.columns(2)

with col1:
    p0 = st.number_input("Primary Revenue (ETB)", min_value=0.0, value=defaults["P0"])
    d = st.number_input("Growth Rate (%)", value=defaults["D"]) / 100
    e = st.number_input("Expenses (ETB)", min_value=0.0, value=defaults["E"])
    tx = st.number_input("Tax Rate (%)", value=defaults["Tx"]) / 100
    si = st.number_input("Investor Share (%)", value=defaults["Si"]) / 100
    
with col2:
    t_ = st.number_input("Time (months)", min_value=1, value=defaults["t"])
    m = st.number_input("Expected Multiple", value=defaults["M"])
    bank = st.number_input("Bank Loan (ETB)", min_value=0.0, value=defaults["Bank"])
    bank_rate = st.number_input("Bank Interest (%)", value=defaults["BankRate"]) / 100

# The button will re-run the script flow when clicked
if st.button("Evaluate Investment"):
    try:
        # Perform calculations using the input variables
        Rt = p0 * (1 + d)**t_
        NG = (Rt - p0 - e*t_)*(1-tx)

        if NG <= 0:
            st.error("Business rejected: negative growth")
            st.stop()

        IR = si * NG
        Imax = IR / m
        OR = (1-si)*NG + p0*t_

        bank_payment = bank * bank_rate * t_
        if NG <= bank_payment:
            st.error("Bank loan too risky")
            st.stop()

        risk = monte_carlo(p0, d, e, tx, si, t_)

        if risk < 0.85:
            st.error(f"Risk too high: {risk*100:.1f}% success probability (needs >= 85%)")
            st.stop()

        # Display results on success
        st.success("Investment Approved!")
        st.metric("Investor Return", f"{IR:,.0f} ETB")
        st.metric("Max Safe Investment", f"{Imax:,.0f} ETB")
        st.metric("Owner Return", f"{OR:,.0f} ETB")
        st.metric("Risk Success Probability", f"{risk*100:.1f}%")

        # Save the data
        data_to_save = {
            "P0": p0, "D": d, "E": e, "Tx": tx, "Si": si, "t": t_, "M": m,
            "BankLoan": bank, "BankRate": bank_rate,
            "MaxInvestment": Imax, "InvestorReturn": IR,
            "OwnerReturn": OR, "RiskProbability": risk
        }
        save_data(data_to_save)

    except Exception as err:
        st.error(f"An unexpected error occurred: {err}")

# Optional: Display the accumulated data table at the bottom
st.subheader("Historical Investment Data")
if os.path.exists(DATA_FILE):
    df_history = pd.read_csv(DATA_FILE)
    st.dataframe(df_history)
