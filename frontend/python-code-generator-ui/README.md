# Python Code Generator UI

A modern React-based frontend for the Python Code Generator application.

## 🚀 Deployment

### Backend
The backend is deployed at: https://python-code-generator-1.onrender.com

### Frontend Deployment to Vercel

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd frontend/python-code-generator-ui
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Environment Setup**
   - Copy `.env.example` to `.env`
   - Update the `VITE_API_BASE_URL` to point to your backend URL

4. **Build for production**
   ```bash
   npm run build
   ```

5. **Deploy to Vercel**
   - Connect your GitHub repository to Vercel
   - Vercel will automatically detect the configuration from `vercel.json`
   - The environment variable `VITE_API_BASE_URL` will be set automatically

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_BASE_URL` | Backend API URL | `http://localhost:5000` |

### Local Development

1. **Start development server**
   ```bash
   npm run dev
   ```

2. **Environment for local development**
   - Update `.env` to use `http://localhost:5000` for local backend
   - Or use `.env.example` as a template

## 📁 Project Structure

```
src/
├── components/          # Reusable components
├── config.js           # API configuration
├── App.jsx             # Main app component
├── main.jsx            # App entry point
└── ...
```

## 🔧 Configuration

- **API Base URL**: Configured via `VITE_API_BASE_URL` environment variable
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Icons**: Lucide React

## 🌐 Supported Features

- Code Generation
- Blog Generation
- Data Processing
- PPT Generation
- Multi-agent AI workflows