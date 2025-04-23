// Form doğrulama fonksiyonları
function validateAmount(amount) {
    return amount > 0;
}

function validateDate(date) {
    return new Date(date) <= new Date();
}

// Para formatı
function formatCurrency(amount) {
    return new Intl.NumberFormat('tr-TR', {
        style: 'currency',
        currency: 'TRY'
    }).format(amount);
}

// Tarih formatı
function formatDate(date) {
    return new Date(date).toLocaleDateString('tr-TR');
}

// Toast bildirimi göster
function showToast(message, type = 'success') {
    const toast = `
        <div class="toast align-items-center text-white bg-${type} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    const toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        const container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(container);
    }
    
    const toastElement = document.createElement('div');
    toastElement.innerHTML = toast;
    document.getElementById('toastContainer').appendChild(toastElement.firstChild);
    
    const bsToast = new bootstrap.Toast(document.getElementById('toastContainer').lastChild);
    bsToast.show();
}

// Form verilerini JSON'a dönüştür
function formDataToJson(form) {
    const formData = new FormData(form);
    const data = {};
    for (let [key, value] of formData.entries()) {
        data[key] = value;
    }
    return data;
}

// AJAX hata işleme
function handleAjaxError(xhr) {
    let errorMessage = 'Bir hata oluştu';
    try {
        const response = JSON.parse(xhr.responseText);
        errorMessage = response.error || errorMessage;
    } catch (e) {
        console.error('JSON parse error:', e);
    }
    showToast(errorMessage, 'danger');
}

// Sayfa yüklendiğinde
document.addEventListener('DOMContentLoaded', function() {
    // Bootstrap tooltips'i etkinleştir
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Form doğrulama
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
    
    // Tarih alanları için maksimum değer ayarla
    const dateInputs = document.querySelectorAll('input[type="date"]');
    const today = new Date().toISOString().split('T')[0];
    dateInputs.forEach(input => {
        input.max = today;
    });
    
    // Tutar alanları için input mask
    const amountInputs = document.querySelectorAll('input[name="amount"]');
    amountInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/[^0-9.]/g, '');
            if (value.split('.').length > 2) value = value.replace(/\.+$/, '');
            e.target.value = value;
        });
    });
}); 