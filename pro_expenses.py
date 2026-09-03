import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from datetime import datetime
from helpers import convertSQLToDict

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def addExpenses(formData, userID):
    expenses = []
    expense = {"description": None, "category": None,
               "date": None, "amount": None, "payer": None}

    if "." not in formData[0][0]:
        for key, value in formData:
            expense[key] = value.strip()

        expense["amount"] = float(expense["amount"])
        expenses.append(expense)

    else:
        counter = 0
        for key, value in formData:
            cleanKey = key.split(".")
            expense[cleanKey[0]] = value.strip()
            counter += 1
            if counter % 5 == 0:
                expense["amount"] = float(expense["amount"])
                expenses.append(expense.copy())

    for expense in expenses:
        now = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        db.execute("INSERT INTO expenses (description, category, expenseDate, amount, payer, submitTime, user_id) VALUES (:description, :category, :expenseDate, :amount, :payer, :submitTime, :usersID)",
                   {"description": expense["description"], "category": expense["category"], "expenseDate": expense["date"], "amount": expense["amount"], "payer": expense["payer"], "submitTime": now, "usersID": userID})
    db.commit()

    return expenses

def getHistory(userID):
    results = db.execute("SELECT description, category, expenseDate AS date, payer, amount, submitTime FROM expenses WHERE user_id = :usersID ORDER BY id ASC",
                         {"usersID": userID}).fetchall()

    history = convertSQLToDict(results)

    return history

def getExpense(formData, userID):
    expense = {"description": None, "category": None,
               "date": None, "amount": None, "payer": None, "submitTime": None, "id": None}
    expense["description"] = formData.get("oldDescription").strip()
    expense["category"] = formData.get("oldCategory").strip()
    expense["date"] = formData.get("oldDate").strip()
    expense["amount"] = formData.get("oldAmount").strip()
    expense["payer"] = formData.get("oldPayer").strip()
    expense["submitTime"] = formData.get("submitTime").strip()

    expense["amount"] = float(
        expense["amount"].replace("$", "").replace(",", ""))

    expenseID = db.execute("SELECT id FROM expenses WHERE user_id = :usersID AND description = :oldDescription AND category = :oldCategory AND expenseDate = :oldDate AND amount = :oldAmount AND payer = :oldPayer AND submitTime = :oldSubmitTime",
                           {"usersID": userID, "oldDescription": expense["description"], "oldCategory": expense["category"], "oldDate": expense["date"], "oldAmount": expense["amount"], "oldPayer": expense["payer"], "oldSubmitTime": expense["submitTime"]}).fetchone()

    if expenseID:
        expense["id"] = expenseID[0]
    else:
        expense["id"] = None

    return expense


def deleteExpense(expense, userID):
    result = db.execute("DELETE FROM expenses WHERE user_id = :usersID AND id = :oldExpenseID",
                        {"usersID": userID, "oldExpenseID": expense["id"]})
    db.commit()

    return result

def updateExpense(oldExpense, formData, userID):
    expense = {"description": None, "category": None,
               "date": None, "amount": None, "payer": None}
    expense["description"] = formData.get("description").strip()
    expense["category"] = formData.get("category").strip()
    expense["date"] = formData.get("date").strip()
    expense["amount"] = formData.get("amount").strip()
    expense["payer"] = formData.get("payer").strip()

    expense["amount"] = float(expense["amount"])

    hasChanges = False
    for key, value in oldExpense.items():
        if key == "submitTime":
            break
        else:
            if oldExpense[key] != expense[key]:
                hasChanges = True
                break
    if hasChanges is False:
        return None

    now = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    result = db.execute("UPDATE expenses SET description = :newDescription, category = :newCategory, expenseDate = :newDate, amount = :newAmount, payer = :newPayer, submitTime = :newSubmitTime WHERE id = :existingExpenseID AND user_id = :usersID",
                        {"newDescription": expense["description"], "newCategory": expense["category"], "newDate": expense["date"], "newAmount": expense["amount"], "newPayer": expense["payer"], "newSubmitTime": now, "existingExpenseID": oldExpense["id"], "usersID": userID}).rowcount
    db.commit()

    if result:
        expenses = []
        expenses.append(expense)
        return expenses
    else:
        return None
