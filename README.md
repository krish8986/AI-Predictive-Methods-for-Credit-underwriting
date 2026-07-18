<p align="center">
  <img src="docs/images/banner.png" alt="AI Credit Underwriting Platform Banner" width="100%">
</p>

<h1 align="center">🚀 AI Credit Underwriting Platform</h1>

<p align="center">
Production Machine Learning • FastAPI • Streamlit • REST API
</p>                                                  # 🚀 Credit Underwriting Dashboard

### Production-Ready AI Credit Risk Assessment Platform

A production-style Machine Learning application that predicts whether a loan application should be **Approved** or **Rejected** using a trained **Gradient Boosting Model** deployed behind a **FastAPI REST API** and consumed by a modern **Streamlit Dashboard**.

Unlike traditional academic ML projects, this project follows a **production-inspired architecture** where the frontend, backend, and ML pipeline are cleanly separated.

---

## ✨ Key Highlights

- 🧠 Production Machine Learning Pipeline
- ⚡ FastAPI REST Backend
- 🎨 Modern Streamlit Dashboard
- 📊 Loan Approval Probability
- 📄 Explainable PDF Report
- 🧠 SHAP Explainability
- 📊 Feature Importance Visualization
- ✅ Top Positive Decision Factors
- ⚠️ Top Negative Risk Factors
- ✅ Input Validation
- 🔍 Health Monitoring
- 🔄 End-to-End API Communication
- 🏗 Production-Oriented Architecture

---

# 🏛 System Architecture

```mermaid
flowchart TD

    U([👤 User])

    S["🖥️ Streamlit Dashboard
    • Applicant Information
    • Employment Details
    • Loan Details
    • Financial Information
    • Asset Information
    • PDF Report Generation"]

    F["⚡ FastAPI Backend
    • GET /health
    • POST /predict
    • Request Validation
    • JSON Response"]

    P["🧠 Production ML Pipeline
    • ColumnTransformer
    • OneHotEncoder
    • GradientBoostingClassifier"]

    R["📊 Prediction Engine
    • Approved / Rejected
    • Approval Probability
    • Rejection Probability"]

    O["📄 Dashboard Output
    • Decision Card
    • Progress Bars
    • Download PDF"]

    U --> S
    S -->|"HTTP POST /predict"| F
    F --> P
    P --> R
    R --> S
    S --> O
```

---

# 🌟 Features

## 🎯 Intelligent Credit Assessment

Predicts whether a loan application should be approved using a trained Machine Learning model.

---

## ⚡ FastAPI Backend

The prediction engine is exposed as a REST API.

Endpoints:

- `/health`
- `/predict`

This architecture allows multiple clients to consume the prediction service.

---

## 🎨 Modern Dashboard

The Streamlit application provides a clean dashboard with:

- Applicant Information
- Employment Details
- Loan Details
- Financial Information
- Asset Information

---

## 📈 Prediction Analytics

The dashboard displays

- Approval Probability
- Rejection Probability
- Decision Status
- Progress Indicators

---

## 📄 PDF Report

Generate a downloadable underwriting report containing:

- Applicant details
- Prediction
- Probabilities
- Submitted application

---

## 🧩 Production ML Pipeline

The project uses a serialized sklearn Pipeline containing

- ColumnTransformer
- OneHotEncoder
- GradientBoostingClassifier

This guarantees that training and inference use identical preprocessing.

---

## 🛡 Input Validation

The dashboard validates

- Email
- Phone Number
- Required Fields

before sending requests to the API.

---

## ❤️ Service Health Monitoring

The dashboard continuously checks the FastAPI server using the `/health` endpoint before making prediction requests.

---

# 🛠 Tech Stack

| Category | Technologies |
|----------|--------------|
| Frontend | Streamlit |
| Backend | FastAPI, Uvicorn |
| Machine Learning | scikit-learn |
| Data Processing | pandas, NumPy |
| Model Persistence | joblib |
| Reporting | FPDF2 |
| Communication | REST API, Requests |
| Language | Python |

---

# 📂 Project Structure

