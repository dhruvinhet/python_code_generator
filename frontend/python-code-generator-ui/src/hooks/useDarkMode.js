import { useState, useEffect } from 'react'

export function useDarkMode() {
  // Initialize with proper detection
  const [isDark, setIsDark] = useState(() => {
    if (typeof window !== 'undefined') {
      const savedMode = localStorage.getItem('darkMode')
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      return savedMode ? savedMode === 'true' : prefersDark
    }
    return false
  })

  useEffect(() => {
    // Apply the initial state to body class
    if (isDark) {
      document.body.classList.add('dark')
    } else {
      document.body.classList.remove('dark')
    }
  }, [isDark])

  const toggleDarkMode = () => {
    const newDarkMode = !isDark
    setIsDark(newDarkMode)
    
    if (newDarkMode) {
      document.body.classList.add('dark')
    } else {
      document.body.classList.remove('dark')
    }
    
    localStorage.setItem('darkMode', newDarkMode.toString())
  }

  return { isDark, toggleDarkMode }
}
