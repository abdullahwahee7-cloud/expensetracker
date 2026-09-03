
$(document).ready(function () {
    $('#expenses').DataTable({
        "pagingType": "full_numbers",
        "order": [[0, "desc"]],
        dom: 'Bfrtip',
        buttons: [
            'copy', 'csv', 'excel'
        ]
    });
});

var expenseDetailsBody;
var saveButton = $('#btnSave');
var deleteButton = $('#btnDelete');
var isDeleteUX = false;
$(document).ready(function () {
    $("#btnDelete, #btnDeleteCancel").click(function () {
        toggleDeleteUX();
        if (isDeleteUX == false) {
            isDeleteUX = true;
        }
        else {
            isDeleteUX = false;
        }
    });
});

function toggleDeleteUX() {
    if (expenseDetailsBody) {
        expenseDetailsBody.appendTo(".modal-body");
        expenseDetailsBody = null;
        $("#deleteDetails").hide();
        saveButton.show();
        deleteButton.show();

    } else {
        expenseDetailsBody = $("#newExpenseDetails").detach();
        saveButton.hide();
        deleteButton.hide();
        $("#deleteDetails").show();
    }
}

$('#updateModal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget) 
    var description = button.data('description') 
    var category = button.data('category') 
    var date = button.data('date') 
    var payer = button.data('payer') 
    var amount = button.data('amount') 
    var submitTime = button.data('submittime')
    var modal = $(this)
    modal.find('.modal-title').text("Update Expense Record")

    modal.find('#oldDescription').val(description)
    modal.find('#oldCategory').val(category)
    modal.find('#oldDate').val(date)
    modal.find('#oldPayer').val(payer)
    modal.find('#oldAmount').val(amount)
    modal.find('#submitTime').val(submitTime)

    modal.find('#description').val(description)
    modal.find('#category').val(category)
    modal.find('#date').val(date)
    modal.find('#payer').val(payer)
    modal.find('#amount').val(amount)
})

$('#updateModal').on('hidden.bs.modal', function () {
    $('#description').val('')
    $('#category').val('')
    $('#date').val('')
    $('#payer').val('')
    $('#amount').val('')

    if (isDeleteUX == true) {
        toggleDeleteUX();
        isDeleteUX = false;
    }
})
