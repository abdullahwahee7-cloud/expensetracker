import os
import dashboard as pro_dashboard
import expenses as pro_expenses
import budgets as pro_budgets
import categories as pro_categories
import reports as pro_reports
import account as pro_account
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from flask_wtf.csrf import CSRFProtect
from helpers import apology, login_required, usd

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
app.jinja_env.filters["usd"] = usd
csrf = CSRFProtect(app)
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username").strip()
        from sqlalchemy import text
        existingUsers = db.execute(
            text("SELECT username FROM users WHERE LOWER(username) = :username"),
            {"username": username.lower()}
        ).fetchone()
        if existingUsers:
            return render_template("register.html", username=username)

        if not username:
            return apology("must provide username", 403)

        password = request.form.get("password")
        if not password:
            return apology("must provide password", 403)

        hashedPass = generate_password_hash(password)
        now = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        newUserID = db.execute("INSERT INTO users (username, hash, registerDate, lastLogin) VALUES (:username, :hashedPass, :registerDate, :lastLogin) RETURNING id",
                               {"username": username, "hashedPass": hashedPass, "registerDate": now, "lastLogin": now}).fetchone()[0]
        db.commit()

        db.execute("INSERT INTO userCategories (category_id, user_id) VALUES (1, :usersID), (2, :usersID), (3, :usersID), (4, :usersID), (5, :usersID), (6, :usersID), (7, :usersID), (8, :usersID)",
                   {"usersID": newUserID})
        db.commit()

        session["user_id"] = newUserID

        return redirect("/")

    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide username", 403)

        elif not request.form.get("password"):
            return apology("must provide password", 403)

        rows = db.execute(text("SELECT * FROM users WHERE username = :username"),
                  {"username": request.form.get("username")}).fetchall()

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        session["user_id"] = rows[0]["id"]

        now = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        db.execute(
            "UPDATE users SET lastLogin = :lastLogin WHERE id = :usersID", {"lastLogin": now, "usersID": session["user_id"]})
        db.commit()

        return redirect("/")

    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "GET":
        expenses_year = None
        expenses_month = None
        expenses_week = None
        expenses_last5 = None
        spending_week = []
        spending_month = []

        categories = pro_categories.getSpendCategories(session["user_id"])
        payers = pro_account.getPayers(session["user_id"])
        date = datetime.today().strftime('%Y-%m-%d')
        income = pro_account.getIncome(session["user_id"])
        expenses_year = pro_dashboard.getTotalSpend_Year(session["user_id"])
        expenses_month = pro_dashboard.getTotalSpend_Month(session["user_id"])
        expenses_week = pro_dashboard.getTotalSpend_Week(session["user_id"])
        expenses_last5 = pro_dashboard.getLastFiveExpenses(session["user_id"])
        budgets = pro_dashboard.getBudgets(session["user_id"])
        weeks = pro_dashboard.getLastFourWeekNames()
        spending_week = pro_dashboard.getWeeklySpending(weeks, session["user_id"])
        spending_month = pro_dashboard.getMonthlySpending(session["user_id"])
        spending_trends = pro_dashboard.getSpendingTrends(session["user_id"])
        payersChart = pro_reports.generatePayersReport(session["user_id"])

        return render_template("index.html", categories=categories, payers=payers, date=date, income=income, expenses_year=expenses_year, expenses_month=expenses_month, expenses_week=expenses_week, expenses_last5=expenses_last5,
                               budgets=budgets, spending_week=spending_week, spending_month=spending_month, spending_trends=spending_trends, payersChart=payersChart)

    else:
        formData = list(request.form.items())
        formData.pop(0)
        expenses = pro_expenses.addExpenses(formData, session["user_id"])
        return render_template("expensed.html", results=expenses)

@app.route("/expenses", methods=["GET"])
@login_required
def expenses():
    return render_template("expenses.html")

@app.route("/addexpenses", methods=["GET", "POST"])
@login_required
def addexpenses():
    if request.method == "POST":
        formData = list(request.form.items())
        formData.pop(0)
        expenses = pro_expenses.addExpenses(formData, session["user_id"])
        return render_template("expensed.html", results=expenses)

    else:
        categories = pro_categories.getSpendCategories(session["user_id"])
        payers = pro_account.getPayers(session["user_id"])
        date = datetime.today().strftime('%Y-%m-%d')
        return render_template("addexpenses.html", categories=categories, date=date, payers=payers)

