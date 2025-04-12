// İşlem silme işlemi
document.addEventListener('DOMContentLoaded', function() {
    const deleteButtons = document.querySelectorAll('.delete-btn');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            if (confirm('Bu işlemi silmek istediğinizden emin misiniz?')) {
                const transactionId = this.dataset.transactionId;
                fetch(`/transactions/delete/${transactionId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        location.reload();
                    } else {
                        alert('İşlem silinirken bir hata oluştu.');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('İşlem silinirken bir hata oluştu.');
                });
            }
        });
    });
}); 