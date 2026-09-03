
$(document).ready(function () {
    loadBudgetYears();
    calculateEstimates();
});

function loadBudgetYears() {
    let years = document.getElementById("year")
    let currentYear = new Date().getFullYear();
    let updatableYear = document.getElementById('year').getAttribute('data-year')

    for (let i = currentYear; i >= 2020; i--) {
        let option = document.createElement("option");
        option.innerHTML = i;
        option.value = i;

        if (updatableYear !== null) {
            if (i.toString() == updatableYear) {
                option.selected = true;
            }
        }
        else {
            if (i == currentYear) {
                option.selected = true;
            }
        }
        years.appendChild(option);
    }
}

function fillBudgetAmount(amount) {
    document.getElementById('amount').value = amount;
    calculateEstimates();
}

var checkBoxes = $('.custom-control-input');
checkBoxes.change(function () {
    $('#btnSaveBudget').prop('disabled', checkBoxes.filter(':checked').length < 1);
});
$('.custom-control-input').change();

function calculateEstimates() {
    let budget = document.getElementById("amount").value;
    const weekly = (budget / 52)
    const monthly = (budget / 12)
    document.getElementById("weekly").innerHTML = "Weekly amount: " + new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(weekly);
    document.getElementById("monthly").innerHTML = "Monthly amount: " + new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(monthly);

    let checkedCategories = getAllCheckedCategories()
    if (checkedCategories) {
        for (i = 0; i < checkedCategories.length; i++) {
            percentInput = checkedCategories[i].nextElementSibling.nextElementSibling.nextElementSibling;
            calculateCategories(percentInput)
        }
    }
}

function displayCategoryAmounts(category) {
    let categoryPercentageInput = category.nextElementSibling.nextElementSibling.nextElementSibling;
    let percentageLabel = categoryPercentageInput.nextElementSibling;
    let percentageAmountLabel = percentageLabel.nextElementSibling;

    if (category.checked == true) {
        categoryPercentageInput.type = "number";
        categoryPercentageInput.hidden = false;
        categoryPercentageInput.required = true;
        categoryPercentageInput.readOnly = false;
        percentageLabel.hidden = false;
        percentageAmountLabel.hidden = false;
    }
    else {
        categoryPercentageInput.type = "hidden";
        categoryPercentageInput.hidden = true;
        categoryPercentageInput.required = false;
        categoryPercentageInput.readOnly = true;
        percentageLabel.hidden = true;
        percentageAmountLabel.hidden = true;
    }
}

$(function () {
    $('.categoryPercent').keypress(function (e) {
        let allow_char = [48, 49, 50, 51, 52, 53, 54, 55, 56, 57];
        if (allow_char.indexOf(e.which) !== -1) {
            return true;
        }
        else {
            return false;
        }
    });
});

function getAllCheckedCategories() {
    var categories = $('.custom-control-input');

    var allCheckedCategories = [];
    for (i = 0; i < categories.length; i++) {
        if (categories[i].checked) {
            allCheckedCategories.push(categories[i]);
        }
    }

    if (allCheckedCategories.length > 0) {
        return allCheckedCategories;
    }
    else {
        return false;
    }
}

function calculateCategories(percentInput) {
    let categoryBudget = document.getElementById("amount").value;
    const categoryWeekly = (categoryBudget / 52);
    const categoryMonthly = (categoryBudget / 12);
    let categoryLabel = percentInput.nextElementSibling.nextElementSibling;

    if (percentInput.value > 0 && percentInput.value <= 100) {
        categoryLabel.innerHTML = "Total amount: " + new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(categoryBudget * (percentInput.value / 100)) + "<br>Weekly amount: " + new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(categoryWeekly * (percentInput.value / 100)) + "<br>Monthly amount: " + new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(categoryMonthly * (percentInput.value / 100));
        document.getElementById("btnSaveBudget").disabled = false;
    }
    else {
        categoryLabel.innerHTML = "⚠ Enter a percentage between 1 to 100, or uncheck the category ⚠";
        document.getElementById("btnSaveBudget").disabled = true;
    }
}

function validateCategories() {
    var allCheckBoxes = $('.custom-control-input');
    var checkBoxesChecked = [];
    for (i = 0; i < allCheckBoxes.length; i++) {
        let checkbox = allCheckBoxes[i];
        if (checkbox.checked) {
            checkBoxesChecked.push(checkbox);
        }
    }

    var sum = 0;
    for (i = 0; i < checkBoxesChecked.length; i++) {
        let percent = checkBoxesChecked[i].nextElementSibling.nextElementSibling.nextElementSibling;
        sum += parseInt(percent.value) || 0;
    }

    var submitAlert = document.getElementById('submitAlert');
    if (sum != 100) {
        submitAlert.innerHTML = "Your spend categories budgets add up to " + sum + "% and it must be equal to 100%";
        submitAlert.hidden = false;
        event.preventDefault();
    }
}