@app.route("/expensehistory", methods=["GET", "POST"])
@login_required
def expensehistory():
    if request.method == "GET":
        history = pro_expenses.getHistory(session["user_id"])
        categories = pro_categories.getSpendCategories(session["user_id"])
        payers = pro_account.getPayers(session["user_id"])
        return render_template("expensehistory.html", history=history, categories=categories, payers=payers, isDeleteAlert=False)

    else:
        userHasSelected_deleteExpense = False

        if "btnDeleteConfirm" in request.form:
            userHasSelected_deleteExpense = True
        elif "btnSave" in request.form:
            userHasSelected_deleteExpense = False
        else:
            return apology("Doh! Spend Categories is drunk. Try again!")

        oldExpense = pro_expenses.getExpense(request.form, session["user_id"])

        if oldExpense["id"] == None:
            return apology("The expense record you're trying to update doesn't exist")

        if userHasSelected_deleteExpense == True:
            deleted = pro_expenses.deleteExpense(oldExpense, session["user_id"])
            if not deleted:
                return apology("The expense was unable to be deleted")

            history = pro_expenses.getHistory(session["user_id"])
            categories = pro_categories.getSpendCategories(session["user_id"])
            payers = pro_account.getPayers(session["user_id"])
            return render_template("expensehistory.html", history=history, categories=categories, payers=payers, isDeleteAlert=True)

        else:
            expensed = pro_expenses.updateExpense(oldExpense, request.form, session["user_id"])
            if not expensed:
                return apology("The expense was unable to be updated")

            return render_template("expensed.html", results=expensed)

@app.route("/budgets", methods=["GET", "POST"])
@app.route("/budgets/<int:year>", methods=["GET"])
@login_required
def budgets(year=None):
    if year:
        currentYear = datetime.now().year
        if not 2020 <= year <= currentYear:
            return apology(f"Please select a valid budget year: 2020 through {currentYear}")
    else:
        year = datetime.now().year

    if request.method == "GET":
        income = pro_account.getIncome(session["user_id"])
        budgets = pro_budgets.getBudgets(session["user_id"])
        budgeted = pro_budgets.getTotalBudgetedByYear(session["user_id"], year)

        return render_template("budgets.html", income=income, budgets=budgets, year=year, budgeted=budgeted, deletedBudgetName=None)

    else:
        budgetName = request.form.get("delete").strip()
        deletedBudgetName = pro_budgets.deleteBudget(budgetName, session["user_id"])

        if deletedBudgetName:
            income = pro_account.getIncome(session["user_id"])
            budgets = pro_budgets.getBudgets(session["user_id"])
            budgeted = pro_budgets.getTotalBudgetedByYear(session["user_id"], year)

            return render_template("budgets.html", income=income, budgets=budgets, year=year, budgeted=budgeted, deletedBudgetName=deletedBudgetName)
        else:
            return apology("Uh oh! Your budget could not be deleted.")

@app.route("/createbudget", methods=["GET", "POST"])
@login_required
def createbudget():
    if request.method == "POST":
        budgets = pro_budgets.getBudgets(session["user_id"])
        if budgets:
            budgetCount = 0
            for year in budgets:
                budgetCount += len(budgets[year])
            if budgetCount >= 20:
                return apology("You've reached the max amount of budgets'")

        formData = list(request.form.items())
        formData.pop(0)
        budgetDict = pro_budgets.generateBudgetFromForm(formData)

        if "apology" in budgetDict:
            return apology(budgetDict["apology"])
        else:
            budget = pro_budgets.createBudget(budgetDict, session["user_id"])
            if "apology" in budget:
                return apology(budget["apology"])
            else:
                return render_template("budgetcreated.html", results=budget)
    else:
        income = pro_account.getIncome(session["user_id"])
        budgeted = pro_budgets.getTotalBudgetedByYear(session["user_id"])
        categories = pro_categories.getSpendCategories(session["user_id"])

        return render_template("createbudget.html", income=income, budgeted=budgeted, categories=categories)

@app.route("/updatebudget/<urlvar_budgetname>", methods=["GET", "POST"])
@login_required
def updatebudget(urlvar_budgetname):
    if request.method == "POST":
        formData = list(request.form.items())
        formData.pop(0)
        budgetDict = pro_budgets.generateBudgetFromForm(formData)

        if "apology" in budgetDict:
            return apology(budgetDict["apology"])
        else:
            budget = pro_budgets.updateBudget(urlvar_budgetname, budgetDict, session["user_id"])

            if "apology" in budget:
                return apology(budget["apology"])
            else:
                return render_template("budgetcreated.html", results=budget)

    else:
        budgetID = pro_budgets.getBudgetID(urlvar_budgetname, session["user_id"])
        if budgetID is None:
            return apology("'" + urlvar_budgetname + "' budget does not exist")
        else:
            budget = pro_budgets.getBudgetByID(budgetID, session["user_id"])
        income = pro_account.getIncome(session["user_id"])
        budgeted = pro_budgets.getTotalBudgetedByYear(session["user_id"], budget['year'])
        budget = pro_budgets.getUpdatableBudget(budget, session["user_id"])

        return render_template("updatebudget.html", income=income, budgeted=budgeted, budget=budget)

