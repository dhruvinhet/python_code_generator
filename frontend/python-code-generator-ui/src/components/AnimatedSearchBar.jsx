import { useState } from 'react';
import { Box, InputBase, IconButton, Paper } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';

export default function AnimatedSearchBar() {
  const [isExpanded, setIsExpanded] = useState(false);

  const handleToggle = () => {
    setIsExpanded(!isExpanded);
  };

  return (
    <Paper
      component="form"
      elevation={3}
      sx={{
        p: '2px 4px',
        display: 'flex',
        alignItems: 'center',
        width: isExpanded ? 350 : 40, // Animate width
        height: 40,
        borderRadius: '50px', // Make it circular when collapsed
        transition: 'width 0.5s cubic-bezier(0.68, -0.55, 0.27, 1.55)', // Smooth transition
        mb: 4, // Margin bottom to space it from the form
        cursor: 'pointer',
      }}
      onFocus={() => setIsExpanded(true)}
      onBlur={() => setIsExpanded(false)}
    >
      <InputBase
        sx={{
          ml: 1,
          flex: 1,
          opacity: isExpanded ? 1 : 0, // Fade in the text
          transition: 'opacity 0.3s ease-in-out',
        }}
        placeholder="Search for topics..."
        inputProps={{ 'aria-label': 'search for topics' }}
      />
      <IconButton 
        type="button" 
        sx={{ p: '10px' }} 
        aria-label="search" 
        onClick={handleToggle}
      >
        <SearchIcon />
      </IconButton>
    </Paper>
  );
}