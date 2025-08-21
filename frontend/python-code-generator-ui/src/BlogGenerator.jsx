import { useState, useMemo } from 'react';
import { 
  CssBaseline, 
  ThemeProvider, 
  createTheme, 
  IconButton, 
  Box, 
  Typography,
  Button
} from '@mui/material';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { useNavigate } from 'react-router-dom';
import QABlogUI from './components/QABlogUI';

// --- THEMES ---
const lightTheme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: '#6D28D9' },
    secondary: { main: '#EC4899' },
    background: { 
      default: '#f9fafb',
      paper: '#FFFFFF' 
    },
    text: { primary: '#111827', secondary: '#6B7280' }
  },
});

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#A78BFA' },
    secondary: { main: '#F472B6' },
    background: { 
      default: '#111827',
      paper: '#1F2937' 
    },
    text: { primary: '#F9FAFB', secondary: '#9CA3AF' }
  },
});

export default function BlogGenerator() {
  const [mode, setMode] = useState('light');
  const navigate = useNavigate();

  const toggleColorMode = () => {
    setMode((prevMode) => (prevMode === 'light' ? 'dark' : 'light'));
  };

  const handleHomeClick = () => {
    navigate('/');
  };

  const theme = useMemo(() => (mode === 'light' ? lightTheme : darkTheme), [mode]);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <style>{` body { background: ${theme.palette.background.default}; } `}</style>
      
      {/* Top Bar */}
      <Box sx={{ p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Button
            onClick={handleHomeClick}
            startIcon={<ArrowBackIcon />}
            variant="outlined"
            sx={{ 
              borderColor: 'primary.main',
              color: 'primary.main',
              '&:hover': {
                backgroundColor: 'primary.main',
                color: 'white',
                borderColor: 'primary.main'
              }
            }}
          >
            Home
          </Button>
          <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'primary.main' }}>AI Blog Agent</Typography>
        </Box>
        <IconButton onClick={toggleColorMode} color="inherit">
          {mode === 'dark' ? <Brightness7Icon /> : <Brightness4Icon />}
        </IconButton>
      </Box>
      
      {/* Main Content - Use QABlogUI Component */}
      <Box sx={{ p: 3 }}>
        <QABlogUI />
      </Box>
    </ThemeProvider>
  );
}