```text
AI-Predictive-Methods-for-Credit-underwriting/
│
├── api/
│   ├── __init__.py
│   ├── main.py                # FastAPI application
│   ├── model_loader.py        # Loads production ML pipeline
│   ├── predictor.py           # Prediction logic
│   └── schemas.py             # Request/Response models
│
├── models/
│   └── credit_underwriting_pipeline.pkl
│
├── streamlit_app.py           # Streamlit dashboard
├── model_training.py          # Model training pipeline
├── credit_underwriting1.csv   # Training dataset
├── requirements.txt
├── FreeSerif.ttf              # PDF report font
├── README.md
│
└── legacy/
    └── best_features_model.pkl   # Legacy model artifact
```

> **Note:** `best_features_model.pkl` is retained only for historical reference. All predictions are served using `credit_underwriting_pipeline.pkl`.

---

# 🔄 Application Workflow

```text
User
   │
   ▼
Fill Loan Application
   │
   ▼
Streamlit Dashboard
   │
HTTP POST /predict
   │
   ▼
FastAPI Backend
   │
Load Production Pipeline
   │
Preprocess Input
   │
Generate Prediction
   │
Return JSON Response
   │
   ▼
Streamlit Dashboard
   │
Display Decision
   │
Generate PDF Report
```

---

# 🔌 REST API

## Health Endpoint

### Request

```http
GET /health
```

### Response

```json
{
    "status": "ok",
    "model_loaded": true
}
```

---

## Prediction Endpoint

### Request

```http
POST /predict
```

### Request Body

```json
{
  "applicant_age": 59,
  "gender": "Women",
  "marital_status": "Single",
  "employee_status": "employed",
  "residence_type": "MORTGAGE",
  "loan_purpose": "Vehicle",
  "income_annum": 9600000,
  "loan_amount": 2400000,
  "loan_term": 12,
  "cibil_score": 778,
  "residential_assets_value": 17600000,
  "commercial_assets_value": 22700000,
  "luxury_assets_value": 8000000,
  "bank_asset_value": 29900000,
  "loan_interest": 6.54,
  "loan_percent_income": 8,
  "active_loans": 3
}
```

### Response

```json
{
  "prediction": "Approved",
  "approval_probability": 0.9987,
  "rejection_probability": 0.0013,
  "top_positive": [
    {
      "feature": "CIBIL Score",
      "impact": 1.82,
      "direction": "positive"
    }
  ],
  "top_negative": [
    {
      "feature": "Active Loans",
      "impact": -0.46,
      "direction": "negative"
    }
  ]
}
```

---

# ⚙️ Installation

Clone the repository

```bash
git clone https://github.com/krish8986/AI-Predictive-Methods-for-Credit-underwriting.git

cd AI-Predictive-Methods-for-Credit-underwriting
```

Create a virtual environment

```bash
python -m venv .venv
```

Activate it

### Windows

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# ▶️ Running the Project

## Step 1 — Start FastAPI

```bash
python -m uvicorn api.main:app --reload
```

FastAPI will be available at

```
http://127.0.0.1:8000
```

Swagger Documentation

```
http://127.0.0.1:8000/docs
```

---

## Step 2 — Start Streamlit

Open another terminal

```bash
python -m streamlit run streamlit_app.py
```

Dashboard

```
http://localhost:8501
```

---

# 📊 Input Features

The production model predicts loan approval using **17 input features**.

### Applicant Information

- Applicant Age
- Gender
- Marital Status

### Employment Details

- Employment Status
- Residence Type
- Active Loans

### Loan Details

- Loan Purpose
- Loan Amount
- Loan Term
- Interest Rate
- Loan Percentage of Income

### Financial Information

- Annual Income
- CIBIL Score

### Asset Information

- Residential Assets
- Commercial Assets
- Luxury Assets
- Bank Assets

---

# 📄 Output

The application returns:

- ✅ Loan Decision
- ✅ Approval Probability
- ✅ Rejection Probability
- ✅ SHAP Explainability
- ✅ Top Positive Factors
- ✅ Top Negative Factors
- ✅ Feature Importance Chart
- ✅ Explainable PDF Report

---

# 📸 Screenshots

## Dashboard

<p align="center">
<img src="docs/images/dashboard.png" width="100%">
</p>

---

## Prediction Result

<p align="center">
<img src="docs/images/prediction.png" width="100%">
</p>

---

## Swagger API

<p align="center">
<img src="docs/images/swagger.png" width="100%">
</p>

---

## PDF Report

<p align="center">
<img src="docs/images/pdf_report.png" width="100%">
</p>

---

# 🚀 Future Roadmap

The project will continue evolving with production-grade Machine Learning and AI features.

