# AI Studio Gemini API Setup Guide

## 🔑 Getting Your AI Studio Gemini API Key

### Step 1: Visit AI Studio
Go to [Google AI Studio](https://aistudio.google.com/app/apikey)

### Step 2: Create API Key
1. Click "Create API key"
2. Select "Create API key in new project" or use existing project
3. Copy the generated API key

### Step 3: Configure Environment
1. Create a `.env` file in the `backend` folder:
```bash
GOOGLE_API_KEY=your_ai_studio_gemini_api_key_here
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
FLASK_DEBUG=True
```

2. Replace `your_ai_studio_gemini_api_key_here` with your actual API key

## ✅ Verification

Test your configuration:
```bash
cd backend
python -c "from config import Config; print('API Key configured:', 'Yes' if Config.GOOGLE_API_KEY else 'No')"
```

## 🔧 Technical Details

### API Key Usage
- The system uses `GOOGLE_API_KEY` environment variable
- Fallback support for `GEMINI_API_KEY` (optional)
- Both point to the same AI Studio Gemini API

### Models Used
- **LangChain Integration**: `gemini-1.5-pro`
- **Direct API**: `gemini-1.5-pro` and `gemini-2.0-flash-exp`

### Files Updated
- `config.py` - Centralized API key configuration
- `advanced_agents_system.py` - Multi-agent system
- `agents.py` - Simple agents
- `web_agents.py` - Web-based agents
- `app.py` - Main Flask application

## 🚨 Important Notes

1. **Free Tier**: AI Studio provides generous free tier limits
2. **Rate Limits**: Respect API rate limits for optimal performance
3. **Security**: Never commit your API key to version control
4. **Environment**: Use `.env` file for local development

## 🎯 Features Supported

✅ **Multi-Agent Project Generation**
- Complete full-stack applications
- AI model integration
- Automatic code generation

✅ **Simple Project Generation**
- Quick prototypes
- Basic applications
- Script generation

✅ **Web Integration**
- Real-time progress tracking
- Interactive UI
- Project management

## 📞 Support

If you encounter issues:
1. Verify your API key is correct
2. Check AI Studio quota and limits
3. Ensure proper environment configuration
4. Test with simple requests first

---
*Updated for AI Studio Gemini API compatibility*
