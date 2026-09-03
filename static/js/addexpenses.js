var rowCount;
var selectedRow;

function loadData(categoryData, dateData, payersData) {
    categories = JSON.parse(categoryData);
    today = dateData;
    payers = JSON.parse(payersData);
}

function addRow() {
    let newRow = "<tr> <td onclick='selectRow(this);'><br></td><td><textarea class='form-control-sm' name='description.' form='expenseForm' required maxlength='200'></textarea></td><td><select class='form-control-sm' name='category.' form='expenseForm' required'>"

    for (i = 0; i < categories.length; i++) {
        newRow += "<option value='" + categories[i].name + "'>" + categories[i].name + "</option>"
    }

    newRow += "</select></td><td><input type='date' class='form-control-sm' name='date.' form='expenseForm' required value='" + today + "'></td><td><select class='form-control-sm' name='payer.' form='expenseForm' required><option value='Self'>Self</option>"

    for (i = 0; i < payers.length; i++) {
        newRow += "<option value='" + payers[i].name + "'>" + payers[i].name + "</option>"
    }

    newRow += "</select></td><td><input type='text' class='form-control-sm' name='amount.' form='expenseForm' size='10' placeholder='$' maxlength='10' required pattern='(?=.*?\\d)^(([1-9]\\d{0,2}(\\d{3})*)|\\d+)?(\\.\\d{1,2})?$' title='Format must be currency value without dollar sign or commas e.g. 1, 2.50, 1500.75'></td></tr>"

    $("#expenseTable tbody").append(newRow);

    rowCount = countRows();
    updateTableElements(rowCount);
    updateRowButton();

    $("textarea[name='description." + rowCount + "']").focus()
}


function countRows() {
    let table = document.getElementById("expenseTable");
    let rows = table.children[1].childElementCount;
    return rows;
}

function updateTableElements(rowCount) {
    let table = document.getElementById("expenseTable");

    for (let i = 0; i < rowCount; i++) {
        table.children[1].children[i].children[0].innerHTML = String(i + 1) + " <i class='far fa-hand-pointer'></i>"

        for (let j = 0; j < 5; j++) {
            let oldName = table.children[1].children[i].children[j + 1].firstElementChild.name;
            let n = oldName.indexOf(".");
            let newName = oldName.substring(0, n + 1) + String(i + 1);
            table.children[1].children[i].children[j + 1].firstElementChild.setAttribute('name', newName);
        }
    }
}

function selectRow(cell) {
    let row = cell.parentNode;
    if (row.className == "table-danger") {
        $("tr").removeClass("table-danger");
        $("textarea").removeClass("selected");
        $("select").removeClass("selected");
        $("input").removeClass("selected");

        document.getElementById("btnDeleteRow").disabled = true;
    }

    else {
        $("tr").removeClass("table-danger");
        $("textarea").removeClass("selected");
        $("select").removeClass("selected");
        $("input").removeClass("selected");

        $(row).addClass("table-danger");

        if (countRows() > 1) {
            document.getElementById("btnDeleteRow").disabled = false;
        }
        else {
            document.getElementById("btnDeleteRow").disabled = true;
        }


        selectedRow = row;
    }
}

function removeRow(row) {
    $(row).remove();

    document.getElementById("btnDeleteRow").disabled = true;

    rowCount = countRows();
    updateTableElements(rowCount);
    updateRowButton();
}

function updateRowButton() {
    count = countRows();

    if (count < 10) {
        document.getElementById("btnNewRow").disabled = false;
    }

    else {
        document.getElementById("btnNewRow").disabled = true;
    }
}