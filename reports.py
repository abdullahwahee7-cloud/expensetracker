import os
import calendar
import copy
import dashboard as pro_dashboard
import categories as pro_categories
import budgets as pro_budgets
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from helpers import convertSQLToDict
from datetime import datetime

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


def generateBudgetsReport(userID, year=None):
    budgetsReport = []

    if not year:
        year = datetime.now().year

    budgetsReport = pro_dashboard.getBudgets(userID, year)

    if budgetsReport:
        for record in budgetsReport:
            budgetID = pro_budgets.getBudgetID(record["name"], userID)
            results = db.execute("SELECT expenses.description, expenses.category, expenses.expenseDate, expenses.payer, expenses.amount FROM expenses WHERE user_id = :usersID AND date_part('year', date(expensedate)) = :year AND category IN (SELECT categories.name FROM budgetcategories INNER JOIN categories on budgetcategories.category_id = categories.id WHERE budgetcategories.budgets_id = :budgetID)",
                                 {"usersID": userID, "year": year, "budgetID": budgetID}).fetchall()
            expenseDetails = convertSQLToDict(results)
            record["expenses"] = expenseDetails

    return budgetsReport


def generateMonthlyReport(userID, year=None):

    if not year:
        year = datetime.now().year

    spending_month_chart = pro_dashboard.getMonthlySpending(userID, year)

    results = db.execute(
        "SELECT description, category, expensedate, amount, payer FROM expenses WHERE user_id = :usersID AND date_part('year', date(expensedate)) = :year ORDER BY id ASC", {"usersID": userID, "year": year}).fetchall()
    spending_month_table = convertSQLToDict(results)

    monthlyReport = {"chart": spending_month_chart,
                     "table": spending_month_table}

    return monthlyReport


def generateSpendingTrendsReport(userID, year=None):

    if not year:
        year = datetime.now().year

    spending_trends_chart = pro_dashboard.getSpendingTrends(userID, year)

    categories = []
    category = {"name": None, "expenseMonth": 0,
                "expenseCount": 0, "amount": 0}
    spending_trends_table = {
        "January": [],
        "February": [],
        "March": [],
        "April": [],
        "May": [],
        "June": [],
        "July": [],
        "August": [],
        "September": [],
        "October": [],
        "November": [],
        "December": []
    }

    categories_active = pro_categories.getSpendCategories(userID)

    categories_inactive = pro_categories.getSpendCategories_Inactive(userID)

    for activeCategory in categories_active:
        category["name"] = activeCategory["name"]
        categories.append(category.copy())

    for inactiveCategory in categories_inactive:
        category["name"] = inactiveCategory["category"]
        categories.append(category.copy())

    for month in spending_trends_table.keys():
        spending_trends_table[month] = copy.deepcopy(categories)

    results = db.execute(
        "SELECT date_part('month', date(expensedate)) AS monthofcategoryexpense, category AS name, COUNT(category) AS count, SUM(amount) AS amount FROM expenses WHERE user_id = :usersID AND date_part('year', date(expensedate)) = :year GROUP BY date_part('month', date(expensedate)), category ORDER BY COUNT(category) DESC",
        {"usersID": userID, "year": year}).fetchall()

    spending_trends_table_query = convertSQLToDict(results)

    for categoryExpense in spending_trends_table_query:
        monthOfExpense = calendar.month_name[int(
            categoryExpense["monthofcategoryexpense"])]
        for category in spending_trends_table[monthOfExpense]:
            if category["name"] == categoryExpense["name"]:
                category["expenseMonth"] = categoryExpense["monthofcategoryexpense"]
                category["expenseCount"] = categoryExpense["count"]
                category["amount"] = categoryExpense["amount"]
                break
            else:
                continue

    numberOfCategories = len(categories)
    categoryTotal = 0
    for i in range(numberOfCategories):
        for month in spending_trends_table.keys():
            categoryTotal += spending_trends_table[month][i]["amount"]
        categories[i]["amount"] = categoryTotal
        categoryTotal = 0

    spendingTrendsReport = {"chart": spending_trends_chart,
                            "table": spending_trends_table, "categories": categories}

    return spendingTrendsReport


def generatePayersReport(userID, year=None):

    if not year:
        year = datetime.now().year
    results_payers = db.execute(
        "SELECT payer AS name, SUM(amount) AS amount FROM expenses WHERE user_id = :usersID AND date_part('year', date(expensedate)) = :year GROUP BY payer ORDER BY amount DESC", {"usersID": userID, "year": year}).fetchall()
    payers = convertSQLToDict(results_payers)

    results_nonExpensePayers = db.execute(
        "SELECT name FROM payers WHERE user_id = :usersID AND name NOT IN (SELECT payer FROM expenses WHERE expenses.user_id = :usersID AND date_part('year', date(expensedate)) = :year)", {"usersID": userID, "year": year}).fetchall()
    nonExpensePayers = convertSQLToDict(results_nonExpensePayers)

    for payer in nonExpensePayers:
        newPayer = {"name": payer["name"], "amount": 0}
        payers.append(newPayer)

    totalPaid = 0
    for payer in payers:
        totalPaid = totalPaid + payer["amount"]

    if totalPaid != 0:
        for payer in payers:
            payer["percentAmount"] = round((payer["amount"] / totalPaid) * 100)

        return payers
    else:
        return None
