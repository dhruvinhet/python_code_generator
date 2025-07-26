# Python Code Generator - AI-Powered Multi-Agent System

A complete multi-agent AI-based Python code generator system that uses CrewAI and Google's Gemini API to automatically plan, generate, test, and package Python projects based on natural language descriptions.

## Features

- **Multi-Agent Architecture**: Uses specialized AI agents for different tasks:
  - **Planning Agent**: Analyzes requirements and creates comprehensive project plans
  - **Sr. Developer 1 Agent**: Generates high-quality Python code
  - **Sr. Developer 2 Agent**: Reviews, debugs, and fixes code issues
  - **Tester Agent**: Performs runtime testing
  - **Detailed Tester Agent**: Conducts functional testing
  - **Document Creator Agent**: Generates comprehensive documentation

- **Real-time Progress Tracking**: WebSocket-based live updates showing agent progress
- **Professional UI**: Dark-themed React interface with modern design
- **Complete Project Generation**: Generates entire Python projects with proper structure
- **Automatic Testing**: Runtime and functional testing of generated code
- **Documentation Generation**: Automatic README and setup instructions
- **Project Packaging**: Downloads projects as ZIP files

## System Architecture

```
Frontend (React)     Backend (Flask)     AI Agents (CrewAI)
     |                      |                    |
     |-- WebSocket ---------|                    |
     |-- REST API ----------|-- Agent Manager ---|
     |                      |                    |
     |                      |-- Project Files ---|
     |                      |-- ZIP Generation   |
```

## Prerequisites

- Python 3.11+
- Node.js 20+
- Google AI Studio API Key (Gemini)

## Installation & Setup

### Backend Setup

1. Navigate to the backend directory:
```bash
cd python_code_generator/backend
```

2. Install Python dependencies:
```bash
pip3 install -r requirements.txt
```

3. Configure environment variables:
```bash
# Create .env file with your Gemini API key
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

4. Start the backend server:
```bash
python3 app.py
```

The backend will start on `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd python_code_generator/frontend/python-code-generator-ui
```

2. Install Node.js dependencies:
```bash
pnpm install
```

3. Start the development server:
```bash
pnpm run dev --host
```

The frontend will start on `http://localhost:5173`

## Usage

1. Open your browser and navigate to `http://localhost:5173`
2. Enter a description of the Python project you want to create
3. Click "Generate Project" to start the AI-powered generation process
4. Watch the real-time progress as agents work on your project
5. Download the completed project as a ZIP file when generation is complete

### Example Prompts

- "Create a calculator app with a GUI that can perform basic arithmetic operations"
- "Build a to-do list application with file persistence and a command-line interface"
- "Make a simple web scraper that extracts data from websites and saves to CSV"
- "Create a password generator with customizable options and a Tkinter GUI"

## API Endpoints

### REST API

- `GET /` - API status and information
- `POST /api/generate` - Start project generation
- `GET /api/projects/<id>/status` - Get project status
- `GET /api/projects/<id>/download` - Download project ZIP
- `GET /api/projects` - List all projects
- `DELETE /api/projects/<id>` - Delete a project

### WebSocket Events

- `connect` - Client connection established
- `progress_update` - Real-time progress updates
- `project_completed` - Project generation completed
- `project_failed` - Project generation failed
- `join_project` - Join project room for updates

## Configuration

### Backend Configuration (`config.py`)

```python
GEMINI_API_KEY = "your_api_key"
CREWAI_MODEL = "gemini/gemini-2.0-flash-exp"
MAX_PROJECT_SIZE = 50  # Maximum number of files
SUPPORTED_GUI_FRAMEWORKS = ['streamlit', 'tkinter']
```

### Environment Variables

- `GEMINI_API_KEY` - Your Google AI Studio API key
- `FLASK_ENV` - Flask environment (development/production)
- `FLASK_DEBUG` - Enable Flask debug mode

## Project Structure

```
python_code_generator/
├── backend/
│   ├── agents.py              # CrewAI agent definitions
│   ├── project_manager.py     # Main project coordination logic
│   ├── app.py                 # Flask application and API endpoints
│   ├── config.py              # Configuration settings
│   ├── requirements.txt       # Python dependencies
│   ├── .env                   # Environment variables
│   ├── generated_projects/    # Generated project storage
│   └── temp/                  # Temporary files and ZIPs
├── frontend/
│   └── python-code-generator-ui/
│       ├── src/
│       │   ├── App.jsx        # Main React application
│       │   ├── App.css        # Styling and themes
│       │   └── components/    # UI components
│       ├── package.json       # Node.js dependencies
│       └── index.html         # HTML entry point
└── README.md                  # This documentation
```

## Generated Project Structure

Each generated project includes:

- **Source Code Files**: Complete Python implementation
- **requirements.txt**: Required dependencies
- **README.txt**: Project documentation and usage instructions
- **Main Entry Point**: Usually `main.py` to run the application

## Troubleshooting

### Common Issues

1. **Backend fails to start**:
   - Check if Gemini API key is correctly set in `.env`
   - Ensure all Python dependencies are installed
   - Verify Python version is 3.11+

2. **Frontend connection issues**:
   - Ensure backend is running on port 5000
   - Check browser console for WebSocket connection errors
   - Verify CORS is properly configured

3. **Project generation fails**:
   - Check API key validity and quota
   - Review backend logs for detailed error messages
   - Ensure internet connection for API calls

### Logs and Debugging

- Backend logs are displayed in the terminal where `app.py` is running
- Frontend logs are available in the browser's developer console
- Generated project files are stored in `backend/generated_projects/`

## Deployment

### Production Deployment

For production deployment, consider:

1. **Backend**: Deploy using a WSGI server like Gunicorn
2. **Frontend**: Build and serve static files with a web server
3. **Environment**: Use production-grade environment variables
4. **Security**: Implement proper authentication and rate limiting

### Docker Deployment (Optional)

Create Dockerfiles for both frontend and backend for containerized deployment.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is provided as-is for educational and development purposes.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs for error messages
3. Ensure all dependencies are properly installed
4. Verify API key configuration

## Technical Details

### AI Agent Workflow

1. **Planning**: Analyzes user requirements and creates structured project plan
2. **Code Generation**: Writes complete Python code based on the plan
3. **Code Review**: Reviews and fixes any issues in the generated code
4. **Runtime Testing**: Tests if the code runs without errors
5. **Functional Testing**: Validates that the code meets requirements
6. **Documentation**: Creates comprehensive project documentation
7. **Packaging**: Bundles everything into a downloadable ZIP file

### Technology Stack

- **Backend**: Flask, CrewAI, Google Generative AI, SocketIO
- **Frontend**: React, Tailwind CSS, Socket.IO Client, Axios
- **AI**: Google Gemini 2.0 Flash via AI Studio API
- **Real-time Communication**: WebSockets for live updates

This system demonstrates the power of multi-agent AI systems for complex software development tasks, providing an end-to-end solution for Python project generation.

