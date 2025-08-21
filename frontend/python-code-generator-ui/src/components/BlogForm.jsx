import { useState } from 'react';
import { Box, TextField, Button, MenuItem, CircularProgress, Typography } from '@mui/material';

export default function BlogForm({ onGenerate, isLoading }) {
  const [topic, setTopic] = useState('');
  const [tone, setTone] = useState('Professional');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (topic.trim()) {
      onGenerate({ topic, tone });
    }
  };

  return (
    <Box 
      component="form" 
      onSubmit={handleSubmit} 
      sx={{ 
        p: 5, 
        borderRadius: 4,
        height: '100%',
        bgcolor: 'rgba(255, 255, 255, 0.9)',
        backdropFilter: 'blur(12px)',
        border: '1px solid rgba(0, 0, 0, 0.1)',
        boxShadow: '0 8px 32px rgba(0,0,0,0.2)',
        display: 'flex',
        flexDirection: 'column',
        gap: 3
      }}
    >
      {/* Title */}
      <Typography 
        variant="h5" 
        sx={{ 
          textAlign: 'center', 
          fontWeight: 'bold', 
          mb: 1,
          color: 'primary.main'
        }}
      >
        📝 Create Your Blog
      </Typography>

      {/* Blog Topic */}
      <TextField
        label="Enter Blog Topic"
        variant="outlined"
        fullWidth
        required
        value={topic}
        onChange={(e) => setTopic(e.target.value)}
        margin="normal"
        InputProps={{ sx: { fontSize: '1.1rem', py: 1 } }}
        InputLabelProps={{ sx: { fontSize: '1rem' } }}
      />

      {/* Tone Selector */}
      <TextField
        select
        label="Writing Tone"
        value={tone}
        onChange={(e) => setTone(e.target.value)}
        fullWidth
        margin="normal"
        InputProps={{ sx: { fontSize: '1.1rem', py: 1 } }}
        InputLabelProps={{ sx: { fontSize: '1rem' } }}
      >
        <MenuItem value="Professional">Professional</MenuItem>
        <MenuItem value="Casual">Casual</MenuItem>
        <MenuItem value="Enthusiastic">Enthusiastic</MenuItem>
        <MenuItem value="Witty">Witty</MenuItem>
      </TextField>

      {/* Generate Button */}
      <Button 
        type="submit" 
        variant="contained" 
        size="large" 
        fullWidth 
        disabled={isLoading}
        sx={{ 
          mt: 2, 
          py: 1.5,
          fontSize: '1.1rem',
          fontWeight: 'bold',
          textTransform: 'none',
          borderRadius: 3,
          background: 'linear-gradient(90deg, #1976d2, #42a5f5)',
          '&:hover': {
            background: 'linear-gradient(90deg, #1565c0, #1e88e5)',
            transform: 'scale(1.02)',
          },
          transition: 'all 0.3s ease'
        }}
      >
        {isLoading ? (
          <>
            <CircularProgress size={24} sx={{ color: 'white', mr: 1 }} />
            Generating...
          </>
        ) : '🚀 Generate Blog'}
      </Button>
    </Box>
  );
}