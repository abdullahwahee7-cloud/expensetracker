// functions of 'Your Account'

$('#collapsePayer').on('shown.bs.collapse', function () {
    $('#payerName').trigger('focus');
})

$('#collapsePayer').on('hidden.bs.collapse', function () {
    $('#payerName').val('');
})

$("#btnAddPayer").click(function (e) {
    $("#collapsePayers").collapse("hide");
});

$("#btnManagePayers").click(function (e) {
    $("#collapsePayer").collapse("hide");
});


$('#renameModal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget); 
    var payer = button.data('payer'); 
    var modal = $(this);
    modal.find('.modal-title').text("Rename payer '" + payer + "'");
    modal.find('#oldpayer').val(payer);
})

$('#renameModal').on('hidden.bs.modal', function () {
    $('#newpayer').val('');
})

$('#deleteModal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget); // Button that triggered the modal
    var payer = button.data('payer'); // Extract info from data-* attributes
    var modal = $(this);
    modal.find('.modal-title').text("Delete payer '" + payer + "'");
    modal.find('#delete').val(payer);
})

$('#collapseIncome').on('shown.bs.collapse', function () {
    $('#income').trigger('focus');
})

$('#collapseIncome').on('hidden.bs.collapse', function () {
    $('#income').val('');
})

$('#collapsePassword').on('shown.bs.collapse', function () {
    $('#currentPassword').trigger('focus');
})

$('#collapsePassword').on('hidden.bs.collapse', function () {
    $('#currentPassword').val('');
    $('#newPassword').val('');
})
