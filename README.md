# 💸 SmartSpend

**Intelligent, AI-Powered Expense Management System**

SmartSpend is a modern full-stack application that helps you track your finances, stick to budgets, and understand your spending habits using state-of-the-art Natural Language Processing (NLP) and Machine Learning. 

---

## ✨ Key Features

🧠 **Natural Language Query Engine**  
Ask questions about your finances in plain English. No complex dashboards needed.
* *"How much did I spend on food this month?"*
* *"Compare my transport spending this month vs last month."*
* *"What was my highest expense?"*
* *"Break down my spending by category."*

🤖 **AI Auto-Categorization**  
When you log an expense, our backend uses a locally-hosted sentence transformer (`all-MiniLM-L6-v2`) to semantically embed your description and automatically predict the correct category with high confidence.

📈 **Smart Budget Forecasting**  
Leverages Linear Regression to analyze your historical spending velocity and predict if you are on track to breach your budget limits by the end of the month.

🔐 **Secure & Modern Architecture**  
* **Backend**: Flask, SQLAlchemy, JWT Authentication, Pytest.
* **Frontend**: React, React Router, dynamic chart visualizations.
* **Database**: SQLite (Development).

---

## 🚀 Quick Start

### 1. Backend Setup

The backend is written in Python 3.10+ and relies on several machine learning libraries.

```bash
# Navigate to the backend directory
cd backend

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the database seed script (generates 70+ realistic expenses for testing)
python scripts/seed_test_data.py

# Start the Flask development server
python run.py
```
> The API will be available at `http://localhost:5000`

### 2. Frontend Setup

The frontend is a React application.

```bash
# Navigate to the frontend directory
cd frontend

# Install Node dependencies
npm install

# Start the React development server
npm start
```
> The web interface will open at `http://localhost:3000`

---

## 🛠️ Testing

The backend is fully covered by a robust test suite using `pytest`.

```bash
cd backend
python -m pytest ../tests/ -v
```

Tests cover:
* JWT Authentication
* Machine Learning model confidence
* Priority Queue data structures
* Natural Language Query deterministic math and parsing

---

## 🧠 NLP Architecture

SmartSpend uses a hybrid approach for its query engine:
1. **Intent Extraction**: Python's `dateutil` and regex handles absolute/relative time slicing.
2. **Semantic Matching**: Sentence-transformers identify implicit categories.
3. **Deterministic Math**: SQLAlchemy aggregates the raw data to ensure 100% mathematical accuracy (no LLM hallucinations).
4. **Natural Phrasing**: (Optional) Integrates with local Ollama instances to generate conversational responses to the hard data.

---

*Built for advanced personal finance management.*
# SpendX
