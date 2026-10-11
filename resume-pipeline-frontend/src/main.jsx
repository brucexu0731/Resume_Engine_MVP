import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { HashRouter } from 'react-router-dom'
import './index.css'
import App from './App.jsx'

/*
    Setting up react router
      1. npm i react-router-dom
      2. in main.jsx wrap the App in BrowserRouter or HashRouter
                                      /                 /#
                                      /login            /#login
                                      /upload           /#upload
      <a href="/login">Login page</a> 
      3. Create some links using hte <Link> component
      4. Create your router

    
*/

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <HashRouter>
      <App />
    </HashRouter>
  </StrictMode>,
)
