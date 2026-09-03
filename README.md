<p align="center">
  <img src="static/logo.png" alt="AIN project logo" width="180">
</p>

<h1 align="center">Financial Tracker 💸</h1>

<p align="center">
  <strong>A Flask-based expense, budget and personal spending tracker.</strong><br>
  Log day-to-day expenses, organise them into categories, set yearly budgets and get a much clearer picture of where the money actually went.
</p>

---

## About the project

Financial Tracker is a personal finance web app built with Python, Flask and PostgreSQL. The idea behind it is pretty simple: instead of keeping expenses in random notes or opening a spreadsheet every time, you can record everything in one place and let the dashboard do the boring calculations.

The app is not huge, but theres quite a lot going on under the hood. It supports user accounts, custom spending categories, multiple payers, yearly budgets, editable expense history, charts and detailed reports. It is not pretending to be a full banking platform either — this is a practical project with a few rough edges, and honestly thats fine.

## What you can do

### Dashboard

The dashboard gives a quick overview of the current year, including:

- Remaining income after recorded expenses
- Total spending for the year, current month and current week
- The five most recently added expenses
- Budget progress with spent and remaining amounts
- Weekly and monthly spending charts
- Category spending trends
- Spending split between different payers
- A quick-expense form so a new expense can be added without leaving the dashboard

### Expenses

Expenses can be added individually or several at once. Each record stores a description, spending category, date, payer and amount.

The expense-history page also lets a user go back and edit or delete an old entry, which is useful because mistakes happen and nobody wants one typo living in a report forever.

### Budgets

Users can create, update and delete annual budgets. A budget can be connected to one or more spending categories, with a percentage assigned to each category.

The application currently allows up to 20 budgets per user, and budget reports compare the planned amount against the expenses recorded in the linked categories.

### Spending categories

Every new account starts with eight default categories from the database. Users can then add their own categories, rename existing ones or remove categories they no longer use.

Renaming a category also updates matching expense records and linked budgets. The current limit is 30 active categories per user, with at least one category required at all times.

### Reports

Reports can be viewed by year, starting from 2020. The included reports cover:

- Budget performance and the expenses attached to each budget
- Monthly spending totals and full expense history
- Spending by category, including monthly totals
- Total spending by payer

Several report tables support copying data or exporting it as CSV or Excel files through DataTables.

### Account settings

From the account page, a user can:

- Update the income amount used by the dashboard and budget calculations
- Add, rename or delete payers
- Change their password
- View account statistics such as the registration date and the number of expenses, budgets, categories and payers

`Self` is always available as a payer, and each account can add up to five additional payers.

## Built with

| Area | Technology |
| --- | --- |
| Backend | Python 3.9 and Flask |
| Templates | Jinja2 |
| Database | PostgreSQL |
| Database access | SQLAlchemy with parameterised SQL queries |
| Authentication | Werkzeug password hashing and Flask sessions |
| Form protection | Flask-WTF CSRF protection |
| Frontend | HTML, CSS, Bootstrap 4 and JavaScript |
| Charts | Chart.js |
| Report tables | jQuery DataTables |
| Icons | Font Awesome |

## Project structure

```text
expensetracker/
├── .vscode/
│   ├── launch.json          # VS Code Flask launch configuration
│   └── settings.json        # Local Python interpreter setting
├── static/
│   ├── css/                 # Bootstrap and project styles
│   ├── js/                  # Dashboard, expense, budget and report scripts
│   ├── favicon.ico
│   └── logo.png
├── templates/               # Jinja templates for all pages
├── app.py                   # Flask app, routes and request handling
├── helpers.py               # Login guard, error page and formatting helpers
├── pro_account.py           # Income, payer, password and account logic
├── pro_budgets.py           # Budget creation and management
├── pro_categories.py        # Spending-category logic
├── pro_dashboard.py         # Dashboard totals and chart data
├── pro_expenses.py          # Expense creation, history, editing and deletion
├── pro_reports.py           # Budget, monthly, category and payer reports
└── README.md
```

Generated folders such as `env/`, `flask_session/` and `__pycache__/` are intentionally not part of the structure above because they should not be committed to the repository.

## Running the project locally

### 1. Clone the repository

```bash
git clone https://github.com/abdullahwahee7-cloud/expensetracker.git
cd expensetracker
```

### 2. Create a virtual environment

This project was originally set up with Python 3.9, which is the safest version to use with its current dependency versions.

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Or on macOS/Linux:

```bash
source .venv/bin/activate
```

### 3. Install the dependencies

