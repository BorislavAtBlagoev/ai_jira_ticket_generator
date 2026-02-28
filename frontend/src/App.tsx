import { Route, Routes } from 'react-router-dom'
import GeneratorPage from './components/GeneratorPage'
import HelpPage from './components/HelpPage'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<GeneratorPage />} />
      <Route path="/help" element={<HelpPage />} />
    </Routes>
  )
}
