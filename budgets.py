import os
import re
import categories as pro_categories
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from datetime import datetime
from helpers import convertSQLToDict

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


def getBudgets(userID):
    results = db.execute(
        "SELECT id, name, year, amount FROM budgets WHERE user_id = :usersID ORDER BY name ASC", {"usersID": userID}).fetchall()

    budgets_query = convertSQLToDict(results)

    if budgets_query:
        budgets = {budget['year']: [] for budget in budgets_query}

        for budget in budgets_query:
            budgets[budget['year']].append(
                {'amount': budget['amount'], 'id': budget['id'], 'name': budget['name']})

        return budgets
    else:
        return None


def getBudgetByID(budgetID, userID):
    results = db.execute(
        "SELECT name, amount, year, id FROM budgets WHERE user_id = :usersID AND id = :budgetID", {"usersID": userID, "budgetID": budgetID}).fetchall()

    budget = convertSQLToDict(results)

    return budget[0]


def getTotalBudgetedByYear(userID, year=None):

    if not year:
        year = datetime.now().year

    amount = db.execute(
        "SELECT SUM(amount) AS amount FROM budgets WHERE user_id = :usersID AND year = :year", {"usersID": userID, "year": year}).fetchone()[0]

    if amount is None:
        return 0
    else:
        return amount


def generateBudgetFromForm(formData):
    budget = {"name": None, "year": None, "amount": None, "categories": []}
    counter = 0

    for key, value in formData:
        counter += 1
        if counter <= 3:
            if key == "name":
                validBudgetName = re.search(r"^([a-zA-Z0-9_\s\-]*)$", value)
                if validBudgetName:
                    budget[key] = value.strip()
                else:
                    return {"apology": "Please enter a budget name without special characters except underscores, spaces, and hyphens"}
            elif key == "year":
                budgetYear = int(value)
                currentYear = datetime.now().year

                if 2020 <= budgetYear <= currentYear:
                    budget[key] = budgetYear
                else:
                    return {"apology": f"Please select a valid budget year: 2020 through {currentYear}"}
            else:
                amount = float(value.strip())
                budget[key] = amount
        else:
            if value == '':
                continue

            cleanKey = key.split(".")

            category = {"name": None, "percent": None}
            if cleanKey[0] == "categories":
                category["name"] = value.strip()

                percent = (int(formData[counter][1].strip()) / 100)
                category["percent"] = percent

                budget[cleanKey[0]].append(category)
            elif cleanKey[0] == "categoryPercent":
                pass
            else:
                return {"apology": "Only categories and their percentage of the overall budget are allowed to be stored"}

    return budget


def createBudget(budget, userID):
    uniqueBudgetName = isUniqueBudgetName(budget["name"], None, userID)
    if not uniqueBudgetName:
        return {"apology": "Please enter a unique budget name, not a duplicate."}

    newBudgetID = db.execute("INSERT INTO budgets (name, year, amount, user_id) VALUES (:budgetName, :budgetYear, :budgetAmount, :usersID) RETURNING id",
                             {"budgetName": budget["name"], "budgetYear": budget["year"], "budgetAmount": budget["amount"], "usersID": userID}).fetchone()[0]
    db.commit()

    categoryIDS = getBudgetCategoryIDS(budget["categories"], userID)

    addCategory(newBudgetID, categoryIDS)

    return budget


def addCategory(budgetID, categoryIDS):
    for categoryID in categoryIDS:
        db.execute("INSERT INTO budgetCategories (budgets_id, category_id, amount) VALUES (:budgetID, :categoryID, :percentAmount)",
                   {"budgetID": budgetID, "categoryID": categoryID["id"], "percentAmount": categoryID["amount"]})
    db.commit()

def updateBudget(oldBudgetName, budget, userID):
    oldBudgetID = getBudgetID(oldBudgetName, userID)

    uniqueBudgetName = isUniqueBudgetName(
        budget["name"], oldBudgetID, userID)
    if not uniqueBudgetName:
        return {"apology": "Please enter a unique budget name, not a duplicate."}

    db.execute("UPDATE budgets SET name = :budgetName, year = :budgetYear, amount = :budgetAmount WHERE id = :oldBudgetID AND user_id = :usersID",
               {"budgetName": budget["name"], "budgetYear": budget["year"], "budgetAmount": budget["amount"], "oldBudgetID": oldBudgetID, "usersID": userID})
    db.commit()

    db.execute("DELETE FROM budgetCategories WHERE budgets_id = :oldBudgetID",
               {"oldBudgetID": oldBudgetID})
    db.commit()

    categoryIDS = getBudgetCategoryIDS(budget["categories"], userID)

    addCategory(oldBudgetID, categoryIDS)

    return budget


def getBudgetCategoryIDS(categories, userID):
    categoryIDS = []
    for category in categories:
        categoryID = db.execute("SELECT categories.id FROM userCategories INNER JOIN categories ON userCategories.category_id = categories.id WHERE userCategories.user_id = :usersID AND categories.name = :categoryName",
                                {"usersID": userID, "categoryName": category["name"]}).fetchone()[0]

        id_amount = {"id": None, "amount": None}
        id_amount["id"] = categoryID
        id_amount["amount"] = category["percent"]

        categoryIDS.append(id_amount)

    return categoryIDS


def deleteBudget(budgetName, userID):
    budgetID = getBudgetID(budgetName, userID)

    if budgetID:
        db.execute("DELETE FROM budgetCategories WHERE budgets_id = :budgetID",
                   {"budgetID": budgetID})
        db.commit()

        db.execute("DELETE FROM budgets WHERE id = :budgetID",
                   {"budgetID": budgetID})
        db.commit()

        return budgetName
    else:
        return None


def getBudgetID(budgetName, userID):
    budgetID = db.execute("SELECT id FROM budgets WHERE user_id = :usersID AND name = :budgetName",
                          {"usersID": userID, "budgetName": budgetName}).fetchone()[0]

    if not budgetID:
        return None
    else:
        return budgetID


def isUniqueBudgetName(budgetName, budgetID, userID):
    if budgetID == None:
        results = db.execute(
            "SELECT name FROM budgets WHERE user_id = :usersID", {"usersID": userID}).fetchall()
        existingBudgets = convertSQLToDict(results)
    else:
        results = db.execute(
            "SELECT name FROM budgets WHERE user_id = :usersID AND NOT id = :oldBudgetID", {"usersID": userID, "oldBudgetID": budgetID}).fetchall()
        existingBudgets = convertSQLToDict(results)

    isUniqueName = True
    for budget in existingBudgets:
        if budgetName.lower() == budget["name"].lower():
            isUniqueName = False
            break

    if isUniqueName:
        return True
    else:
        return False


def getUpdatableBudget(budget, userID):

    categories = pro_categories.getSpendCategories(userID)

    results = db.execute("SELECT DISTINCT categories.name, budgetCategories.amount FROM budgetCategories INNER JOIN categories ON budgetCategories.category_id = categories.id INNER JOIN budgets ON budgetCategories.budgets_id = budgets.id WHERE budgets.id = :budgetsID",
                         {"budgetsID": budget["id"]}).fetchall()
    budgetCategories = convertSQLToDict(results)

    budget["categories"] = []

    for category in categories:
        for budgetCategory in budgetCategories:
            if category["name"] == budgetCategory["name"]:
                amount = round(budgetCategory["amount"] * 100)
                budget["categories"].append(
                    {"name": category["name"], "amount": amount, "checked": True})
                break
        else:
            budget["categories"].append(
                {"name": category["name"], "amount": None, "checked": False})

    return budget
