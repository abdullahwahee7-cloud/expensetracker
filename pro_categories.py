import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from helpers import convertSQLToDict

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


def getSpendCategories(userID):
    results = db.execute(
        "SELECT categories.name FROM usercategories INNER JOIN categories ON usercategories.category_id = categories.id WHERE usercategories.user_id = :usersID",
        {"usersID": userID}).fetchall()

    categories = convertSQLToDict(results)

    return categories


def getSpendCategories_Inactive(userID):
    results = db.execute(
        "SELECT category FROM expenses WHERE user_id = :usersID AND category NOT IN(SELECT categories.name FROM usercategories INNER JOIN categories ON categories.id = usercategories.category_id WHERE user_id = :usersID) GROUP BY category",
        {"usersID": userID}).fetchall()

    categories = convertSQLToDict(results)

    return categories


def getSpendCategoryLibrary():
    results = db.execute("SELECT id, name FROM categories").fetchall()

    categories = convertSQLToDict(results)

    return categories


def getSpendCategoryName(categoryID):
    name = db.execute(
        "SELECT name FROM categories WHERE id = :categoryID", {"categoryID": categoryID}).fetchone()[0]

    return name


def getBudgetsSpendCategories(userID):
    results = db.execute("SELECT budgets.name AS budgetname, categories.id AS categoryid, categories.name AS categoryname FROM budgetcategories INNER JOIN budgets on budgetcategories.budgets_id = budgets.id INNER JOIN categories on budgetcategories.category_id = categories.id WHERE budgets.user_id = :usersID ORDER BY budgets.name, categories.name",
                         {"usersID": userID}).fetchall()

    budgetsWithCategories = convertSQLToDict(results)

    return budgetsWithCategories


def getBudgetsFromSpendCategory(categoryID, userID):
    results = db.execute("SELECT budgets.id AS budgetid, budgets.name AS budgetname, categories.id AS categoryid, categories.name AS categoryname FROM budgetcategories INNER JOIN budgets on budgetcategories.budgets_id = budgets.id INNER JOIN categories on budgetcategories.category_id = categories.id WHERE budgets.user_id = :usersID AND budgetcategories.category_id = :categoryID ORDER BY budgets.name, categories.name", {
        "usersID": userID, "categoryID": categoryID}).fetchall()

    budgets = convertSQLToDict(results)

    return budgets


def updateSpendCategoriesInBudgets(budgets, oldCategoryID, newCategoryID):
    for budget in budgets:
        db.execute("UPDATE budgetcategories SET category_id = :newID WHERE budgets_id = :budgetID AND category_id = :oldID",
                   {"newID": newCategoryID, "budgetID": budget["budgetid"], "oldID": oldCategoryID})
    db.commit()


def deleteSpendCategoriesInBudgets(budgets, categoryID):
    for budget in budgets:
        db.execute("DELETE FROM budgetcategories WHERE budgets_id = :budgetID AND category_id = :categoryID",
                   {"budgetID": budget["budgetid"], "categoryID": categoryID})

    db.commit()


def generateSpendCategoriesWithBudgets(categories, categoryBudgets):
    categoriesWithBudgets = []

    for category in categories:
        categoryWithBudget = {"name": None, "budgets": []}
        categoryWithBudget["name"] = category["name"]

        for budget in categoryBudgets:
            if category["name"] == budget["categoryname"]:
                categoryWithBudget["budgets"].append(budget["budgetname"])

        categoriesWithBudgets.append(categoryWithBudget)

    return categoriesWithBudgets


def existsInLibrary(newName):
    row = db.execute(
        "SELECT * FROM categories WHERE LOWER(name) = :name", {"name": newName.lower()}).fetchone()

    if row:
        return True
    else:
        return False


def getCategoryID(categoryName, userID=None):
    if userID is None:
        categoryID = db.execute(
            "SELECT id FROM categories WHERE LOWER(name) = :name", {"name": categoryName.lower()}).fetchone()

        if not categoryID:
            return None
        else:
            return categoryID["id"]

    else:
        categoryID = db.execute(
            "SELECT categories.id FROM usercategories INNER JOIN categories ON usercategories.category_id = categories.id WHERE usercategories.user_id = :usersID AND LOWER(categories.name) = :name", {"usersID": userID, "name": categoryName.lower()}).fetchone()

        if not categoryID:
            return None
        else:
            return categoryID["id"]


def existsForUser(newName, userID):
    row = db.execute(
        "SELECT categories.id FROM usercategories INNER JOIN categories ON usercategories.category_id = categories.id WHERE usercategories.user_id = :usersID AND LOWER(categories.name) = :name", {"usersID": userID, "name": newName.lower()}).fetchone()

    if row:
        return True
    else:
        return False


def addCategory_DB(newName):
    categoryID = db.execute(
        "INSERT INTO categories (name) VALUES (:name) RETURNING id", {"name": newName}).fetchone()[0]
    db.commit()

    return categoryID


def addCategory_User(categoryID, userID):
    db.execute("INSERT INTO usercategories (user_id, category_id) VALUES (:usersID, :categoryID)",
               {"usersID": userID, "categoryID": categoryID})
    db.commit()


def deleteCategory_User(categoryID, userID):
    db.execute("DELETE FROM usercategories WHERE user_id = :usersID AND category_id = :categoryID",
               {"usersID": userID, "categoryID": categoryID})
    db.commit()


def updateExpenseCategoryNames(oldCategoryName, newCategoryName, userID):
    db.execute("UPDATE expenses SET category = :newName WHERE user_id = :usersID AND category = :oldName",
               {"newName": newCategoryName, "usersID": userID, "oldName": oldCategoryName})
    db.commit()


def renameCategory(oldCategoryID, newCategoryID, oldCategoryName, newCategoryName, userID):
    addCategory_User(newCategoryID, userID)
    deleteCategory_User(oldCategoryID, userID)
    budgets = getBudgetsFromSpendCategory(oldCategoryID, userID)

    if budgets:
        updateSpendCategoriesInBudgets(budgets, oldCategoryID, newCategoryID)

    updateExpenseCategoryNames(oldCategoryName, newCategoryName, userID)


def deleteCategory(categoryID, userID):
    budgets = getBudgetsFromSpendCategory(categoryID, userID)
    if budgets:
        deleteSpendCategoriesInBudgets(budgets, categoryID)

    deleteCategory_User(categoryID, userID)
