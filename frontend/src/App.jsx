import { useState } from 'react'
import Research from './components/Research'
import './App.css'

function App() {
  const [activePage, setActivePage] = useState('research')

  const renderPage = () => {
    switch (activePage) {
      case 'home':
        return <div className="page-container"><h1>Home Page</h1><p>Home page content will go here.</p></div>
      case 'trade':
        return <div className="page-container"><h1>Trade Page</h1><p>Trade page content will go here.</p></div>
      case 'research':
        return <Research />
      default:
        return <Research />
    }
  }

  return (
    <div className="app-container">
      <nav className="navbar">
        <div className="nav-logo">Koinbase</div>
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
