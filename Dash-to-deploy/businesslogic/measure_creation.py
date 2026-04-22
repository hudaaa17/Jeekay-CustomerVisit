import pandas as pd
from data_handling.load_data import parse_mixed_dates


def calculate_measures(df):
    measures = {}

    df["Date"] = parse_mixed_dates(df["Date"])
    df["Follow up Date"] = parse_mixed_dates(df["Follow up Date"])
    df["Oldest Bill Date"] = parse_mixed_dates(df["Oldest Bill Date"])

    df["Total Outstanding"] = (
    df["Total Outstanding"]
    .astype(str)
    .str.replace("₹", "", regex=False)
    .str.replace(",", "", regex=False)
    .str.replace("-", "", regex=False)
    .str.strip()
)

    df["Total Outstanding"] = pd.to_numeric(df["Total Outstanding"], errors="coerce")

    # -----------------------------
    # 1. Total Visits
    # -----------------------------
    measures["Total Visits"] = len(df)

    # -----------------------------
    # 2. Latest Visit Date
    # -----------------------------
    latest_date = df["Date"].max()

    if pd.notna(latest_date):
        measures["Latest Visit Date"] = latest_date.strftime("%d-%b-%Y")
    else:
        measures["Latest Visit Date"] = "No data"

    # -----------------------------
    # 3. Days Since Last Visit
    # -----------------------------
    today = pd.Timestamp.today().normalize()

    if pd.notna(latest_date):
        measures["Days Since Last Visit"] = (today - latest_date.normalize()).days
    else:
        measures["Days Since Last Visit"] = "-"

    # -----------------------------
    # 4. Upcoming Follow-up Date
    # -----------------------------
    future_followups = df[
        (df["Follow up Date"].notna()) &
        (df["Follow up Date"] >= today)
    ]

    if not future_followups.empty:
        next_followup = future_followups["Follow up Date"].min()
    else:
        next_followup = pd.NaT

    # Store formatted value (IMPORTANT)
    if pd.notna(next_followup):
        measures["Upcoming Follow-up Date"] = next_followup.strftime("%d-%b-%Y")
        days_until = (next_followup - today).days
    else:
        measures["Upcoming Follow-up Date"] = "No upcoming follow-up"
        days_until = None

    # -----------------------------
    # 5. Days Until Follow-up
    # -----------------------------
    if days_until is not None:
        measures["Days Until Follow-up"] = days_until
    else:
        measures["Days Until Follow-up"] = "-"

    # -----------------------------
    # 6. Follow-up Status
    # -----------------------------
    if days_until is None:
        status = "No Follow-up"
    elif days_until < 0:
        status = "Overdue"
    elif days_until == 0:
        status = "Today"
    elif days_until <= 3:
        status = "Upcoming"
    else:
        status = "Scheduled"

    measures["Follow-up Status"] = status

    # -----------------------------
    # 7. Oldest Bill Date (Latest Visit)
    # -----------------------------
    latest_row = df[df["Date"] == latest_date]

    if not latest_row.empty:
        oldest_bill = latest_row["Oldest Bill Date"].max()
        measures["Oldest Bill Date (Customer)"] = (
            oldest_bill.strftime("%d-%b-%Y") if pd.notna(oldest_bill) else "-"
        )
    else:
        measures["Oldest Bill Date (Customer)"] = "-"

    # -----------------------------
    # 8. TEXT FIELDS (Latest Entry)
    # -----------------------------
    def get_latest_text(col):
        if col in df.columns and not latest_row.empty:
            val = latest_row[col].dropna()
            return val.iloc[0] if not val.empty else "-"
        return "-"

    measures["Latest Company Updates"] = get_latest_text("Company Updates")
    measures["Latest Competitor Info"] = get_latest_text("Competitor products / prices")
    measures["Latest Market Updates"] = get_latest_text("Market / End Market Updates")
    measures["Latest Remarks"] = get_latest_text("Other Remarks")
    measures["Latest Follow-up Details"] = get_latest_text("Follow up")
    measures["Outstanding Days"] = get_latest_text("Period (Days)")
    latest_df = (
    df.sort_values("Date")
      .groupby("Customer", as_index=False)
      .last())

    total_outstanding = latest_df["Total Outstanding"].sum()
    measures["Total Outstanding"] = total_outstanding

    # -----------------------------
    # 9. Customer Summary
    # -----------------------------
    measures["Customer Summary"] = f"""
    Competitor: {measures['Latest Competitor Info']}

    Company: {measures['Latest Company Updates']}

    Market: {measures['Latest Market Updates']}

    Remarks: {measures['Latest Remarks']}

    Follow-up: {measures['Latest Follow-up Details']}
    """

    return measures