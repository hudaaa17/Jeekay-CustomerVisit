from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import io
from reportlab.platypus import Table, TableStyle

def generate_visit_pdf(filtered_df, customer_filter, area_filter, branch_filter):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            leftMargin=20*mm, rightMargin=20*mm,
                            topMargin=20*mm, bottomMargin=20*mm,
                             allowSplitting=1)

    # ── Styles ──
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("title", fontSize=18, fontName="Times-Bold",
                                  textColor=colors.HexColor("#1B2A4A"),
                                  spaceAfter=4, alignment=TA_CENTER)
    customer_style = ParagraphStyle("customer", fontSize=15, fontName="Times-Bold",
                                     textColor=colors.HexColor("#1B2A4A"), spaceAfter=3, alignment=TA_CENTER)
    label_style = ParagraphStyle("label", fontSize=11, fontName="Times-Bold",
                                  textColor=colors.HexColor("#88762D"),
                                  spaceAfter=1)
    value_style = ParagraphStyle("value", fontSize=11, fontName="Times-Roman",
                                  textColor=colors.HexColor("#1B2A4A"),
                                  spaceAfter=6)
    visit_style = ParagraphStyle("visit", fontSize=13, fontName="Times-Bold",
                                  textColor=colors.HexColor("#492170"), spaceAfter=4, alignment=TA_CENTER)

    story = []

    # ── Title ──
    title_text = f"Customer Visit Report"
    if customer_filter != "All":
        title_text += f" — {customer_filter}"
    elif area_filter != "All":
        title_text += f" — Area: {area_filter} "
    elif branch_filter != "All":
        title_text += f" — Branch: {branch_filter} "

    story.append(Paragraph(title_text, title_style))
    story.append(HRFlowable(width="100%", thickness=1.5,
                             color=colors.HexColor("#C9A84C"), spaceBefore=10, spaceAfter=12))

    # ── Group by customer ──
    cols_needed = ["Date", "Customer", "Customer Team",
                   "Oldest Bill Date", "Period (Days)", "Total Outstanding",
                   "Our Products offered / discussed", "Competitor products / prices", "Company Updates",
                   "Market / End Market Updates", "Other Remarks", "Follow up", "Follow up Date"]

    # Only use columns that actually exist in the df
    cols_needed = [c for c in cols_needed if c in filtered_df.columns]

    grouped = filtered_df.sort_values("Date", ascending=False).groupby("Customer", sort=False)

    for customer_name, group in grouped:
        story.append(Paragraph(customer_name, customer_style))
        story.append(HRFlowable(width="90%", thickness=0.5,
                                 color=colors.HexColor("#D9D0BE"), spaceBefore=5, spaceAfter=8))

        top4 = group.head(4)

        for i, (_, row) in enumerate(top4.iterrows(), 1):
            date_str = str(row["Date"])[:10] if "Date" in row else "–"

            def get_val(col):
                raw = row.get(col, None)
                try:
                    val = str(raw).strip() if raw is not None else "–"
                except Exception:
                    val = "–"
                if val in ("", "nan", "None", "NA", "<NA>", "NaN", "NaT"):
                    val = "–"
                return val

            # ── Visit header ──
            story.append(Spacer(1, 3*mm))
            story.append(Paragraph(f"Visit {i} — {date_str}", visit_style))
            story.append(Spacer(1, 2*mm))

            # ── Metadata table ──
            def cell(text, bold=False):
                font = "Times-Bold" if bold else "Times-Roman"
                return Paragraph(text, ParagraphStyle("cell", fontSize=10,
                                fontName=font, textColor=colors.HexColor("#1B2A4A"),
                                leading=14))

            # Format outstanding nicely
            outstanding_raw = get_val("Total Outstanding")
            try:
                outstanding = f"Rs. {float(outstanding_raw):,.0f}"
            except Exception:
                outstanding = outstanding_raw

            # Format oldest bill date (trim timestamp)
            oldest_bill = get_val("Oldest Bill Date")
            if len(oldest_bill) > 10 and "00:00:00" in oldest_bill:
                oldest_bill = oldest_bill[:10]

            table_data = [
            # Row 1 — Labels
            [
                cell("Area", bold=True),
                cell("Samira Team", bold=True),
                cell("Oldest Bill Date", bold=True),
                cell("Period (Days)", bold=True),
                cell("Total Outstanding", bold=True),
            ],
            # Row 2 — Values
            [
                cell(get_val("Area")),
                cell(get_val("Samira Team")),
                cell(oldest_bill),
                cell(get_val("Period (Days)").replace(".0", "")),
                cell(outstanding),
            ],
        ]

            meta_table = Table(table_data, colWidths=[30*mm, 28*mm, 34*mm, 28*mm, 40*mm])
            meta_table.setStyle(TableStyle([
                ("BOX",          (0, 0), (-1, -1), 0.8, colors.HexColor("#D9D0BE")),
                ("INNERGRID",    (0, 0), (-1, -1), 0.4, colors.HexColor("#EDE8DF")),
                # Label row background
                ("BACKGROUND",   (0, 0), (-1, 0), colors.HexColor("#F5F1EA")),
                # Value row background
                ("BACKGROUND",   (0, 1), (-1, 1), colors.HexColor("#FFFFFF")),
                ("TOPPADDING",   (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
                ("LEFTPADDING",  (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
                ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
            ]))

            story.append(meta_table)
            story.append(Spacer(1, 4*mm))

            # ── Text fields ──
            def add_field(label, col):
                val = get_val(col)
                if val == "–":
                    return  # Skip empty fields entirely — keeps it clean!
                story.append(Paragraph(label, label_style))
                story.append(Paragraph(val, value_style))

            add_field("CUSTOMER TEAM", "Customer Team")
            add_field("PRODUCTS OFFERED / DISCUSSED", "Our Products offered / discussed")
            add_field("COMPETITOR PRODUCTS / PRICES", "Competitor products / prices")
            add_field("COMPANY UPDATES", "Company Updates")
            add_field("MARKET / END MARKET UPDATES", "Market / End Market Updates")
            add_field("OTHER REMARKS", "Other Remarks")
            add_field("FOLLOW UP", "Follow up")
            add_field("FOLLOW UP DATE", "Follow up Date")

            if i < len(top4):
                story.append(Spacer(1, 4*mm))
                story.append(HRFlowable(width="50%", thickness=0.4,
                                        color=colors.HexColor("#D9D0BE"),
                                        spaceAfter=6))

        story.append(Spacer(1, 8*mm))
        story.append(HRFlowable(width="100%", thickness=2,
                                color=colors.HexColor("#1B2A4A"),
                                spaceAfter=10))
        story.append(Spacer(1, 4*mm))

    doc.build(story)
    buffer.seek(0)
    return buffer