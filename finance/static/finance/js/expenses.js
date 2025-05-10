function editExpense(expenseId) {
    window.location.href = `/api/edit-transaction/${expenseId}/0/`;
}

function editEarning(earningId) {
    window.location.href = `/api/edit-transaction/${earningId}/1/`;
}

function deleteExpense(expenseId) {
    if (confirm('Are you sure you want to delete this expense?')) {
        window.location.href = `/api/delete-transaction/${expenseId}/0/`;
    }
}

function deleteEarning(earningId) {
    if (confirm('Are you sure you want to delete this earning?')) {
        window.location.href = `/api/delete-transaction/${earningId}/1/`;
    }
}