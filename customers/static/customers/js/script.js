// Auto-dismiss Bootstrap alerts after a few seconds
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.alert').forEach(function (alertEl) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alertEl);
            bsAlert.close();
        }, 5000);
    });

    // Live client-side hint on the customer form: highlight invalid fields as the user types
    const nameField = document.getElementById('id_name');
    const phoneField = document.getElementById('id_phone');

    if (nameField) {
        nameField.addEventListener('input', function () {
            this.classList.toggle('is-invalid', this.value.trim().length > 0 && this.value.trim().length < 3);
        });
    }
    if (phoneField) {
        phoneField.addEventListener('input', function () {
            const valid = /^\+?\d{9,15}$/.test(this.value.trim());
            this.classList.toggle('is-invalid', this.value.trim().length > 0 && !valid);
        });
    }
});
