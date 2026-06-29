// JavaScript Personalizado para la aplicación

// Confirmar cancelación de cita
document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        let alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            let closeButton = alert.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        });
    }, 5000);
});

// Función para formatear moneda
function formatCurrency(amount) {
    return new Intl.NumberFormat('es-DO', {
        style: 'currency',
        currency: 'DOP'
    }).format(amount);
}

// Función para validar teléfono
function validatePhone(phone) {
    const regex = /^[0-9]{10}$/;
    return regex.test(phone);
}