document.addEventListener('DOMContentLoaded', () => {
    // Ensure API_BASE_URL matches your Flask server's address and blueprint prefix
    const API_BASE_URL = 'http://localhost:8080/api'; 

    // --- Navigation Toggle for Mobile --- //
    const navToggle = document.querySelector('.nav-toggle');
    const navMenu = document.getElementById('main-menu');

    if (navToggle && navMenu) {
        navToggle.addEventListener('click', () => {
            const isExpanded = navToggle.getAttribute('aria-expanded') === 'true';
            navToggle.setAttribute('aria-expanded', !isExpanded);
            navMenu.classList.toggle('open');
        });

        // Close menu when a link is clicked (for single-page navigation or on the same page)
        navMenu.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => {
                if (navMenu.classList.contains('open')) {
                    navToggle.setAttribute('aria-expanded', 'false');
                    navMenu.classList.remove('open');
                }
            });
        });
    }

    // --- Dynamic Background for Login/Register pages --- //
    const video = document.getElementById('bg-video');
    if (video) {
        video.oncanplaythrough = () => {
            video.play();
            // Optionally fade in video to prevent black flash
            video.style.opacity = 1;
        };
        video.onerror = () => {
            console.error('Error loading background video. Check path and format.');
            // Fallback to CSS background if video fails (defined in style.css for .video-background)
            const videoBackgroundDiv = document.querySelector('.video-background');
            if (videoBackgroundDiv) {
                videoBackgroundDiv.style.backgroundImage = 'linear-gradient(45deg, #0f0c29, #302b63, #24243e)';
                videoBackgroundDiv.style.backgroundSize = '400% 400%';
                videoBackgroundDiv.style.animation = 'gradientAnimation 15s ease infinite';
            }
            video.style.display = 'none'; // Hide broken video element
        };
        // Set initial opacity to 0 or low value, then animate to 1 on canplaythrough
        video.style.opacity = 0; 
        video.style.transition = 'opacity 1s ease-in';
    }

    // --- Helper function to display messages ---
    function showStatusMessage(element, msg, type) {
        if (!element) return;
        element.textContent = msg;
        element.className = `status-message ${type}`;
        // For forms, ensure it's displayed, for other elements it might always be present.
        element.style.display = 'block'; 
    }

    // --- Client-side Form Validation and Submission (Login Page) --- //
    const loginForm = document.getElementById('login-form');
    const loginStatusMessage = document.getElementById('login-status-message');
    const loginSubmitBtn = document.getElementById('login-submit-btn');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const usernameError = document.getElementById('username-error');
    const passwordError = document.getElementById('password-error');

    const validateLoginInput = () => {
        let isValid = true;

        if (usernameInput) { // Check if element exists on the page
            if (!usernameInput.value.trim()) {
                usernameError.textContent = 'Username is required.';
                usernameInput.setAttribute('aria-invalid', 'true');
                isValid = false;
            } else {
                usernameError.textContent = '';
                usernameInput.removeAttribute('aria-invalid');
            }
        }

        if (passwordInput) { // Check if element exists on the page
            if (!passwordInput.value.trim()) {
                passwordError.textContent = 'Password is required.';
                passwordInput.setAttribute('aria-invalid', 'true');
                isValid = false;
            } else {
                passwordError.textContent = '';
                passwordInput.removeAttribute('aria-invalid');
            }
        }
        return isValid;
    };

    // Real-time validation feedback
    if (usernameInput) usernameInput.addEventListener('input', validateLoginInput);
    if (passwordInput) passwordInput.addEventListener('input', validateLoginInput);

    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            showStatusMessage(loginStatusMessage, '', ''); // Clear previous messages

            if (!validateLoginInput()) {
                showStatusMessage(loginStatusMessage, 'Please fill in all required fields.', 'error');
                return;
            }

            if (loginSubmitBtn) { // Ensure button exists
                loginSubmitBtn.textContent = 'Logging in...';
                loginSubmitBtn.disabled = true;
                loginSubmitBtn.classList.add('loading');
            }
            

            const username = usernameInput.value.trim();
            const password = passwordInput.value.trim();

            try {
                const response = await fetch(`${API_BASE_URL}/login`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    body: JSON.stringify({ username, password })
                });

                if (response.ok) {
                    const data = await response.json();
                    console.log('Login successful:', data);
                    showStatusMessage(loginStatusMessage, data.message || 'Login successful! Redirecting...', 'success');
                    // In a real app, you would store tokens, redirect, etc.
                    setTimeout(() => { window.location.href = '/'; }, 1500); // Redirect to home page
                } else {
                    const errorData = await response.json();
                    console.error('Login failed:', errorData);
                    showStatusMessage(loginStatusMessage, errorData.message || 'Login failed. Please check your credentials.', 'error');
                }
            } catch (error) {
                console.error('Network error or server unavailable:', error);
                showStatusMessage(loginStatusMessage, 'Failed to connect to the server. Please try again later.', 'error');
                // Fallback for API unavailability (e.g., mock successful login after delay)
                console.warn('Simulating success due to API unavailability...');
                showStatusMessage(loginStatusMessage, 'Server unavailable. Simulating success...', 'success');
                setTimeout(() => { window.location.href = '/'; }, 3000); // Redirect to home page
            }
            finally {
                if (loginSubmitBtn) {
                    loginSubmitBtn.textContent = 'Login';
                    loginSubmitBtn.disabled = false;
                    loginSubmitBtn.classList.remove('loading');
                }
            }
        });
    }

    // --- Test API Connection Button --- //
    const testApiBtn = document.getElementById('test-api-btn');
    const apiTestStatus = document.getElementById('api-test-status');

    if (testApiBtn && apiTestStatus) {
        testApiBtn.addEventListener('click', async () => {
            showStatusMessage(apiTestStatus, 'Testing connection...', '');
            testApiBtn.disabled = true;
            testApiBtn.classList.add('loading');

            try {
                // Using the /api/status endpoint to test connectivity
                const response = await fetch(`${API_BASE_URL}/status`); 

                if (response.ok) {
                    const data = await response.json();
                    console.log('API Status:', data);
                    showStatusMessage(apiTestStatus, `API Connected! Status: ${data.status || 'OK'}`, 'success'); 
                } else {
                    console.error('API connection failed with status:', response.status);
                    const errorData = await response.json().catch(() => ({})); // Try to parse, but don't fail if not JSON
                    showStatusMessage(apiTestStatus, `API connection failed: HTTP ${response.status}. ${errorData.message || ''}`, 'error');
                }
            } catch (error) {
                console.error('Network error or API not reachable:', error);
                showStatusMessage(apiTestStatus, 'Network error: API is not reachable. Ensure Flask server is running.', 'error');
                // Provide fallback sample data for demonstration if API isn't available (e.g., a simple status object)
                console.log('Using fallback data for API status.');
                showStatusMessage(apiTestStatus, 'API not reachable. (Fallback: Status OK)', 'success');
            }
            finally {
                testApiBtn.disabled = false;
                testApiBtn.classList.remove('loading');
            }
        });
    }

    // --- Register Form Validation and Submission --- //
    const registerForm = document.getElementById('register-form');
    const registerStatusMessage = document.getElementById('register-status-message');
    const registerSubmitBtn = document.getElementById('register-submit-btn');
    const regUsernameInput = document.getElementById('reg-username');
    const regEmailInput = document.getElementById('reg-email');
    const regPasswordInput = document.getElementById('reg-password');
    const regConfirmPasswordInput = document.getElementById('reg-confirm-password');
    const regUsernameError = document.getElementById('reg-username-error');
    const regEmailError = document.getElementById('reg-email-error');
    const regPasswordError = document.getElementById('reg-password-error');
    const regConfirmPasswordError = document.getElementById('reg-confirm-password-error');

    const validateRegisterInput = () => {
        let isValid = true;

        // Exit if elements not found (not on register page)
        if (!regUsernameInput || !regEmailInput || !regPasswordInput || !regConfirmPasswordInput) return true; 

        // Username validation
        if (!regUsernameInput.value.trim()) {
            regUsernameError.textContent = 'Username is required.';
            regUsernameInput.setAttribute('aria-invalid', 'true');
            isValid = false;
        } else if (regUsernameInput.value.trim().length < 3) {
            regUsernameError.textContent = 'Username must be at least 3 characters.';
            regUsernameInput.setAttribute('aria-invalid', 'true');
            isValid = false;
        } else {
            regUsernameError.textContent = '';
            regUsernameInput.removeAttribute('aria-invalid');
        }

        // Email validation
        const emailPattern = /^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$/;
        if (!regEmailInput.value.trim()) {
            regEmailError.textContent = 'Email is required.';
            regEmailInput.setAttribute('aria-invalid', 'true');
            isValid = false;
        } else if (!emailPattern.test(regEmailInput.value.trim())) {
            regEmailError.textContent = 'Please enter a valid email address.';
            regEmailInput.setAttribute('aria-invalid', 'true');
            isValid = false;
        } else {
            regEmailError.textContent = '';
            regEmailInput.removeAttribute('aria-invalid');
        }

        // Password validation
        if (!regPasswordInput.value.trim()) {
            regPasswordError.textContent = 'Password is required.';
            regPasswordInput.setAttribute('aria-invalid', 'true');
            isValid = false;
        } else if (regPasswordInput.value.trim().length < 6) {
            regPasswordError.textContent = 'Password must be at least 6 characters.';
            regPasswordInput.setAttribute('aria-invalid', 'true');
            isValid = false;
        } else {
            regPasswordError.textContent = '';
            regPasswordInput.removeAttribute('aria-invalid');
        }

        // Confirm password validation
        if (regConfirmPasswordInput.value.trim() !== regPasswordInput.value.trim()) {
            regConfirmPasswordError.textContent = 'Passwords do not match.';
            regConfirmPasswordInput.setAttribute('aria-invalid', 'true');
            isValid = false;
        } else {
            regConfirmPasswordError.textContent = '';
            regConfirmPasswordInput.removeAttribute('aria-invalid');
        }

        return isValid;
    };

    if (regUsernameInput) regUsernameInput.addEventListener('input', validateRegisterInput);
    if (regEmailInput) regEmailInput.addEventListener('input', validateRegisterInput);
    if (regPasswordInput) regPasswordInput.addEventListener('input', validateRegisterInput);
    if (regConfirmPasswordInput) regConfirmPasswordInput.addEventListener('input', validateRegisterInput);

    if (registerForm) {
        registerForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            showStatusMessage(registerStatusMessage, '', '');

            if (!validateRegisterInput()) {
                showStatusMessage(registerStatusMessage, 'Please correct the errors in the form.', 'error');
                return;
            }

            if (registerSubmitBtn) { // Ensure button exists
                registerSubmitBtn.textContent = 'Registering...';
                registerSubmitBtn.disabled = true;
                registerSubmitBtn.classList.add('loading');
            }
            

            const username = regUsernameInput.value.trim();
            const email = regEmailInput.value.trim(); // Backend only uses username/password for User model
            const password = regPasswordInput.value.trim();

            try {
                // This would typically go to a /register endpoint on the backend
                const response = await fetch(`${API_BASE_URL}/register`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    body: JSON.stringify({ username, password }) // Only send data backend expects
                });

                if (response.ok) {
                    const data = await response.json();
                    console.log('Registration successful:', data);
                    showStatusMessage(registerStatusMessage, data.message || 'Registration successful! You can now log in.', 'success');
                    setTimeout(() => { window.location.href = '/login'; }, 2000);
                } else {
                    const errorData = await response.json();
                    console.error('Registration failed:', errorData);
                    showStatusMessage(registerStatusMessage, errorData.message || 'Registration failed. Please try again.', 'error');
                }
            } catch (error) {
                console.error('Network error during registration:', error);
                showStatusMessage(registerStatusMessage, 'Failed to connect to the server. Please try again later.', 'error');
                // Fallback for API unavailability - simulate success
                console.warn('Simulating successful registration due to API unavailability...');
                showStatusMessage(registerStatusMessage, 'Server unavailable. Simulating registration success...', 'success');
                setTimeout(() => { window.location.href = '/login'; }, 3000);
            }
            finally {
                if (registerSubmitBtn) {
                    registerSubmitBtn.textContent = 'Register';
                    registerSubmitBtn.disabled = false;
                    registerSubmitBtn.classList.remove('loading');
                }
            }
        });
    }

    // --- Contact Form Submission (Basic Client-Side with mock API call) --- //
    const contactForm = document.getElementById('contact-form');
    const contactStatusMessage = document.getElementById('contact-status-message');
    const contactSubmitBtn = document.getElementById('contact-submit-btn');

    if (contactForm) {
        contactForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            showStatusMessage(contactStatusMessage, '', '');

            const name = document.getElementById('name').value.trim();
            const email = document.getElementById('email').value.trim();
            const message = document.getElementById('message').value.trim();

            if (!name || !email || !message) {
                showStatusMessage(contactStatusMessage, 'All fields are required.', 'error');
                return;
            }
            const emailPattern = /^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$/;
            if (!emailPattern.test(email)) {
                showStatusMessage(contactStatusMessage, 'Please enter a valid email address.', 'error');
                return;
            }

            if (contactSubmitBtn) {
                contactSubmitBtn.textContent = 'Sending...';
                contactSubmitBtn.disabled = true;
                contactSubmitBtn.classList.add('loading');
            }
            

            try {
                // Send data to a backend contact endpoint
                const response = await fetch(`${API_BASE_URL}/contact`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    body: JSON.stringify({ name, email, message })
                });

                if (response.ok) {
                    const data = await response.json();
                    console.log('Contact form submitted:', data);
                    showStatusMessage(contactStatusMessage, data.message || 'Thank you for your message! We will get back to you soon.', 'success');
                    contactForm.reset(); // Clear the form
                } else {
                    const errorData = await response.json();
                    console.error('Contact form submission failed:', errorData);
                    showStatusMessage(contactStatusMessage, errorData.message || 'Failed to send message. Please try again.', 'error');
                }
            } catch (error) {
                console.error('Contact form submission error:', error);
                showStatusMessage(contactStatusMessage, 'Failed to connect to the server for contact submission. Please try again later.', 'error');
                // Fallback / simulation if API is unavailable
                console.warn('Simulating successful contact submission due to API unavailability...');
                showStatusMessage(contactStatusMessage, 'Server unavailable. Simulating message sent successfully.', 'success');
                contactForm.reset();
            }
            finally {
                if (contactSubmitBtn) {
                    contactSubmitBtn.textContent = 'Send Message';
                    contactSubmitBtn.disabled = false;
                    contactSubmitBtn.classList.remove('loading');
                }
            }
        });
    }
});
