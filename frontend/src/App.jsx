import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';
import { ClerkProvider } from '@clerk/clerk-react';
import StartPage from './pages/start_page';
import HomePage from './pages/homepage';
// import UploadPage from './pages/upload';
import RecommendationsPage from './pages/recommendations';
import WishlistPage from './components/wishlist';
import UserDetails from './components/user_details';
import Settings from './components/settings';
import Preferences from './components/preferences';
import Support from './components/support';
import Header from './components/header';
import Sidebar from './components/sidebar';
import { useState } from 'react';

const PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;

if (!PUBLISHABLE_KEY) {
  throw new Error("Missing Clerk Publishable Key");
}

function ClerkProviderWithRoutes() {
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [uploadedImages, setUploadedImages] = useState([]);
  const [selectedImageId, setSelectedImageId] = useState(null);
  const [selectedDetails, setSelectedDetails] = useState(null);

  const handleUploadSuccess = (newImage) => {
    setUploadedImages([newImage, ...uploadedImages]);
    setSelectedImageId(newImage.id);
    setSidebarOpen(true);
    navigate('/recommendations');
  };

  const handleSelectImage = (imageId, details) => {
    setSelectedImageId(imageId);
    setSelectedDetails(details);
  };

  const handleDeleteImage = async (imageId) => {
    if (!window.confirm("Delete this image?")) return;

    try {
      await fetch(`http://127.0.0.1:8000/user/images/${imageId}`, {
        method: "DELETE",
      });
      setUploadedImages(uploadedImages.filter((img) => img.id !== imageId));
      if (selectedImageId === imageId) {
        setSelectedImageId(null);
        setSelectedDetails(null);
      }
      alert("Image deleted successfully");
    } catch (error) {
      console.error("Delete error:", error);
      alert("Failed to delete image");
    }
  };

  // Show Header and Sidebar ONLY on upload, recommendations, wishlist, and component pages
  const showHeaderAndSidebar = [
    '/upload',
    '/recommendations',
    '/wishlist',
    '/user-details',
    '/settings',
    '/preferences',
    '/support',
  ].includes(location.pathname);

  return (
    <ClerkProvider 
      publishableKey={PUBLISHABLE_KEY}
      navigate={(to) => navigate(to)}
      afterSignInUrl="/home"
      afterSignUpUrl="/home"
      signInFallbackRedirectUrl="/home"
      signUpFallbackRedirectUrl="/home"
    >
      <div className={`flex h-screen bg-gray-100 overflow-hidden ${!showHeaderAndSidebar ? 'flex-col' : ''}`}>
        {/* Sidebar - Only show on specific pages */}
        {showHeaderAndSidebar && (
          <Sidebar
            isOpen={sidebarOpen}
            onClose={() => setSidebarOpen(false)}
            uploadedImages={uploadedImages}
            selectedImageId={selectedImageId}
            onSelectImage={handleSelectImage}
            onDeleteImage={handleDeleteImage}
          />
        )}

        {/* Main Content */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Header - Only show on specific pages */}
          {showHeaderAndSidebar && (
            <Header
              onMenuClick={() => setSidebarOpen(!sidebarOpen)}
              isSidebarOpen={sidebarOpen}
            />
          )}

          {/* Routes */}
          <main className="flex-1 overflow-y-auto">
            <AnimatePresence mode="wait">
              <Routes>
                {/* Public Routes - NO navbar or sidebar */}
                <Route path="/" element={<StartPage />} />
                <Route path="/home" element={<HomePage />} />
                <Route path="/login" element={<StartPage />} />

                {/* Protected Routes - WITH navbar and sidebar
                <Route 
                  path="/upload" 
                  element={
                    <UploadPage onUploadSuccess={handleUploadSuccess} />
                  } 
                /> */}

                <Route
                  path="/recommendations"
                  element={
                    <RecommendationsPage
                      selectedImageId={selectedImageId}
                      selectedDetails={selectedDetails}
                    />
                  }
                />

                <Route
                  path="/wishlist"
                  element={<WishlistPage />}
                />

                {/* Component Routes - WITH navbar and sidebar */}
                <Route
                  path="/user-details"
                  element={<UserDetails />}
                />

                <Route
                  path="/settings"
                  element={<Settings />}
                />

                <Route
                  path="/preferences"
                  element={<Preferences />}
                />

                <Route
                  path="/support"
                  element={<Support />}
                />

                {/* Fallback */}
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </AnimatePresence>
          </main>
        </div>
      </div>
    </ClerkProvider>
  );
}

function App() {
  return (
    <Router>
      <ClerkProviderWithRoutes />
    </Router>
  );
}

export default App;