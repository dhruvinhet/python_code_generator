import { 
  CssBaseline, 
  ThemeProvider, 
  createTheme, 
  Box, 
  Typography,
  Button
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { useNavigate } from 'react-router-dom';
import QABlogUI from './components/QABlogUI';

// --- DARK THEME ---
const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#8b5cf6' },
    secondary: { main: '#f472b6' },
    background: { 
      default: '#0f172a',
      paper: '#1e293b' 
    },
    text: { primary: '#f1f5f9', secondary: '#94a3b8' }
  },
  typography: {
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    h1: {
      fontWeight: 800,
      letterSpacing: '-0.025em'
    },
    h2: {
      fontWeight: 700,
      letterSpacing: '-0.025em'
    },
    h3: {
      fontWeight: 600,
      letterSpacing: '-0.025em'
    }
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          textTransform: 'none',
          fontWeight: 600,
          padding: '12px 24px'
        }
      }
    }
  }
});

export default function BlogGenerator() {
  const navigate = useNavigate();

  const handleHomeClick = () => {
    navigate('/');
  };

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <style>{` 
        body { 
          background: ${darkTheme.palette.background.default}; 
          font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }
        
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
        
        * {
          box-sizing: border-box;
        }
        
        ::-webkit-scrollbar {
          width: 8px;
        }
        
        ::-webkit-scrollbar-track {
          background: #1e293b;
        }
        
        ::-webkit-scrollbar-thumb {
          background: ${darkTheme.palette.primary.main};
          border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
          background: #a855f7;
        }
      `}</style>
      
      {/* Top Bar */}
      <Box sx={{ 
        background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
        borderBottom: '1px solid #374151',
        backdropFilter: 'blur(10px)',
        position: 'sticky',
        top: 0,
        zIndex: 1000,
        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3)'
      }}>
        <Box sx={{ 
          maxWidth: '1200px', 
          margin: '0 auto',
          p: 2, 
          display: 'flex', 
          justifyContent: 'flex-start', 
          alignItems: 'center' 
        }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Button
              onClick={handleHomeClick}
              startIcon={<ArrowBackIcon />}
              variant="outlined"
              sx={{ 
                borderColor: 'primary.main',
                color: 'primary.main',
                borderRadius: '12px',
                padding: '8px 16px',
                fontWeight: 600,
                '&:hover': {
                  background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(244, 114, 182, 0.1) 100%)',
                  borderColor: 'primary.main',
                  transform: 'translateY(-1px)',
                  boxShadow: '0 4px 15px rgba(139, 92, 246, 0.3)'
                },
                transition: 'all 0.3s ease'
              }}
            >
              Home
            </Button>
            
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
              <Box sx={{
                width: 36,
                height: 36,
                background: 'linear-gradient(135deg, #8b5cf6 0%, #f472b6 100%)',
                borderRadius: '8px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '18px',
                color: 'white',
                boxShadow: '0 4px 15px rgba(139, 92, 246, 0.4)'
              }}>
                ✨
              </Box>
              <Box>
                <Typography 
                  variant="h4" 
                  sx={{ 
                    fontWeight: 800, 
                    background: 'linear-gradient(135deg, #8b5cf6 0%, #f472b6 100%)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    backgroundClip: 'text',
                    margin: 0,
                    lineHeight: 1,
                    fontSize: '1.8rem'
                  }}
                >
                  BlogBot
                </Typography>
                <Typography 
                  variant="caption" 
                  sx={{ 
                    color: 'text.secondary',
                    fontSize: '11px',
                    fontWeight: 500
                  }}
                >
                  AI-Powered Content Creator
                </Typography>
              </Box>
            </Box>
          </Box>
        </Box>
      </Box>
      
      {/* Main Content Container */}
      <Box sx={{ 
        maxWidth: '1200px', 
        margin: '0 auto',
        padding: { xs: 1.5, sm: 2, md: 3 },
        minHeight: 'calc(100vh - 80px)'
      }}>
        <QABlogUI />
      </Box>
    </ThemeProvider>
  );
}
