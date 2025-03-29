import { useState } from 'react'
import Research from './components/Research'
import Home from './components/Home'
import './App.css'
import Trade from './components/Trade'

function App() {
  const [activePage, setActivePage] = useState('home')

  const renderPage = () => {
    switch (activePage) {
      case 'home':
        return <Home />
      case 'trade':
        return <Trade />
      case 'research':
        return <Research />
      default:
        return <Home />
    }
  }

  return (
    <div className="app-container">
      <nav className="navbar">
        <div className="nav-logo"
          onClick={() => setActivePage('home')}>
          Koinbase
        </div>
        <ul className="nav-links">
          <li 
            className={activePage === 'home' ? 'active' : ''} 
            onClick={() => setActivePage('home')}
          >
            Home
          </li>
          <li 
            className={activePage === 'trade' ? 'active' : ''} 
            onClick={() => setActivePage('trade')}
          >
            Trade
          </li>
          <li 
            className={activePage === 'research' ? 'active' : ''} 
            onClick={() => setActivePage('research')}
          >
            Research
          </li>
        </ul>
      </nav>
      
      <main className="main-content">
        {renderPage()}
      </main>
      
      <footer className="footer">
        <p>© 2025 Koinbase - Investment Platform</p>
      </footer>
    </div>
  )
}

export default App