@app.route("/categories", methods=["GET", "POST"])
@login_required
def categories():
    if request.method == "POST":
        userHasSelected_newCategory = False
        userHasSelected_renameCategory = False
        userHasSelected_deleteCategory = False
        alert_newCategory = None
        alert_renameCategory = None
        alert_deleteCategory = None

        if "btnCreateCategory" in request.form:
            userHasSelected_newCategory = True
        elif "btnRenameCategory" in request.form:
            userHasSelected_renameCategory = True
        elif "btnDeleteCategory" in request.form:
            userHasSelected_deleteCategory = True
        else:
            return apology("Doh! Spend Categories is drunk. Try again!")

        if userHasSelected_newCategory:
            newCategoryName = request.form.get("createName").strip()
            categoryCount = len(pro_categories.getSpendCategories(session["user_id"]))
            if categoryCount >= 30:
                return apology("You've reached the max amount of categories")

            categoryID = pro_categories.getCategoryID(newCategoryName)

            if categoryID:
                existingID = pro_categories.getCategoryID(newCategoryName, session["user_id"])
                if (existingID):
                    return apology("You already have '" + newCategoryName + "' category")
                else:
                    pro_categories.addCategory_User(categoryID, session["user_id"])
            else:
                newCategoryID = pro_categories.addCategory_DB(newCategoryName)
                pro_categories.addCategory_User(newCategoryID, session["user_id"])

            alert_newCategory = newCategoryName

        if userHasSelected_renameCategory:
            oldCategoryName = request.form.get("oldname").strip()
            newCategoryName = request.form.get("newname").strip()
            oldCategoryID = pro_categories.getCategoryID(oldCategoryName)

            if oldCategoryID is None:
                return apology("The category you're trying to rename doesn't exist")

            newCategoryID = pro_categories.getCategoryID(newCategoryName)

            if newCategoryID:
                existingID = pro_categories.getCategoryID(newCategoryName, session["user_id"])
                if existingID:
                    return apology("You already have '" + newCategoryName + "' category")
                newCategoryNameFromDB = pro_categories.getSpendCategoryName(newCategoryID)
                pro_categories.renameCategory(oldCategoryID, newCategoryID, oldCategoryName, newCategoryNameFromDB, session["user_id"])
            else:
                newCategoryID = pro_categories.addCategory_DB(newCategoryName)
                pro_categories.renameCategory(oldCategoryID, newCategoryID, oldCategoryName, newCategoryName, session["user_id"])

            alert_renameCategory = [oldCategoryName, newCategoryName]

        if userHasSelected_deleteCategory:
            deleteName = request.form.get("delete").strip()
            categoryID = pro_categories.getCategoryID(deleteName)

            if categoryID is None:
                return apology("The category you're trying to delete doesn't exist")

            categoryCount = len(pro_categories.getSpendCategories(session["user_id"]))
            if categoryCount <= 1:
                return apology("You need to keep at least 1 spend category")

            pro_categories.deleteCategory(categoryID, session["user_id"])
            alert_deleteCategory = deleteName

        categories = pro_categories.getSpendCategories(session["user_id"])
        return render_template("categories.html", categories=categories, newCategory=alert_newCategory, renamedCategory=alert_renameCategory, deleteCategory=alert_deleteCategory)

    else:
        categories = pro_categories.getSpendCategories(session["user_id"])
        categoryBudgets = pro_categories.getBudgetsSpendCategories(session["user_id"])
        categoriesWithBudgets = pro_categories.generateSpendCategoriesWithBudgets(categories, categoryBudgets)

        return render_template("categories.html", categories=categoriesWithBudgets, newCategory=None, renamedCategory=None, deleteCategory=None)

@app.route("/reports", methods=["GET"])
@login_required
def reports():
    return render_template("reports.html")

@app.route("/budgetsreport", methods=["GET"])
@app.route("/budgetsreport/<int:year>", methods=["GET"])
@login_required
def budgetsreport(year=None):
    if year:
        currentYear = datetime.now().year
        if not 2020 <= year <= currentYear:
            return apology(f"Please select a valid budget year: 2020 through {currentYear}")
    else:
        year = datetime.now().year

    budgets = pro_reports.generateBudgetsReport(session["user_id"], year)

    return render_template("budgetsreport.html", budgets=budgets, year=year)

