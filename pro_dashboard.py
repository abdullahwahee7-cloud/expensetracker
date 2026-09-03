import os
import calendar
import pro_budgets
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from helpers import convertSQLToDict
from datetime import datetime

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


def getTotalSpend_Year(userID):
    results = db.execute(
        "SELECT SUM(amount) AS expenses_year FROM expenses WHERE user_id = :usersID AND date_part('year', date(expensedate)) = date_part('year', CURRENT_DATE)",
        {"usersID": userID}).fetchall()

    totalSpendYear = convertSQLToDict(results)

    return totalSpendYear[0]['expenses_year']


def getTotalSpend_Month(userID):
    results = db.execute(
        "SELECT SUM(amount) AS expenses_month FROM expenses WHERE user_id = :usersID AND date_part('year', date(expensedate)) = date_part('year', CURRENT_DATE) AND date_part('month', date(expensedate)) = date_part('month', CURRENT_DATE)",
        {"usersID": userID}).fetchall()

    totalSpendMonth = convertSQLToDict(results)

    return totalSpendMonth[0]['expenses_month']


def getTotalSpend_Week(userID):
    results = db.execute(
        "SELECT SUM(amount) AS expenses_week FROM expenses WHERE user_id = :usersID AND date_part('year', date(expensedate)) = date_part('year', CURRENT_DATE) AND date_part('week', date(expensedate)) = date_part('week', CURRENT_DATE)",
        {"usersID": userID}).fetchall()

    totalSpendWeek = convertSQLToDict(results)

    return totalSpendWeek[0]['expenses_week']


def getLastFiveExpenses(userID):
    results = db.execute(
        "SELECT description, category, expenseDate, payer, amount FROM expenses WHERE user_id = :usersID ORDER BY id DESC LIMIT 5", {"usersID": userID}).fetchall()

    lastFiveExpenses = convertSQLToDict(results)

    if lastFiveExpenses:
        return lastFiveExpenses
    else:
        return None


def getBudgets(userID, year=None):
    budgets = []
    budget = {"name": None, "amount": 0, "spent": 0, "remaining": 0}

    if not year:
        year = datetime.now().year

    budgets_query = pro_budgets.getBudgets(userID)
    if budgets_query and year in budgets_query:
        for record in budgets_query[year]:
            budgetID = record["id"]
            budget["name"] = record["name"]
            budget["amount"] = record["amount"]

            results = db.execute(
                "SELECT SUM(amount) AS spent FROM expenses WHERE user_id = :usersID AND date_part('year', date(expensedate)) = :year AND category IN (SELECT categories.name FROM budgetcategories INNER JOIN categories on budgetcategories.category_id = categories.id WHERE budgetcategories.budgets_id = :budgetID)",
                {"usersID": userID, "year": year, "budgetID": budgetID}).fetchall()
            budget_TotalSpent = convertSQLToDict(results)

            if (budget_TotalSpent[0]["spent"] == None):
                budget["spent"] = 0
            else:
                budget["spent"] = budget_TotalSpent[0]["spent"]

            if (budget["spent"] > budget["amount"]):
                budget["remaining"] = 0
            else:
                budget["remaining"] = budget["amount"] - budget["spent"]

            budgets.append(budget.copy())

        return budgets

    else:
        return None


def getLastFourWeekNames():
    results = db.execute("SELECT date_trunc('week', CURRENT_DATE)::date AS startofweek, (date_trunc('week', CURRENT_DATE) + interval '6 day')::date AS endofweek UNION SELECT date_trunc('week', CURRENT_DATE - interval '1 week')::date AS startofweek, (date_trunc('week', CURRENT_DATE - interval '1 week') + interval '6 day')::date AS endofweek UNION SELECT date_trunc('week', CURRENT_DATE - interval '2 week')::date AS startofweek, (date_trunc('week', CURRENT_DATE - interval '2 week') + interval '6 day')::date AS endofweek UNION SELECT date_trunc('week', CURRENT_DATE - interval '3 week')::date AS startofweek, (date_trunc('week', CURRENT_DATE - interval '3 week') + interval '6 day')::date AS endofweek ORDER BY startofweek ASC").fetchall()

    weekNames = convertSQLToDict(results)

    return weekNames


def getWeeklySpending(weekNames, userID):
    weeklySpending = []
    week = {"startOfWeek": None, "endOfWeek": None, "amount": None}

    for name in weekNames:
        week["endOfWeek"] = name['endofweek'].strftime('%b %d')
        week["startOfWeek"] = name['startofweek'].strftime('%b %d')
        results = db.execute(
            "SELECT SUM(amount) AS amount FROM expenses WHERE user_id = :usersID AND date_part('year', date(expensedate)) = date_part('year', date(:weekName)) AND date_part('week', date(expensedate)) = date_part('week',date(:weekName))",
            {"usersID": userID, "weekName": str(name["endofweek"])}).fetchall()
        weekSpending = convertSQLToDict(results)

        if weekSpending[0]["amount"] == None:
            week["amount"] = 0
        else:
            week["amount"] = weekSpending[0]["amount"]

        weeklySpending.append(week.copy())

    hasExpenses = False
    for record in weeklySpending:
        if record["amount"] != 0:
            hasExpenses = True
            break
    if hasExpenses is False:
        weeklySpending.clear()

    return weeklySpending


def getMonthlySpending(userID, year=None):
    spending_month = []
    month = {"name": None, "amount": None}

    if not year:
        year = datetime.now().year

    results = db.execute(
        "SELECT date_part('month', date(expensedate)) AS month, SUM(amount) AS amount FROM expenses WHERE user_id = :usersID AND date_part('year', date(expensedate)) = :year GROUP BY date_part('month', date(expensedate)) ORDER BY month",
        {"usersID": userID, "year": year}).fetchall()
    spending_month_query = convertSQLToDict(results)

    for record in spending_month_query:
        month["name"] = calendar.month_abbr[int(record["month"])]
        month["amount"] = record["amount"]

        spending_month.append(month.copy())

    return spending_month


def getSpendingTrends(userID, year=None):

    spending_trends = []
    categoryTrend = {"name": None, "proportionalAmount": None,
                     "totalSpent": None, "totalCount": None}

    if not year:
        year = datetime.now().year

    results = db.execute("SELECT category, COUNT(category) as count, SUM(amount) as amount FROM expenses WHERE user_id = :usersID AND date_part('year', date(expensedate)) = :year GROUP BY category ORDER BY COUNT(category) DESC",
                         {"usersID": userID, "year": year}).fetchall()
    categories = convertSQLToDict(results)

    totalSpent = 0
    for categoryExpense in categories:
        totalSpent += categoryExpense["amount"]

    for category in categories:
        proportionalAmount = round((category["amount"] / totalSpent) * 100)
        if (proportionalAmount < 1):
            continue
        else:
            categoryTrend["name"] = category["category"]
            categoryTrend["proportionalAmount"] = proportionalAmount
            categoryTrend["totalSpent"] = category["amount"]
            categoryTrend["totalCount"] = category["count"]
            spending_trends.append(categoryTrend.copy())

    return spending_trends
