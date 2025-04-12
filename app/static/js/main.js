function confirmDelete(transactionId) {
    if (confirm('İşlemi silmek istediğinizden emin misiniz?')) {
        fetch(`/transactions/delete/${transactionId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
            }
        })
        .then(response => {
            if (response.ok) {
                window.location.reload();
            } else {
                alert('İşlem silinirken bir hata oluştu.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('İşlem silinirken bir hata oluştu.');
        });
    }
    return false;
}

// Sayfa yüklendiğinde çalışacak kodlar
document.addEventListener('DOMContentLoaded', function() {
    // Alert mesajlarını otomatik kapat
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.style.opacity = '0';
            setTimeout(function() {
                alert.remove();
            }, 500);
        }, 5000);
    });
}); 