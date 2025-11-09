import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';
import StartPage from './pages/start_page';
import HomePage from './pages/homepage';
import BodyDetails from './components/body_details';
import FaceDetails from './components/face_details';
import Preferences from './components/preferences';
import Settings from './components/settings';
import Support from './components/support';

function App() {
  return (
    <Router>
      <AnimatePresence mode="wait">
        <Routes>
          <Route path="/" element={<StartPage />} />
          <Route path="/home" element={<HomePage />} />
          <Route path="/login" element={<StartPage />} />
          <Route path="/body-details" element={<BodyDetails />} />
          <Route path="/face-details" element={<FaceDetails />} />
          <Route path="/preferences" element={<Preferences />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/support" element={<Support />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AnimatePresence>
    </Router>
  );
}

export default App;