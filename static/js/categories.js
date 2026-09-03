
$('#collapseCategory').on('shown.bs.collapse', function () {
    $('#name').trigger('focus')
})

$('#collapseCategory').on('hidden.bs.collapse', function () {
    $('#name').val('')
})

$('#renameModal').on('show.bs.modal', function (event) {
    let button = $(event.relatedTarget) 
    let category = button.data('category') 
    let budgets_string = button.data('budgets')
    let budgets = budgets_string.split(";")
    let modal = $(this)
    modal.find('.modal-title').text("Rename category '" + category + "'")
    modal.find('#oldname').val(category)
    msg = modal.find('#renameAlert_msg');
    msg_budgets = modal.find('#renameAlert_budgets');

    if (budgets.length > 1) {
        msg[0].innerText = "The following budgets will have the category name updated:";
        for (i = 0; i < budgets.length; i++) {

            if (budgets[i] != '') {
                msg_budgets[0].innerHTML += "<li>" + budgets[i] + "</li>";
            }
        }
    }
    else {
        msg[0].innerText = "No budgets will be affected by this change";
    }
})

$('#renameModal').on('hidden.bs.modal', function () {
    $('#newname').val('');
    $('#renameAlert_budgets').empty();
})

$('#deleteModal').on('show.bs.modal', function (event) {
    let button = $(event.relatedTarget) 
    let category = button.data('category') 
    let budgets_string = button.data('budgets') 
    let budgets = budgets_string.split(";")
    let modal = $(this)
    modal.find('.modal-title').text("Delete category '" + category + "'")
    modal.find('#delete').val(category)
    msg = modal.find('#deleteAlert_msg');
    msg_budgets = modal.find('#deleteAlert_budgets');
    if (budgets.length > 1) {
        msg[0].innerText = "The following budgets will have the category name deleted. Make sure you update your budgets after deleting the category!";
        for (i = 0; i < budgets.length; i++) {
            if (budgets[i] != '') {
                msg_budgets[0].innerHTML += "<li>" + budgets[i] + "</li>";
            }
        }
    }
    else {
        msg[0].innerText = "No budgets will be affected by this change";
    }
})

$('#deleteModal').on('hidden.bs.modal', function () {
    $('#deleteAlert_budgets').empty();
})