import pandas as pd
import streamlit as st 
from data_handling.sheet_utils import load_data_from_gsheet


from io import BytesIO


def to_excel(df):
    output = BytesIO()
    # Use context manager to ensure the writer closes properly
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Visit History')
        
        workbook  = writer.book
        worksheet = writer.sheets['Visit History']

        # 1. Define a uniform format for the whole sheet
        # Added 'valign': 'top' so text starts at the top of the cell
        uniform_format = workbook.add_format({
            'text_wrap': True,
            'valign': 'top',
            'border': 1  # Optional: adds subtle borders for better "grid" feel
        })

        # 2. Set a standard width for ALL columns
        standard_width = 20 
        
        # Apply the width and the wrap format to every column in the dataframe
        # .set_column(first_col, last_col, width, cell_format)
        num_cols = len(df.columns)
        worksheet.set_column(0, num_cols - 1, standard_width, uniform_format)

    return output.getvalue()

def parse_mixed_dates(date_series):
    """
    Handles mixed date formats:
    - 20 February 2026  (day month_name year)
    - 20-02-2026        (dd-mm-yyyy)
    - 2026-02-10        (yyyy-mm-dd)
    - 10/02/2026        (dd/mm/yyyy)
    - 20 Feb 2026       (abbreviated month name)
    """
    s = (
        date_series
        .astype(str)
        .str.strip()
        .str.replace("\xa0", " ", regex=False)   # non-breaking space
        .str.replace("\u2013", "-", regex=False)  # en-dash
        .str.replace("\u2014", "-", regex=False)  # em-dash
        .str.replace(r"\s+", " ", regex=True)     # collapse multiple spaces
    )

    result = pd.Series(pd.NaT, index=s.index, dtype="datetime64[ns]")

    # Format 1: 2026-02-10  (ISO)
    mask1 = s.str.match(r"^\d{4}-\d{2}-\d{2}$", na=False)
    result[mask1] = pd.to_datetime(s[mask1], format="%Y-%m-%d", errors="coerce")

    # Format 2: 10-02-2026  (dd-mm-yyyy)
    mask2 = s.str.match(r"^\d{2}-\d{2}-\d{4}$", na=False)
    result[mask2] = pd.to_datetime(s[mask2], format="%d-%m-%Y", errors="coerce")

    # Format 3: 10/02/2026  (dd/mm/yyyy)
    mask3 = s.str.match(r"^\d{2}/\d{2}/\d{4}$", na=False)
    result[mask3] = pd.to_datetime(s[mask3], format="%d/%m/%Y", errors="coerce")

    # Format 4: 20 February 2026  (full month name)
    mask4 = s.str.match(r"^\d{1,2}\s+[A-Za-z]+\s+\d{4}$", na=False)
    result[mask4] = pd.to_datetime(s[mask4], format="%d %B %Y", errors="coerce")

    # Format 5: 20 Feb 2026  (abbreviated month) — fallback for mask4 failures
    still_nat = result.isna() & mask4
    result[still_nat] = pd.to_datetime(s[still_nat], format="%d %b %Y", errors="coerce")

    # Catch-all: let pandas infer anything still NaT
    remaining = result.isna() & s.str.strip().ne("") & s.str.strip().ne("nan") & s.str.strip().ne("NaT")
    if remaining.any():
        result[remaining] = pd.to_datetime(s[remaining], dayfirst=True, errors="coerce")

    # Debug: show unparsed rows
    failed = result.isna() & s.str.strip().ne("nan") & s.str.strip().ne("NaT") & s.str.strip().ne("")
    if failed.any():
        print(f"⚠️  {failed.sum()} dates could not be parsed:")
        print(s[failed].value_counts().to_string())

    return result


def format_inr(num):
    if pd.isna(num):
        return "₹ 0"
    
    num = int(round(num))
    s = str(num)
    
    # Last 3 digits
    last3 = s[-3:]
    rest = s[:-3]
    
    if rest != "":
        rest = rest[::-1]
        parts = [rest[i:i+2] for i in range(0, len(rest), 2)]
        rest = ",".join(parts)[::-1]
        return f"₹ {rest},{last3}"
    else:
        return f"₹ {last3}"

@st.cache_data(ttl=300)
def load_and_preprocess_data():

    # 1. Load data
    df = load_data_from_gsheet("17kHih7frWstv6Ff1jl6kgHYxUpKuz0I_UJueLaPEkwo", "Sheet1")

    # 2. Clean column names
    df.columns = df.columns.str.strip()

    # 3. Replace "-" with NaN globally
    df = df.replace("-", pd.NA)

    # 4. Define column groups
    date_cols = [
        "Date",
        "Oldest Bill Date",
        "Follow up Date"
    ]

    numeric_cols = [
        "Period (Days)"
    ]

    text_cols = [
        "Branch",
        "Area",
        "Samira Team",
        "Customer",
        "Industry",
        "Customer Team",
        "Our Products offered / discussed",
        "Competitor products / prices",
        "Company Updates",
        "Market / End Market Updates",
        "Other Remarks",
        "Follow up"
    ]

    df["Total Outstanding"] = (
    df["Total Outstanding"]
    .astype(str)
    .str.replace("₹", "", regex=False)
    .str.replace(",", "", regex=False)
    .str.replace("-", "", regex=False)
    .str.strip()
)

    df["Total Outstanding"] = pd.to_numeric(df["Total Outstanding"], errors="coerce")

    # 5. Convert DATE columns ✅ now handles mixed formats
    for col in date_cols:
        if col in df.columns:
            df[col] = parse_mixed_dates(df[col])

    # 6. Convert NUMERIC columns
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # 7. Convert TEXT columns
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype("string")

    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

    return df