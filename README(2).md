<p align="center">
  <img src="static/logo.png" alt="Financial Tracker logo" width="150">
</p>

<h1 align="center">Financial Tracker</h1>

<p align="center">
  <strong>A full-stack personal finance application that helps users record expenses, plan budgets, and understand where their money is going.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9-3776AB?logo=python&logoColor=white" alt="Python 3.9">
  <img src="https://img.shields.io/badge/Flask-Web%20App-000000?logo=flask&logoColor=white" alt="Flask">
  <img src="https://img.shields.io/badge/PostgreSQL-Database-4169E1?logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/JavaScript-Interactive%20UI-F7DF1E?logo=javascript&logoColor=000000" alt="JavaScript">
  <img src="https://img.shields.io/badge/Bootstrap-Responsive%20Design-7952B3?logo=bootstrap&logoColor=white" alt="Bootstrap">
</p>

## About the project

Financial Tracker turns everyday expense records into a useful picture of a user's financial activity. A user can record purchases, organise them by category and payer, create annual budgets, and then review the same data through dashboard summaries, charts, and year-based reports.

The goal was to build more than a basic form connected to a database. The application combines user accounts, relational data, budget calculations, editable transaction history, interactive visualisations, and downloadable reports in one complete workflow.

This was developed as a collaborative project by **Ibrahim, Taha, Abdullah, and Areeb**.

## What users can do

- **Create a personal account** and sign in through session-based authentication.
- **Record expenses quickly** from the dashboard or add several expenses in one entry form.
- **Edit and delete past records** through a searchable expense-history table.
- **Organise spending** using custom categories and different payers.
- **Create annual budgets** and divide each budget across selected spending categories.
- **Track progress visually** with spent-versus-remaining budget charts.
- **Review weekly, monthly, and yearly totals**, including remaining income and recent activity.
- **Explore detailed reports** for budgets, monthly spending, category trends, and payer contributions.
- **Export table data** to formats such as CSV and Excel for further analysis.

## Why this project is interesting

The same expense affects several areas of the application at once. When a user records a transaction, it can change the dashboard totals, the remaining income, a category trend, a payer report, and the progress of one or more budgets. Keeping those views consistent required the backend, database queries, and frontend charts to work together rather than existing as separate demo pages.

The project demonstrates practical experience with:

- designing a multi-user, database-backed web application;
- writing PostgreSQL queries for weekly, monthly, yearly, category, and payer-based analysis;
- separating account, expense, budget, category, dashboard, and reporting logic into focused modules;
- protecting passwords with hashing and forms with CSRF tokens;
- building responsive server-rendered pages with Jinja and Bootstrap;
- turning backend data into interactive Chart.js visualisations;
- adding search, sorting, and exports with jQuery DataTables.

## Technology stack

| Area | Technologies |
| --- | --- |
| Backend | Python, Flask |
| Database | PostgreSQL, SQLAlchemy |
| Authentication | Flask-Session, Werkzeug password hashing |
| Form protection | Flask-WTF, CSRF protection |
| Frontend | HTML, CSS, JavaScript, Jinja2, Bootstrap |
| Charts | Chart.js |
| Tables and exports | jQuery DataTables |
| Deployment support | Gunicorn |

## Repository structure

```text
expensetracker/
├── static/             # CSS, JavaScript, logo, and browser assets
├── templates/          # Jinja templates for all application pages
├── app.py              # Flask application, routes, and authentication flow
├── account.py          # Income, payer, password, and account operations
├── budgets.py          # Budget creation, updates, and calculations
├── categories.py       # Spending-category management
├── dashboard.py        # Dashboard summaries and chart data
├── expenses.py         # Expense creation, history, editing, and deletion
├── reports.py          # Budget, monthly, category, and payer reports
├── helpers.py          # Shared authentication, formatting, and error helpers
├── requirements.txt    # Python runtime dependencies
└── README.md
```

<details>
<summary><strong>Run the project locally</strong></summary>

### 1. Clone the repository

```bash
git clone https://github.com/abdullahwahee7-cloud/expensetracker.git
cd expensetracker
```

### 2. Create a Python 3.9 virtual environment

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS or Linux:

```bash
source .venv/bin/activate
```

### 3. Install the dependencies

```bash
pip install -r requirements.txt
```

### 4. Add the environment variables

Create a local `.env` file in the project root:

```env
SECRET_KEY=replace_with_a_long_random_secret
DATABASE_URL=postgresql+psycopg2://username:password@localhost:5432/financial_tracker
```

The real `.env` file should stay local and must not be committed to the repository.

### 5. Prepare PostgreSQL

The application expects a PostgreSQL database containing the project tables for users, expenses, categories, user-category relationships, payers, budgets, and budget-category relationships. The current repository assumes that this schema already exists.

### 6. Start Flask

Windows PowerShell:

```powershell
$env:FLASK_APP = "app.py"
flask run
```

macOS or Linux:

```bash
export FLASK_APP=app.py
flask run
```

Open `http://127.0.0.1:5000` in a browser.

</details>

## Project status

The core application is complete and covers account management, expense tracking, budgeting, analytics, and reporting. Strong next steps would be adding automated tests, database migrations, and a hosted demo.
