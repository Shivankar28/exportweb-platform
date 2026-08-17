// Multi-step Seller Registration Form Wizard Logic
document.addEventListener('DOMContentLoaded', function () {
    const wizardForm = document.getElementById('sellerRegistrationForm');
    if (!wizardForm) return;

    let currentStep = 1;
    const totalSteps = 4;

    const stepElements = document.querySelectorAll('.wizard-tab-content');
    const stepIndicators = document.querySelectorAll('.step-wizard-step');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const submitBtn = document.getElementById('submitBtn');

    function showStep(step) {
        stepElements.forEach((el, idx) => {
            if (idx + 1 === step) {
                el.classList.remove('d-none');
            } else {
                el.classList.add('d-none');
            }
        });

        stepIndicators.forEach((indicator, idx) => {
            const stepNum = idx + 1;
            indicator.classList.remove('active', 'completed');
            if (stepNum === step) {
                indicator.classList.add('active');
            } else if (stepNum < step) {
                indicator.classList.add('completed');
            }
        });

        // Navigation buttons
        if (step === 1) {
            prevBtn.classList.add('d-none');
        } else {
            prevBtn.classList.remove('d-none');
        }

        if (step === totalSteps) {
            nextBtn.classList.add('d-none');
            submitBtn.classList.remove('d-none');
        } else {
            nextBtn.classList.remove('d-none');
            submitBtn.classList.add('d-none');
        }

        window.scrollTo({ top: 100, behavior: 'smooth' });
    }

    function validateStep(step) {
        const currentTab = document.getElementById(`step-${step}`);
        if (!currentTab) return true;

        const requiredInputs = currentTab.querySelectorAll('[required]');
        let isValid = true;

        requiredInputs.forEach(input => {
            if (!input.checkValidity()) {
                input.reportValidity();
                isValid = false;
            }
        });

        // Password matching validation on step 1
        if (step === 1) {
            const pass = document.getElementById('password');
            const confirmPass = document.getElementById('confirm_password');
            if (pass && confirmPass && pass.value !== confirmPass.value) {
                confirmPass.setCustomValidity('Passwords do not match.');
                confirmPass.reportValidity();
                isValid = false;
            } else if (confirmPass) {
                confirmPass.setCustomValidity('');
            }
        }

        return isValid;
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', function () {
            if (validateStep(currentStep)) {
                if (currentStep < totalSteps) {
                    currentStep++;
                    showStep(currentStep);
                }
            }
        });
    }

    if (prevBtn) {
        prevBtn.addEventListener('click', function () {
            if (currentStep > 1) {
                currentStep--;
                showStep(currentStep);
            }
        });
    }

    showStep(currentStep);
});
