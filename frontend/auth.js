/**
 * Video Blog Content - Authentication Frontend Logic
 */

document.addEventListener('DOMContentLoaded', () => {

    // -----------------------------
    // Helper Functions
    // -----------------------------

    function setError(inputElement, errorElement, message) {
        if (!inputElement || !errorElement) return;

        inputElement.classList.add('is-invalid');
        errorElement.textContent = message;
        errorElement.classList.add('visible');
    }

    function clearError(inputElement, errorElement) {
        if (!inputElement || !errorElement) return;

        inputElement.classList.remove('is-invalid');
        errorElement.textContent = '';
        errorElement.classList.remove('visible');
    }

    function isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }


    // =====================================
    // REGISTER FORM
    // =====================================

    const registerForm = document.getElementById('register-form');

    if (registerForm) {

        const nameInput =
            document.getElementById('reg-name');

        const emailInput =
            document.getElementById('reg-email');

        const passwordInput =
            document.getElementById('reg-password');

        const confirmPasswordInput =
            document.getElementById('reg-confirm-password');


        const nameError =
            document.getElementById('reg-name-error');

        const emailError =
            document.getElementById('reg-email-error');

        const passwordError =
            document.getElementById('reg-password-error');

        const confirmPasswordError =
            document.getElementById('reg-confirm-password-error');


        // Remove errors while typing

        [
            nameInput,
            emailInput,
            passwordInput,
            confirmPasswordInput
        ].forEach(input => {

            if (input) {

                input.addEventListener('input', () => {

                    input.classList.remove('is-invalid');

                    const errorElement =
                        document.getElementById(
                            `${input.id}-error`
                        );

                    if (errorElement) {
                        errorElement.classList.remove('visible');
                    }

                });

            }

        });


        // Register Submit

        registerForm.addEventListener('submit', (e) => {

            e.preventDefault();

            let isValid = true;


            // Name validation

            if (!nameInput.value.trim()) {

                setError(
                    nameInput,
                    nameError,
                    'Name is required.'
                );

                isValid = false;

            } else {

                clearError(
                    nameInput,
                    nameError
                );

            }


            // Email validation

            if (!emailInput.value.trim()) {

                setError(
                    emailInput,
                    emailError,
                    'Email address is required.'
                );

                isValid = false;

            } else if (
                !isValidEmail(
                    emailInput.value.trim()
                )
            ) {

                setError(
                    emailInput,
                    emailError,
                    'Please enter a valid email address.'
                );

                isValid = false;

            } else {

                clearError(
                    emailInput,
                    emailError
                );

            }


            // Password validation

            if (!passwordInput.value) {

                setError(
                    passwordInput,
                    passwordError,
                    'Password is required.'
                );

                isValid = false;

            } else if (
                passwordInput.value.length < 6
            ) {

                setError(
                    passwordInput,
                    passwordError,
                    'Password must be at least 6 characters long.'
                );

                isValid = false;

            } else {

                clearError(
                    passwordInput,
                    passwordError
                );

            }


            // Confirm password validation

            if (!confirmPasswordInput.value) {

                setError(
                    confirmPasswordInput,
                    confirmPasswordError,
                    'Please confirm your password.'
                );

                isValid = false;

            } else if (
                passwordInput.value !==
                confirmPasswordInput.value
            ) {

                setError(
                    confirmPasswordInput,
                    confirmPasswordError,
                    'Passwords do not match.'
                );

                isValid = false;

            } else {

                clearError(
                    confirmPasswordInput,
                    confirmPasswordError
                );

            }


            // If everything is valid

            if (isValid) {

                const userData = {

                    name: nameInput.value.trim(),

                    email: emailInput.value.trim(),

                    isLoggedIn: false

                };


                // Save user using app.js store

                VideoBlogStore.updateUser(userData);


                // Success message

                sessionStorage.setItem(
                    'videoblog_flash_msg',
                    JSON.stringify({
                        text: 'Registration successful. Please login.',
                        type: 'success'
                    })
                );


                // Go to Login

                window.location.href = 'login.html';
            }

        });

    }


    // =====================================
    // LOGIN FORM
    // =====================================

    const loginForm =
        document.getElementById('login-form');

    if (loginForm) {

        const emailInput =
            document.getElementById('login-email');

        const passwordInput =
            document.getElementById('login-password');


        const emailError =
            document.getElementById('login-email-error');

        const passwordError =
            document.getElementById('login-password-error');


        // Remove errors while typing

        [
            emailInput,
            passwordInput
        ].forEach(input => {

            if (input) {

                input.addEventListener('input', () => {

                    input.classList.remove('is-invalid');

                    const errorElement =
                        document.getElementById(
                            `${input.id}-error`
                        );

                    if (errorElement) {
                        errorElement.classList.remove('visible');
                    }

                });

            }

        });


        // Login Submit

        loginForm.addEventListener('submit', (e) => {

            e.preventDefault();

            let isValid = true;


            // Email validation

            if (!emailInput.value.trim()) {

                setError(
                    emailInput,
                    emailError,
                    'Email address is required.'
                );

                isValid = false;

            } else if (
                !isValidEmail(
                    emailInput.value.trim()
                )
            ) {

                setError(
                    emailInput,
                    emailError,
                    'Please enter a valid email address.'
                );

                isValid = false;

            } else {

                clearError(
                    emailInput,
                    emailError
                );

            }


            // Password validation

            if (!passwordInput.value) {

                setError(
                    passwordInput,
                    passwordError,
                    'Password is required.'
                );

                isValid = false;

            } else {

                clearError(
                    passwordInput,
                    passwordError
                );

            }


            // Login success

            if (isValid) {

                const existingUser =
                    VideoBlogStore.getUser();


                VideoBlogStore.updateUser({

                    ...existingUser,

                    email: emailInput.value.trim(),

                    isLoggedIn: true

                });


                // Success message

                sessionStorage.setItem(
                    'videoblog_flash_msg',
                    JSON.stringify({
                        text:
                            'Welcome to your Video Blog Content Dashboard!',
                        type: 'success'
                    })
                );


                // Go to Dashboard

                window.location.href =
                    'dashboard.html';

            }

        });

    }

});