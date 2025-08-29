import React, { createContext, useContext, useState, useEffect } from 'react'

const DarkModeContext = createContext()

export function DarkModeProvider({ children }) {
  // Initialize with proper detection
  const [isDark, setIsDark] = useState(() => {
    if (typeof window !== 'undefined') {
      const savedMode = localStorage.getItem('darkMode')
      if (savedMode !== null) {
        return savedMode === 'true'
      }
      return window.matchMedia('(prefers-color-scheme: dark)').matches
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
    console.log('Toggling dark mode:', newDarkMode) // Debug log
    setIsDark(newDarkMode)
    
    if (newDarkMode) {
      document.body.classList.add('dark')
      console.log('Added dark class to body') // Debug log
    } else {
      document.body.classList.remove('dark')
      console.log('Removed dark class from body') // Debug log
    }
    
    localStorage.setItem('darkMode', newDarkMode.toString())
  }

  return (
    <DarkModeContext.Provider value={{ isDark, toggleDarkMode }}>
      {children}
    </DarkModeContext.Provider>
  )
}

export function useDarkMode() {
  const context = useContext(DarkModeContext)
  if (context === undefined) {
    throw new Error('useDarkMode must be used within a DarkModeProvider')
  }
  return context
}