The code uses older Flask and SQLAlchemy APIs, so installing the matching versions avoids a lot of unnecessary compatibility errors.

```bash
pip install Flask==1.1.2 Flask-Session==0.3.1 Flask-WTF==0.14.3 Jinja2==2.11.3 MarkupSafe==1.1.1 Werkzeug==0.16.1 WTForms==2.3.3 SQLAlchemy==1.3.16 psycopg2-binary==2.9.10 python-dotenv==1.0.1 requests==2.23.0 click==7.1.2 itsdangerous==1.1.0 gunicorn==20.0.4
```

A proper `requirements.txt` would be a good addition later. For now, the command above matches the versions used by the supplied project environment closely.

### 4. Add environment variables

Create a file named `.env` in the project root:

```env
SECRET_KEY=replace-this-with-a-long-random-secret
DATABASE_URL=postgresql+psycopg2://username:password@localhost:5432/financial_tracker
```

A secure secret key can be generated with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Never commit the real `.env` file. A safe `.env.example` containing empty placeholders can be committed instead.

### 5. Prepare PostgreSQL

The application expects a PostgreSQL database with the following tables:

| Table | Purpose |
| --- | --- |
| `users` | Usernames, password hashes, income and account dates |
| `expenses` | Individual expense records |
| `categories` | Shared category library |
| `userCategories` | Categories enabled for each user |
| `budgets` | Annual budgets created by users |
| `budgetCategories` | Links budgets to categories and stores category percentages |
| `payers` | Additional payers belonging to each user |

One important detail: registration automatically attaches category IDs `1` through `8` to a new user. Those eight category rows therefore need to exist before new accounts are registered.

A database schema or migration file is not currently included in this repository. Until one is added, you will need an existing compatible database or create the tables yourself based on the queries in the Python modules.

The SQL also uses PostgreSQL-specific functions such as `date_part` and `date_trunc`, so swapping the database to SQLite is not a one-line change.

### 6. Start the development server

```bash
python app.py
```

The application should then be available at:

```text
http://127.0.0.1:5000
```

You can also run it through the Flask CLI:

```bash
flask run
```

## Environment variables

| Variable | Required | Description |
| --- | --- | --- |
| `SECRET_KEY` | Yes | Signs Flask sessions and CSRF tokens. Use a long random value. |
| `DATABASE_URL` | Yes | SQLAlchemy PostgreSQL connection string. |

## Files that should stay out of GitHub

The local environment, secrets, session data and Python cache files do not belong in the repository. A useful `.gitignore` is:

```gitignore
# Secrets
.env
.env.*
!.env.example

# Virtual environments
env/
venv/
.venv/

# Flask filesystem sessions
flask_session/
sessions/

# Python cache
__pycache__/
*.py[cod]

# Local database or instance data
instance/

# Operating-system files
.DS_Store
Thumbs.db
```

The `.vscode/` folder can stay in the repository if the launch configuration is meant to be shared. Just remember that interpreter paths inside `settings.json` may be different on somebody else's computer.

## Security notes

Passwords are stored as Werkzeug-generated hashes rather than plain text, forms are protected with CSRF tokens and private pages require a logged-in session.

For an actual deployment, a few things still need attention:

- Do not run the public site with `debug=True`
- Use HTTPS and secure cookie settings
- Store secrets only in the hosting platform's environment variables
- Use a production WSGI server such as Gunicorn
- Replace filesystem sessions with a shared session store if the app runs on multiple server instances
- Review and update the older Python package versions before exposing the app publicly

## Current limitations

This is a working project, but it is not production-ready yet. The main things still missing are:

- A committed database schema or migration system
- Automated tests
- A `requirements.txt` file
- Modern Flask and SQLAlchemy compatibility
- Stronger server-side validation for some form values
- Pagination for very large expense histories
- A cleaner deployment configuration

The frontend also loads Chart.js, jQuery, DataTables, Font Awesome and a few other assets from public CDNs, so some charts and report features may not work properly without an internet connection.

## Ideas for later

Some features that would fit the project nicely:

- Recurring expenses and subscriptions
- Monthly budgets as well as yearly budgets
- Search and filters for expense history
- Receipt uploads
- Downloadable PDF reports
- More currencies and user-selectable currency formatting
- Email or in-app budget warnings
- Database migrations with Flask-Migrate or Alembic
- Unit and integration tests

## Credits

Created by **Ibrahim, Taha, Abdullah and Areeb**.

## License

No license file is included at the moment. Until a license is added, the source code should not be assumed to be open for unrestricted reuse or redistribution.
