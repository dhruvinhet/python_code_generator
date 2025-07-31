// API Base URL
const API_BASE_URL = 'http://localhost:8080/api';

// DOM Elements
const vehicleListContainer = document.getElementById('vehicle-list');
const searchInput = document.getElementById('search-input');
const searchButton = document.getElementById('search-button');
const testApiConnectionButton = document.getElementById('test-api-connection');

// Function to fetch vehicles from the API
async function fetchVehicles() {
    vehicleListContainer.innerHTML = '<div class="loading">Loading vehicles...</div>';
    try {
        const response = await fetch(`${API_BASE_URL}/vehicles`);
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const vehicles = await response.json();
        displayVehicles(vehicles);
    } catch (error) {
        console.error('Error fetching vehicles:', error);
        vehicleListContainer.innerHTML = '<div class="error">Failed to load vehicles. Please try again later.</div>';
        // Fallback Data
        const fallbackVehicles = [
            { id: 1, make: 'Toyota', model: 'Camry', year: 2020, price: 25000, imageUrl: 'https://via.placeholder.com/300x200', availability: true },
            { id: 2, make: 'Honda', model: 'Civic', year: 2021, price: 23000, imageUrl: 'https://via.placeholder.com/300x200', availability: false }
        ];
        displayVehicles(fallbackVehicles);
    }
}

// Function to display vehicles in the UI
function displayVehicles(vehicles) {
    vehicleListContainer.innerHTML = ''; // Clear loading message or previous content
    if (vehicles.length === 0) {
        vehicleListContainer.innerHTML = '<div class="no-results">No vehicles found.</div>';
        return;
    }

    vehicles.forEach(vehicle => {
        const vehicleCard = document.createElement('div');
        vehicleCard.classList.add('vehicle-card');

        const imageUrl = vehicle.imageUrl || 'https://via.placeholder.com/300x200'; // Fallback image URL

        vehicleCard.innerHTML = `
            <img src="${imageUrl}" alt="${vehicle.make} ${vehicle.model}">
            <div class="vehicle-details">
                <h3>${vehicle.make} ${vehicle.model}</h3>
                <p>${vehicle.year}</p>
                <p class="price">$${vehicle.price}/day</p>
                <p>${vehicle.availability ? 'Available' : 'Not Available'}</p>
                <button class="rent-now" data-vehicle-id="${vehicle.id}">Rent Now</button>
            </div>
        `;

        vehicleListContainer.appendChild(vehicleCard);
    });

    // Add event listeners to the Rent Now buttons after they are added to the DOM
    const rentNowButtons = document.querySelectorAll('.rent-now');
    rentNowButtons.forEach(button => {
        button.addEventListener('click', handleRentNowClick);
    });
}

// Function to handle the Rent Now button click
function handleRentNowClick(event) {
    const vehicleId = event.target.dataset.vehicleId;
    alert(`Rent Now clicked for vehicle ID: ${vehicleId}`); // Replace with actual booking logic
    console.log(`Rent Now clicked for vehicle ID: ${vehicleId}`);
}

// Function to handle search
async function handleSearch() {
    const searchTerm = searchInput.value.toLowerCase();
    // In a real application, you would filter the vehicles based on the search term
    // For this example, we'll just log the search term to the console
    console.log('Search term:', searchTerm);
    // Fetch vehicles again, potentially with search parameters
    await fetchVehicles(); // Refresh the vehicle list (modify API call when backend is ready)
}


// Function to test API connection
async function testApiConnection() {
    try {
        const response = await fetch(`${API_BASE_URL}/vehicles`);
        if (response.ok) {
            alert('API connection successful!');
            console.log('API connection successful!');
        } else {
            alert(`API connection failed. Status: ${response.status}`);
            console.error(`API connection failed. Status: ${response.status}`);
        }
    } catch (error) {
        alert('API connection failed. Check the console for details.');
        console.error('API connection error:', error);
    }
}


// Event Listeners
searchButton.addEventListener('click', handleSearch);
searchInput.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
        handleSearch();
    }
});
testApiConnectionButton.addEventListener('click', testApiConnection);

// Initial Vehicle Fetch
fetchVehicles();