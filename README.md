# 💰 Smart Expense Tracker

An AI-powered expense management application that helps users track, analyze, and understand their spending habits through interactive dashboards and intelligent chatbot support.

---

## 🚀 Features

### 🔐 1. Authentication System
- User Registration (new users)
- Login (existing users)
- Username + Password based authentication
- Secure session management
- Logout functionality
- User-scoped database isolation (each user's data is securely separated)

---

### ➕ 2. Add / Update Expenses
- Manually add expenses for **any selected date**
- Update previously added expenses
- Edit category, amount, notes, and date
- Persistent storage in user-specific tables

---

### 🤖 3. AI Chatbot Support
- Chatbot answers financial questions using **only the logged-in user's data**
- Powered by an LLM
- Example queries:
  - "How much did I spend on food last month?"
  - "What was my highest spending category in January?"
  - "Compare my expenses between Jan and Feb"
- Uses database querying (SQL) over user-scoped tables

---

### 📊 4. Analytics Dashboard
- Select any **start date and end date**
- Fetch expense records within selected range
- Visualizations:
  - 📊 Bar Chart (Category-wise spending)
  - 🥧 Pie Chart (Spending distribution)
- Auto-generated insights summary using LLM:
  - Spending trends
  - Highest expense categories
  - Unusual spending patterns

---

### 🔄 5. Reset Data
- Completely wipes all stored expense data
- Operates only for the currently logged-in user
- Safe and isolated deletion

---

### 🚪 6. Logout
- Ends user session
- Redirects to login page
- Clears authentication tokens/session

---

## 🏗️ Tech Stack

**Frontend**
- Streamlit

**Backend**
- Python (FastAPI)
- MYSQL
- SQLAlchemy (ORM)
- Langchain

**AI Integration**
- LLM for:
  - Expense summarization
  - Natural language SQL querying
  - Financial insights generation

**Visualization**
- Plotly

---

## 🗂️ Project Structure

```
├── expense-tracker
    ├──ExpenseTracker
        ├── backend/
        │   ├── analytics_summarizer.py
        │   ├── db_interaction.py
        │   ├── fetch_userid_and_userscope_tables.py
        │   ├── logging_setup.py
        │   ├── server.py
        │   ├── tool_based_sql_agent.py
        │
        ├── frontend/
        │   ├── streamlit/
        │   ├── add_update_dashboard.py
        │   ├── analytics_dashboard.py
        │   ├── app.py
        │   ├── auth_dashboard.py
        │   ├── chatbot_support.py
        │   ├── db_reset_dashboard.py
        │
        ├── test/
        │   ├── backend_test/
        │       ├── test_db_interaction.py
        │   ├── frontend_test/
        │
        ├── pytest.toml
        ├── requirements.txt
        ├── README.md
    ├──screenshots
```

---

## 🗃️ Database Design

### Users Table (LOGGED_USERS)

| Column   | Type                    |
|---------|-------------------------|
| id      | Integer (Primary Key)   |
| username | String (Unique)         |
| password| String                  |

### User-Scoped Expenses Table

| Column       | Type                  |
|--------------|-----------------------|
| expense_id   | Integer (Primary Key) |
| id           | Foreign Key           |
| amount       | Float                 |
| category     | String                |
| expense_date | Date                  |
| notes        | Text                  |

> All queries are filtered using `user_id` to ensure data isolation.

---

## 🧠 How AI Integration Works

1. User asks a natural language question.
2. Backend:
   - Extracts user context (`user_id`)
   - Generates SQL query using LLM
   - Executes query on user-scoped data
3. LLM formats the response into human-readable insights.

---

## 🔒 Security Considerations

- Password hashing (bcrypt / argon2)
- User-scoped SQL filtering
- Protected routes via authentication middleware
- No cross-user data access
- Session/token validation

---

## ⚙️ Installation

### 1️⃣ Clone Repository

```bash
git clone https://github.com/Soumyadip54321/efficient-expense-tracker
cd efficient-expense-tracker
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Run Application From expense-tracker(root)

```bash
(Start server)
fastapi dev ExpenseTracker/backend/server.py

(Serve UI)
python3 -m streamlit run ExpenseTracker/frontend/app.py
```

---

## 📈 Example Use Case Flow

1. Register/Login
2. Add daily expenses
3. View analytics for selected period
4. Ask chatbot:
   - “Where am I overspending?”
5. Reset data if needed
6. Logout

---

## 🛠️ Future Enhancements

- Budget goal tracking to optimize savings
- Predict future spends using ML
- Convert auto-summarization to speech
- Automated expense pulling using OCR from images and PDFs
- Password hiding while typing
- Inclusion of other user credentials while login - Mobile, address etc.
- OTP based login.

---

## 📌 Key Highlights

✔ User-isolated secure data  
✔ AI-powered insights  
✔ Natural language expense queries  
✔ Visual analytics  
✔ Clean modular backend  
