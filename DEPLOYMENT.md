# Deployment Guide

## Quick Start

### 1. Clone and Setup

```bash
# Extract the project files
unzip python_code_generator.zip
cd python_code_generator
```

### 2. Backend Setup

```bash
cd backend

# Install dependencies
pip3 install -r requirements.txt

# Configure your Gemini API key
echo "GEMINI_API_KEY=AIzaSyD-m3JmxAJmAYYOuA2CXdD8gZv1-y0P_4M" > .env

# Start the backend server
python3 app.py
```

### 3. Frontend Setup

```bash
# Open a new terminal
cd frontend/python-code-generator-ui

# Install dependencies
pnpm install

# Start the frontend
pnpm run dev --host
```

### 4. Access the Application

- Frontend: http://localhost:5173
- Backend API: http://localhost:5000

## Production Deployment

### Backend (Flask)

```bash
# Install production server
pip3 install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Frontend (React)

```bash
# Build for production
pnpm run build

# Serve static files (example with nginx)
# Copy dist/ folder to your web server
```

## Environment Variables

Create a `.env` file in the backend directory:

```
GEMINI_API_KEY=your_actual_api_key_here
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your_secret_key_for_production
```

## System Requirements

- Python 3.11+
- Node.js 20+
- 2GB RAM minimum
- Internet connection for AI API calls

## Troubleshooting

1. **Port conflicts**: Change ports in configuration if needed
2. **API key issues**: Verify your Gemini API key is valid
3. **Dependencies**: Ensure all packages are installed correctly
4. **Permissions**: Check file permissions for generated projects

## Security Notes

- Keep your API key secure and never commit it to version control
- Use environment variables for sensitive configuration
- Implement rate limiting for production use
- Consider authentication for multi-user deployments