@app.route("/monthlyreport", methods=["GET"])
@app.route("/monthlyreport/<int:year>", methods=["GET"])
@login_required
def monthlyreport(year=None):
    if year:
        currentYear = datetime.now().year
        if not 2020 <= year <= currentYear:
            return apology(f"Please select a valid budget year: 2020 through {currentYear}")
    else:
        year = datetime.now().year

    monthlySpending = pro_reports.generateMonthlyReport(session["user_id"], year)

    return render_template("monthlyreport.html", monthlySpending=monthlySpending, year=year)

@app.route("/spendingreport", methods=["GET"])
@app.route("/spendingreport/<int:year>", methods=["GET"])
@login_required
def spendingreport(year=None):
    if year:
        currentYear = datetime.now().year
        if not 2020 <= year <= currentYear:
            return apology(f"Please select a valid budget year: 2020 through {currentYear}")
    else:
        year = datetime.now().year

    spendingReport = pro_reports.generateSpendingTrendsReport(session["user_id"], year)

    return render_template("spendingreport.html", spending_trends_chart=spendingReport["chart"], spending_trends_table=spendingReport["table"], categories=spendingReport["categories"], year=year)

@app.route("/payersreport", methods=["GET"])
@app.route("/payersreport/<int:year>", methods=["GET"])
@login_required
def payersreport(year=None):
    if year:
        currentYear = datetime.now().year
        if not 2020 <= year <= currentYear:
            return apology(f"Please select a valid budget year: 2020 through {currentYear}")
    else:
        year = datetime.now().year

    payersReport = pro_reports.generatePayersReport(session["user_id"], year)

    return render_template("payersreport.html", payers=payersReport, year=year)

@app.route("/account", methods=["GET", "POST"])
@login_required
def updateaccount():
    if request.method == "POST":
        userHasSelected_updateIncome = False
        userHasSelected_addPayer = False
        userHasSelected_renamePayer = False
        userHasSelected_deletePayer = False
        userHasSelected_updatePassword = False
        alert_updateIncome = None
        alert_addPayer = None
        alert_renamePayer = None
        alert_deletePayer = None
        alert_updatePassword = None

        if "btnUpdateIncome" in request.form:
            userHasSelected_updateIncome = True
        elif "btnSavePayer" in request.form:
            userHasSelected_addPayer = True
        elif "btnRenamePayer" in request.form:
            userHasSelected_renamePayer = True
        elif "btnDeletePayer" in request.form:
            userHasSelected_deletePayer = True
        elif "btnUpdatePassword" in request.form:
            userHasSelected_updatePassword = True
        else:
            return apology("Doh! Your Account is drunk. Try again!")

        if userHasSelected_updateIncome:
            newIncome = float(request.form.get("income").strip())
            updatedIncome = pro_account.updateIncome(newIncome, session["user_id"])
            if updatedIncome != 1:
                return apology(updatedIncome["apology"])
            alert_updateIncome = newIncome

        if userHasSelected_addPayer:
            newName = request.form.get("payerName").strip()
            newPayer = pro_account.addPayer(newName, session["user_id"])
            if newPayer != 1:
                return apology(newPayer["apology"])
            alert_addPayer = newName

        if userHasSelected_renamePayer:
            oldName = request.form.get("oldpayer").strip()
            newName = request.form.get("newpayer").strip()
            renamedPayer = pro_account.renamePayer(oldName, newName, session["user_id"])
            if renamedPayer != 1:
                return apology(renamedPayer["apology"])
            alert_renamePayer = [oldName, newName]

        if userHasSelected_deletePayer:
            name = request.form.get("delete").strip()
            deletedPayer = pro_account.deletePayer(name, session["user_id"])
            if deletedPayer != 1:
                return apology(renamedPayer["apology"])
            alert_deletePayer = name

        if userHasSelected_updatePassword:
            updatedPassword = pro_account.updatePassword(request.form.get("currentPassword"), request.form.get("newPassword"), session["user_id"])
            if updatedPassword != 1:
                return apology(updatedPassword["apology"])
            alert_updatePassword = True

        user = pro_account.getAllUserInfo(session["user_id"])

        return render_template("account.html", username=user["name"], income=user["income"], payers=user["payers"], stats=user["stats"], newIncome=alert_updateIncome, addPayer=alert_addPayer, renamedPayer=alert_renamePayer, deletedPayer=alert_deletePayer, updatedPassword=alert_updatePassword)
    else:
        user = pro_account.getAllUserInfo(session["user_id"])
        return render_template("account.html", username=user["name"], income=user["income"], payers=user["payers"], stats=user["stats"], newIncome=None, addPayer=None, renamedPayer=None, deletedPayer=None, updatedPassword=None)

def errorhandler(e):
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)

for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

if __name__ == "__main__":
    app.run(debug=True)
