document.addEventListener('DOMContentLoaded', () => {
    const API_BASE_URL = 'http://localhost:8080/api';

    // DOM Elements
    const numbersInput = document.getElementById('numbers-input');
    const buildTreeBtn = document.getElementById('build-tree-btn');
    const clearTreeBtn = document.getElementById('clear-tree-btn');
    const testApiBtn = document.getElementById('test-api-btn');
    const messageArea = document.getElementById('message-area');
    const loadingIndicator = document.getElementById('loading-indicator');
    const treeVisualization = document.getElementById('tree-visualization');

    // Fallback Data for API failure or empty tree
    const FALLBACK_TREE_DATA = {
        "tree": {
            "value": 10,
            "height": 2,
            "left": {
                "value": 5,
                "height": 1,
                "left": {
                    "value": 3,
                    "height": 0,
                    "left": null,
                    "right": null
                },
                "right": {
                    "value": 7,
                    "height": 0,
                    "left": null,
                    "right": null
                }
            },
            "right": {
                "value": 15,
                "height": 1,
                "left": {
                    "value": 12,
                    "height": 0,
                    "left": null,
                    "right": null
                },
                "right": {
                    "value": 18,
                    "height": 0,
                    "left": null,
                    "right": null
                }
            }
        }
    };

    /**
     * Displays a message to the user.
     * @param {string} message - The message to display.
     * @param {'success'|'error'|'info'} type - The type of message (for styling).
     */
    const displayMessage = (message, type) => {
        messageArea.textContent = message;
        messageArea.className = `message-area ${type}`;
        messageArea.setAttribute('aria-live', 'assertive');
        setTimeout(() => {
            messageArea.textContent = '';
            messageArea.className = 'message-area';
            messageArea.removeAttribute('aria-live');
        }, 5000); // Message disappears after 5 seconds
    };

    /**
     * Shows the loading indicator and disables buttons/input.
     */
    const showLoading = () => {
        loadingIndicator.style.display = 'flex';
        buildTreeBtn.disabled = true;
        clearTreeBtn.disabled = true;
        testApiBtn.disabled = true;
        numbersInput.disabled = true;
        messageArea.textContent = ''; // Clear any previous messages
        messageArea.className = 'message-area';
        treeVisualization.innerHTML = ''; // Clear visualization area during loading
    };

    /**
     * Hides the loading indicator and enables buttons/input.
     */
    const hideLoading = () => {
        loadingIndicator.style.display = 'none';
        buildTreeBtn.disabled = false;
        clearTreeBtn.disabled = false;
        testApiBtn.disabled = false;
        numbersInput.disabled = false;
    };

    /**
     * Validates the input string to ensure it contains comma-separated numbers.
     * @param {string} inputString - The string from the input field.
     * @returns {number[]|null} An array of numbers if valid, null otherwise.
     */
    const isValidInput = (inputString) => {
        if (!inputString.trim()) {
            displayMessage('Please enter numbers.', 'error');
            return null;
        }
        const numbers = inputString.split(',').map(s => s.trim()).filter(s => s !== '');
        if (numbers.length === 0) {
            displayMessage('No valid numbers found in input. Please use comma-separated values.', 'error');
            return null;
        }
        const parsedNumbers = numbers.map(Number);
        const invalidNumbers = parsedNumbers.filter(isNaN);

        if (invalidNumbers.length > 0) {
            displayMessage(`Invalid input: '${invalidNumbers.join(", ")}' are not numbers.`, 'error');
            return null;
        }
        return parsedNumbers;
    };

    /**
     * Recursively creates and returns a DOM element for a tree node.
     * @param {Object} nodeData - The data for the current node (value, left, right).
     * @param {boolean} isRoot - True if this is the root node.
     * @returns {HTMLElement} The created DOM element for the node.
     */
    const createNodeElement = (nodeData, isRoot = false) => {
        if (!nodeData || nodeData.value === undefined) {
            return null;
        }

        const nodeWrapper = document.createElement('div');
        nodeWrapper.classList.add('tree-node-wrapper');
        if (isRoot) {
            nodeWrapper.classList.add('is-root');
        }

        const nodeDiv = document.createElement('div');
        nodeDiv.classList.add('tree-node');
        nodeDiv.setAttribute('aria-label', `Node with value ${nodeData.value}`);

        const valueSpan = document.createElement('span');
        valueSpan.classList.add('node-value');
        valueSpan.textContent = nodeData.value;
        nodeDiv.appendChild(valueSpan);

        // Optional: Display height/balance factor for debugging/information
        const heightSpan = document.createElement('span');
        heightSpan.style.fontSize = '0.8em';
        heightSpan.style.display = 'block';
        heightSpan.style.marginTop = '5px';
        heightSpan.textContent = `H: ${nodeData.height !== undefined ? nodeData.height : '?'}`;
        nodeDiv.appendChild(heightSpan);

        nodeWrapper.appendChild(nodeDiv);

        const childrenContainer = document.createElement('div');
        childrenContainer.classList.add('children-container');

        const leftChild = createNodeElement(nodeData.left);
        const rightChild = createNodeElement(nodeData.right);

        if (leftChild) {
            childrenContainer.appendChild(leftChild);
        }
        if (rightChild) {
            childrenContainer.appendChild(rightChild);
        }

        // Only append children container if there are actual children to avoid empty space
        if (leftChild || rightChild) {
            nodeWrapper.appendChild(childrenContainer);
        }

        return nodeWrapper;
    };

    /**
     * Renders the AVL tree visualization on the frontend.
     * @param {Object} treeData - The structured tree data received from the backend.
     */
    const renderTree = (treeData) => {
        treeVisualization.innerHTML = ''; // Clear previous tree
        if (!treeData || !treeData.tree) {
            displayMessage('No tree data received or tree is empty. Please enter numbers.', 'info');
            return;
        }

        const rootElement = createNodeElement(treeData.tree, true);
        if (rootElement) {
            treeVisualization.appendChild(rootElement);
            displayMessage('Tree built successfully!', 'success');
        } else {
            displayMessage('Tree is empty (e.g., no valid numbers provided).', 'info');
        }
    };

    /**
     * Handles the 'Build Tree' button click, sending data to backend.
     */
    const buildTree = async () => {
        const inputString = numbersInput.value;
        const numbers = isValidInput(inputString);

        if (!numbers) {
            return; // Validation failed, message already displayed
        }

        showLoading();
        console.log('Sending numbers to backend:', numbers);

        try {
            const response = await fetch(`${API_BASE_URL}/build-avl-tree`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({ numbers: numbers })
            });

            if (!response.ok) {
                console.error(`HTTP error! status: ${response.status}`);
                let errorData = {};
                try {
                    errorData = await response.json();
                } catch (jsonError) {
                    console.error('Failed to parse error response JSON:', jsonError);
                    errorData.message = await response.text(); // Get raw text if JSON parsing fails
                }
                throw new Error(`Server responded with an error: ${errorData.error || response.statusText}. Details: ${errorData.details || errorData.message || 'No specific details.'}`);
            }

            const data = await response.json();
            console.log('Received tree data:', data);
            renderTree(data);
        } catch (error) {
            console.error('Failed to build AVL tree:', error);
            displayMessage(`Error building tree: ${error.message}. Displaying fallback data.`, 'error');
            renderTree(FALLBACK_TREE_DATA);
        } finally {
            hideLoading();
        }
    };

    /**
     * Clears the input field and the tree visualization area.
     */
    const clearTree = () => {
        numbersInput.value = '';
        treeVisualization.innerHTML = '';
        messageArea.textContent = '';
        messageArea.className = 'message-area';
        displayMessage('Visualization cleared.', 'info');
        console.log('Tree visualization cleared.');
    };

    /**
     * Tests the API connection by sending a dummy request.
     */
    const testApiConnection = async () => {
        displayMessage('Testing API connection...', 'info');
        console.log('Attempting to test API connection to:', API_BASE_URL);

        try {
            // Send a small, non-critical POST request to check server response
            const response = await fetch(`${API_BASE_URL}/build-avl-tree`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({ numbers: [1] })
            });

            if (response.ok) {
                const data = await response.json();
                displayMessage('API connection successful! Server responded with a dummy tree (value 1).', 'success');
                console.log('API test response:', data);
            } else {
                let errorDetail = await response.text();
                displayMessage(`API connection failed (Status: ${response.status}). ${errorDetail.substring(0, Math.min(errorDetail.length, 100))}...`, 'error');
                console.error(`API test failed: Status ${response.status}, Body: ${errorDetail}`);
            }
        } catch (error) {
            displayMessage(`API connection failed: ${error.message}. Is the backend running?`, 'error');
            console.error('Network error during API test:', error);
        }
    };

    // Event Listeners
    buildTreeBtn.addEventListener('click', (e) => {
        e.preventDefault(); // Prevent form submission
        buildTree();
    });

    clearTreeBtn.addEventListener('click', clearTree);

    testApiBtn.addEventListener('click', testApiConnection);

    // Initial message for user
    displayMessage('Enter numbers and click "Build Tree" to visualize!', 'info');
});
