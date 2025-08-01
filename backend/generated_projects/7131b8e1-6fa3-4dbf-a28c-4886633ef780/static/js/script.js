// script.js

// Function to handle form submission (example for contact form)
async function handleSubmit(event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    try {
        const response = await fetch('http://localhost:8080/api/submit_form', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const result = await response.json();
        console.log('Success:', result);
        alert('Form submitted successfully!'); // Provide user feedback
        form.reset(); // Clear the form

    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while submitting the form.'); // User friendly error
    }
}

// Attach submit event listener to the contact form (if it exists)
const contactForm = document.getElementById('contactForm');
if (contactForm) {
    contactForm.addEventListener('submit', handleSubmit);
}

// Function to fetch vehicles data from API
async function fetchVehicles() {
    try {
        // Show loading indicator
        console.log('Fetching vehicles...');

        const response = await fetch('http://localhost:8080/api/vehicles');

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        console.log('Vehicles data:', data);

        // Process the data and update the UI accordingly

    } catch (error) {
        console.error('Error fetching vehicles:', error);

        // Provide fallback data
        const fallbackData = [
            { id: 1, name: 'Fallback Vehicle 1' },
            { id: 2, name: 'Fallback Vehicle 2' }
        ];
        console.log('Using fallback vehicles data:', fallbackData);
        // Use the fallbackData to populate UI, maybe display a message that API failed

    } finally {
        // Hide loading indicator, even on success or failure
        console.log('Vehicle fetch complete.');
    }
}

// Event listener for the "Test API Connection" button
const testApiButton = document.getElementById('testApi');
if (testApiButton) {
    testApiButton.addEventListener('click', fetchVehicles);
}

// Smooth scrolling navigation
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();

        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

//Example Start Quiz button functionality. Add full functionality as needed
const startQuizButton = document.getElementById('startQuiz');
if(startQuizButton){
    startQuizButton.addEventListener('click', () => {
        const category = document.getElementById('category').value;
        const difficulty = document.getElementById('difficulty').value;
        console.log(`Starting quiz with category: ${category} and difficulty: ${difficulty}`);
        alert(`Starting quiz with category: ${category} and difficulty: ${difficulty}`);
        // Redirect to quiz page, or load the quiz questions
        // window.location.href = '/quiz?category=' + category + '&difficulty=' + difficulty;
    });
}