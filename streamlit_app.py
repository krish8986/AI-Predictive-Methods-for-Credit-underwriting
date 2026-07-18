import os
import re
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, Optional

import requests
import streamlit as st
from fpdf import FPDF


API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
FONT_PATH = Path(__file__).resolve().parent / "FreeSerif.ttf"


st.set_page_config(
    page_title="Credit Underwriting Dashboard",
    page_icon="C",
    layout="wide",
    initial_sidebar_state="expanded",
)


def get_api_health() -> bool:
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        return response.ok and response.json().get("model_loaded", False)
    except requests.RequestException:
        return False


def request_prediction(payload: Dict[str, Any]) -> Dict[str, Any]:
    response = requests.post(f"{API_BASE_URL}/predict", json=payload, timeout=15)
    response.raise_for_status()
    result = response.json()
    required_fields = {
        "prediction",
        "approval_probability",
        "rejection_probability",
    }
    if not required_fields.issubset(result):
        raise ValueError("The prediction service returned an incomplete response.")
    return result


def create_pdf_report(
    applicant: Dict[str, Any], payload: Dict[str, Any], result: Dict[str, Any]
) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=14)
    pdf.add_page()

    font_name = "Helvetica"
    if FONT_PATH.exists():
        pdf.add_font("FreeSerif", "", str(FONT_PATH), uni=True)
        font_name = "FreeSerif"

    pdf.set_font(font_name, size=16)
    pdf.cell(0, 10, txt="Credit Underwriting Decision Report", ln=True, align="C")
    pdf.ln(4)

    pdf.set_font(font_name, size=12)
    pdf.cell(0, 8, txt="Applicant Information", ln=True)
    pdf.set_font(font_name, size=10)
    pdf.cell(0, 6, txt=f"Name: {applicant['full_name']}", ln=True)
    pdf.cell(0, 6, txt=f"Email: {applicant['email']}", ln=True)
    pdf.cell(0, 6, txt=f"Phone: {applicant['phone']}", ln=True)
    pdf.ln(4)

    pdf.set_font(font_name, size=12)
    pdf.cell(0, 8, txt="Decision", ln=True)
    pdf.set_font(font_name, size=10)
    pdf.cell(0, 6, txt=f"Prediction: {result['prediction']}", ln=True)
    pdf.cell(
        0,
        6,
        txt=f"Approval probability: {result['approval_probability']:.2%}",
        ln=True,
    )
    pdf.cell(
        0,
        6,
        txt=f"Rejection probability: {result['rejection_probability']:.2%}",
        ln=True,
    )
    pdf.ln(4)

    pdf.set_font(font_name, size=12)
    pdf.cell(0, 8, txt="Application Snapshot", ln=True)
    pdf.set_font(font_name, size=10)
    for label, value in payload.items():
        pdf.cell(0, 6, txt=f"{label.replace('_', ' ').title()}: {value}", ln=True)

    buffer = BytesIO()
    pdf.output(buffer)
    return buffer.getvalue()


def clamp_percentage(value: float) -> int:
    return max(0, min(100, round(value * 100)))


