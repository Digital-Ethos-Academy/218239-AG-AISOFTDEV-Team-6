
import './App.css'
import Dashboard from './components/dashboard.jsx'
import Chat from './components/chat.jsx'

function App() {

  return (
    <div className="flex h-screen">
      <div className="w-1/2 bg-gray-50 border-r border-gray-200">
        <Dashboard />
      </div>
      
      <div className="w-1/2 bg-white flex items-center justify-center p-4">
        <Chat />
      </div>
    </div>
  )
}

export default App
