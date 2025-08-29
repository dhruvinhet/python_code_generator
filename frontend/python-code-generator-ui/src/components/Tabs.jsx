import { useState, createContext, useContext } from 'react'
import { clsx } from 'clsx'

const TabsContext = createContext()

export function Tabs({ children, defaultValue, className, ...props }) {
  const [activeTab, setActiveTab] = useState(defaultValue)

  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      <div className={clsx('w-full', className)} {...props}>
        {children}
      </div>
    </TabsContext.Provider>
  )
}

export function TabsList({ children, className, ...props }) {
  return (
    <div 
      className={clsx(
        'inline-flex h-14 items-center justify-center rounded-2xl glass-effect p-2 mb-8 w-full max-w-md mx-auto',
        className
      )} 
      {...props}
    >
      {children}
    </div>
  )
}

export function TabsTrigger({ children, value, className, ...props }) {
  const { activeTab, setActiveTab } = useContext(TabsContext)
  
  return (
    <button
      onClick={() => setActiveTab(value)}
      className={clsx(
        'flex-1 inline-flex items-center justify-center whitespace-nowrap rounded-xl px-6 py-3 text-sm font-semibold transition-all duration-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/50 disabled:pointer-events-none disabled:opacity-50',
        activeTab === value 
          ? 'tab-active transform scale-105' 
          : 'tab-inactive hover:bg-white/20',
        className
      )}
      {...props}
    >
      {children}
    </button>
  )
}

export function TabsContent({ children, value, className, ...props }) {
  const { activeTab } = useContext(TabsContext)
  
  if (activeTab !== value) return null
  
  return (
    <div
      className={clsx(
        'animate-in fade-in-50 duration-300',
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}