## Phase 1 ✅ (Completed)

- Modern Streamlit Dashboard
- FastAPI REST Backend
- Production sklearn Pipeline
- Loan Approval Prediction
- PDF Report Generation
- Input Validation
- Health Check Endpoint
- API Integration

---
## Phase 2 ✅ (Completed)

- SHAP Explainability
- Feature Importance Visualization
- Top Positive Factors
- Top Negative Factors
- Prediction Reasoning
- AI Explainability Dashboard
- Explainable PDF Reports
---

## Phase 3 🚀

- AI Credit Officer (RAG Assistant)
- Credit Policy Knowledge Base
- FAISS / ChromaDB Vector Search
- Groq LLM Integration
- Natural Language Decision Explanation
- Loan Improvement Recommendations
- Conversational AI Assistant

---

## Phase 4 🔜

- Docker Support
- CI/CD Pipeline
- Cloud Deployment
- Monitoring & Logging
- Authentication
- Rate Limiting

---

# 📈 Future Architecture

User
   │
   ▼
Streamlit Dashboard
   │
   ▼
FastAPI Backend
   │
   ▼
ML Pipeline
   │
   ▼
SHAP Explainability
   │
   ├────────► Dashboard
   │
   └────────► RAG Assistant
                 │
                 ▼
        Knowledge Base
                 │
                 ▼
           Groq LLM

---

# 💡 Engineering Highlights

This project demonstrates practical software engineering concepts beyond traditional Machine Learning projects.

### Backend Engineering

- REST API Development
- FastAPI
- Request Validation
- Response Serialization
- Modular Project Structure

---

### Machine Learning

- Gradient Boosting Classifier
- Production sklearn Pipeline
- ColumnTransformer
- OneHotEncoder
- Model Serialization
- Probability Prediction
- SHAP Explainability
- Explainable AI (XAI)
- Feature Attribution

---

### Frontend

- Streamlit Dashboard
- Custom CSS
- Interactive Forms
- API Integration
- PDF Report Generation

---

### Software Engineering

- Separation of Concerns
- Frontend–Backend Architecture
- Modular Design
- Error Handling
- Input Validation
- Clean Code Organization

---

# 🎯 Skills Demonstrated

- Python
- FastAPI
- Streamlit
- scikit-learn
- REST APIs
- Machine Learning
- Data Preprocessing
- API Integration
- Model Deployment
- Software Architecture
- Git
- GitHub
- Explainable AI (SHAP)

---

# 📚 Key Learnings

During this project I learned how to:

- Design a production-inspired ML architecture
- Separate frontend from backend services
- Build REST APIs with FastAPI
- Deploy ML models using sklearn Pipelines
- Maintain preprocessing consistency between training and inference
- Generate prediction reports programmatically
- Validate user inputs before inference
- Structure projects for scalability and maintainability

---

# 📊 Resume Highlights

This project demonstrates experience in:

- Production-ready Machine Learning
- API Development
- Backend Engineering
- ML Model Deployment
- Dashboard Development
- Software Design
- Data Processing

---

# 🎤 Interview Discussion Topics

This repository can be used to discuss:

- Why FastAPI instead of Flask?
- Why use a sklearn Pipeline?
- Why separate frontend and backend?
- Why OneHotEncoder instead of LabelEncoder?
- How is preprocessing kept consistent?
- How does the REST API work?
- How would this scale for thousands of requests?
- How would Docker improve deployment?
- How would SHAP explain predictions?
- How would a RAG assistant improve the system?
- Why SHAP instead of LIME?
- How does TreeExplainer work?
- How are feature contributions calculated?
- How do you explain ML predictions to non-technical users?

---

# 🤝 Contributions

Contributions, suggestions, and improvements are welcome.

If you find an issue or have an idea for improvement:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Open a Pull Request

---

# ⭐ Support

If you found this project useful, consider giving it a ⭐ on GitHub.

It helps increase visibility and motivates future improvements.

---

# 📄 License

This project is licensed under the MIT License.

---

# 👨‍💻 Author

**Krishna Kumar**

B.Tech in Electronics & Communication Engineering (ECE) with a Minor in AI/ML

Backend Developer • Machine Learning Engineer • AI Engineer

GitHub:
https://github.com/krish8986

LinkedIn:
https://www.linkedin.com/in/krishna-kumar-deve/

---

## ⭐ If you like this project, don't forget to star the repository!