st.markdown(
    """
    <style>
        .stApp { background: #f5f7f7; }
        .block-container { max-width: 1280px; padding-top: 2rem; padding-bottom: 3rem; }
        .dashboard-header {
            border-left: 6px solid #147d64;
            padding: 0.4rem 0 1rem 1.25rem;
            margin-bottom: 1.25rem;
        }
        .dashboard-header h1 {
            color: #173b3f;
            font-size: 2.25rem;
            margin: 0;
            letter-spacing: 0;
        }
        .dashboard-header p { color: #52656a; margin: 0.35rem 0 0; font-size: 1rem; }
        .badge {
            display: inline-block;
            background: #d9f3ea;
            color: #0f5e4c;
            border: 1px solid #9dd8c3;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 700;
            padding: 0.25rem 0.55rem;
            margin-top: 0.65rem;
        }
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: #ffffff;
            border-color: #d8e2e1;
            border-radius: 8px;
        }
        div[data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #d8e2e1;
            border-radius: 8px;
            padding: 0.7rem 0.85rem;
        }
        .section-title { color: #173b3f; font-weight: 700; font-size: 1.05rem; }
        .section-note { color: #64777a; font-size: 0.85rem; margin-bottom: 0.6rem; }
        .result-heading { color: #173b3f; font-size: 1.2rem; font-weight: 700; }
        div[data-testid="stSidebar"] { background: #173b3f; }
        div[data-testid="stSidebar"] * { color: #edf6f4; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <section class="dashboard-header">
        <h1>Credit Underwriting Dashboard</h1>
        <p>Structured loan assessment powered by a production machine learning service.</p>
        <span class="badge">Production ML + FastAPI</span>
    </section>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("### Service Status")
    if get_api_health():
        st.success("Prediction service online")
    else:
        st.error("Prediction service unavailable")
    st.caption(API_BASE_URL)

if "prediction_result" not in st.session_state:
    st.session_state.prediction_result = None
if "submitted_payload" not in st.session_state:
    st.session_state.submitted_payload = None
if "applicant_details" not in st.session_state:
    st.session_state.applicant_details = None

with st.form("underwriting_application", clear_on_submit=False):
    top_left, top_right = st.columns(2, gap="large")

    with top_left:
        with st.container(border=True):
            st.markdown('<div class="section-title">Applicant Information</div>', unsafe_allow_html=True)
            st.markdown('<div class="section-note">Identity and personal profile</div>', unsafe_allow_html=True)
            full_name = st.text_input("Full name", placeholder="Applicant name")
            email = st.text_input("Email address", placeholder="name@example.com")
            phone = st.text_input("Phone number", placeholder="10-digit mobile number")
            applicant_age = st.number_input("Applicant age", min_value=18, max_value=100, value=30, step=1)
            gender = st.selectbox("Gender", ["Men", "Women"])
            marital_status = st.selectbox("Marital status", ["Single", "Married"])

    with top_right:
        with st.container(border=True):
            st.markdown('<div class="section-title">Employment Details</div>', unsafe_allow_html=True)
            st.markdown('<div class="section-note">Employment and residence profile</div>', unsafe_allow_html=True)
            employee_status = st.selectbox(
                "Employment status",
                ["employed", "self employed", "unemployed", "student"],
            )
            residence_type = st.selectbox("Residence type", ["MORTGAGE", "OWN", "RENT"])
            active_loans = st.number_input(
                "Number of active loans", min_value=0, max_value=50, value=1, step=1
            )

    middle_left, middle_right = st.columns(2, gap="large")

    with middle_left:
        with st.container(border=True):
            st.markdown('<div class="section-title">Loan Details</div>', unsafe_allow_html=True)
            st.markdown('<div class="section-note">Requested facility and credit profile</div>', unsafe_allow_html=True)
            loan_purpose = st.selectbox(
                "Loan purpose",
                ["Vehicle", "Personal", "Home Renovation", "Education", "Medical", "Other"],
            )
            loan_amount = st.number_input("Loan amount (INR)", min_value=1, value=2_000_000, step=10_000)
            loan_term = st.number_input("Loan term (months)", min_value=1, max_value=480, value=24, step=1)
            loan_interest = st.number_input(
                "Loan interest rate (%)", min_value=0.01, max_value=100.0, value=7.5, step=0.1
            )
            loan_percent_income = st.number_input(
                "Loan as percentage of income", min_value=0, max_value=100, value=20, step=1
            )

    with middle_right:
        with st.container(border=True):
            st.markdown('<div class="section-title">Financial Information</div>', unsafe_allow_html=True)
            st.markdown('<div class="section-note">Annual income and credit standing</div>', unsafe_allow_html=True)
            income_annum = st.number_input(
                "Annual income (INR)", min_value=1, value=5_000_000, step=100_000
            )
            cibil_score = st.number_input(
                "CIBIL score", min_value=300, max_value=900, value=750, step=1
            )

    with st.container(border=True):
        st.markdown('<div class="section-title">Asset Information</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-note">Declared asset values in INR</div>', unsafe_allow_html=True)
        asset_one, asset_two, asset_three, asset_four = st.columns(4, gap="medium")
        with asset_one:
            residential_assets_value = st.number_input(
                "Residential assets", min_value=0, value=2_400_000, step=100_000
            )
        with asset_two:
            commercial_assets_value = st.number_input(
                "Commercial assets", min_value=0, value=1_000_000, step=100_000
            )
        with asset_three:
            luxury_assets_value = st.number_input(
                "Luxury assets", min_value=0, value=1_000_000, step=100_000
            )
        with asset_four:
            bank_asset_value = st.number_input(
                "Bank assets", min_value=0, value=1_000_000, step=100_000
            )

    submitted = st.form_submit_button("Assess application", type="primary", use_container_width=True)

if submitted:
    validation_errors = []
    if not full_name.strip() or not re.fullmatch(r"[A-Za-z ]+", full_name.strip()):
        validation_errors.append("Enter a valid full name using letters and spaces only.")
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email.strip()):
        validation_errors.append("Enter a valid email address.")
    if not re.fullmatch(r"\d{10}", phone.strip()):
        validation_errors.append("Enter a valid 10-digit phone number.")

    if validation_errors:
        for error in validation_errors:
            st.error(error)
    else:
        payload = {
            "applicant_age": applicant_age,
            "gender": gender,
            "marital_status": marital_status,
            "employee_status": employee_status,
            "residence_type": residence_type,
            "loan_purpose": loan_purpose,
            "income_annum": income_annum,
            "loan_amount": loan_amount,
            "loan_term": loan_term,
            "cibil_score": cibil_score,
            "residential_assets_value": residential_assets_value,
            "commercial_assets_value": commercial_assets_value,
            "luxury_assets_value": luxury_assets_value,
            "bank_asset_value": bank_asset_value,
            "loan_interest": loan_interest,
            "loan_percent_income": loan_percent_income,
            "active_loans": active_loans,
        }
        applicant = {"full_name": full_name.strip(), "email": email.strip(), "phone": phone.strip()}

        try:
            with st.spinner("Submitting application to the underwriting service..."):
                result = request_prediction(payload)
            st.session_state.prediction_result = result
            st.session_state.submitted_payload = payload
            st.session_state.applicant_details = applicant
        except requests.HTTPError as error:
            detail = "The prediction service rejected the request."
            try:
                detail = error.response.json().get("detail", detail)
            except ValueError:
                pass
            st.error(detail)
        except (requests.RequestException, ValueError) as error:
            st.error(f"Unable to retrieve a prediction: {error}")

result: Optional[Dict[str, Any]] = st.session_state.prediction_result
if result:
    with st.container(border=True):
        st.markdown('<div class="result-heading">Underwriting Result</div>', unsafe_allow_html=True)
        if result["prediction"] == "Approved":
            st.success("Approved")
        else:
            st.warning("Rejected")

        approval_probability = float(result["approval_probability"])
        rejection_probability = float(result["rejection_probability"])
        metric_one, metric_two = st.columns(2, gap="large")
        with metric_one:
            st.metric("Approval probability", f"{approval_probability:.1%}")
            st.progress(clamp_percentage(approval_probability))
        with metric_two:
            st.metric("Rejection probability", f"{rejection_probability:.1%}")
            st.progress(clamp_percentage(rejection_probability))

        report = create_pdf_report(
            st.session_state.applicant_details,
            st.session_state.submitted_payload,
            result,
        )
        st.download_button(
            "Download decision report (PDF)",
            data=report,
            file_name="credit_underwriting_report.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
