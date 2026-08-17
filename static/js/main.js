// Global UI Interactivity JavaScript
document.addEventListener('DOMContentLoaded', function () {
    // Auto dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Image preview helper for file inputs
    const imageInputs = document.querySelectorAll('.image-preview-input');
    imageInputs.forEach(function (input) {
        input.addEventListener('change', function (e) {
            const previewTargetId = input.getAttribute('data-preview');
            const previewTarget = document.getElementById(previewTargetId);
            if (previewTarget && input.files && input.files[0]) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    previewTarget.src = e.target.result;
                    previewTarget.classList.remove('d-none');
                }
                reader.readAsDataURL(input.files[0]);
            }
        });
    });
});
