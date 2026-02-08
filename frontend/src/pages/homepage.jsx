import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { 
  SignedIn, 
  SignedOut, 
  UserButton, 
  useUser,
  SignInButton,
  SignUpButton 
} from "@clerk/clerk-react";
import fashionVideo from "../assets/fashion.mp4";
import { 
  Menu, 
  X, 
  Sparkles, 
  LogIn, 
  Home, 
  Info, 
  Mail, 
  User, 
  Settings,
  Upload,
  Lock,
  CheckCircle
} from "lucide-react";
import { useAuth } from "@clerk/clerk-react";
import LoadingSpinner from '../components/LoadingSpinner';

const HomePage = () => {
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState("");
  const { user } = useUser();
  const { isLoaded, isSignedIn } = useAuth();
  
  // Track previous auth state to detect login
  const [prevSignedIn, setPrevSignedIn] = useState(null);

  useEffect(() => {
    if (isLoaded && prevSignedIn !== null) {
      if (isSignedIn && !prevSignedIn) {
        // User just logged in
        displayToast("Welcome back! You're successfully logged in.");
      }
    }
    if (isLoaded) {
      setPrevSignedIn(isSignedIn);
    }
  }, [isLoaded, isSignedIn]);

  const displayToast = (message) => {
    setToastMessage(message);
    setShowToast(true);
    setTimeout(() => {
      setShowToast(false);
    }, 3000);
  };

  if (!isLoaded) {
    return <LoadingSpinner />;
  }

  const toggleSidebar = () => setSidebarOpen(!sidebarOpen);

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setUploadedFile(file);
      console.log("File uploaded:", file.name);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-rose-50 to-pink-50 relative overflow-hidden">
      
      {/* Toast Notification */}
      <AnimatePresence>
        {showToast && (
          <motion.div
            initial={{ opacity: 0, y: -50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -50 }}
            className="fixed top-4 left-1/2 transform -translate-x-1/2 z-50 flex items-center gap-3 bg-white shadow-2xl rounded-full px-6 py-3 border border-green-200"
          >
            <CheckCircle className="w-5 h-5 text-green-500" />
            <p className="text-gray-800 font-medium">{toastMessage}</p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Decorative Background Elements */}
      <div className="absolute top-0 right-0 w-72 sm:w-96 h-72 sm:h-96 bg-pink-200 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse"></div>
      <div className="absolute bottom-0 left-0 w-72 sm:w-96 h-72 sm:h-96 bg-rose-200 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse" style={{animationDelay: '700ms'}}></div>

      {/* Top Navigation Bar */}
      <nav className="relative z-20 px-4 sm:px-6 py-4 flex items-center justify-between">
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={toggleSidebar}
          className="p-2 rounded-lg bg-white/80 backdrop-blur-sm shadow-md hover:shadow-lg transition-all"
        >
          <Menu className="w-5 h-5 sm:w-6 sm:h-6 text-gray-800" />
        </motion.button>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="flex items-center gap-2 bg-white/80 backdrop-blur-sm px-3 sm:px-4 py-2 rounded-full shadow-md"
        >
          <Sparkles className="w-4 h-4 sm:w-5 sm:h-5 text-pink-500" />
          <span className="font-bold text-gray-800 text-sm sm:text-base hidden sm:inline">AI Fashion</span>
        </motion.div>

        {/* User Button - Only show when signed in */}
        <SignedIn>
          <div className="flex items-center gap-3">
            <UserButton 
              appearance={{
                elements: {
                  avatarBox: "w-9 h-9 sm:w-10 sm:h-10"
                }
              }}
            />
          </div>
        </SignedIn>

        <SignedOut>
          <div className="w-9 sm:w-10"></div>
        </SignedOut>
      </nav>

      {/* Sidebar Overlay */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            onClick={toggleSidebar}
            className="fixed inset-0 bg-black/40 backdrop-blur-sm z-30"
          />
        )}
      </AnimatePresence>

      {/* Sliding Sidebar */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ x: -320 }}
            animate={{ x: 0 }}
            exit={{ x: -320 }}
            transition={{ type: "spring", damping: 25, stiffness: 200 }}
            className="fixed left-0 top-0 h-full w-72 sm:w-80 bg-white shadow-2xl z-40 flex flex-col"
          >
            {/* Sidebar Header */}
            <div className="p-4 sm:p-6 border-b border-gray-100 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 sm:w-12 sm:h-12 bg-gradient-to-br from-pink-500 to-rose-500 rounded-xl flex items-center justify-center shadow-lg">
                  <Sparkles className="w-6 h-6 sm:w-7 sm:h-7 text-white" />
                </div>
                <div>
                  <h2 className="font-bold text-gray-900 text-base sm:text-lg">AI Fashion</h2>
                  <p className="text-xs text-gray-500">Style Recommender</p>
                </div>
              </div>
              <button
                onClick={toggleSidebar}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X className="w-5 h-5 text-gray-600" />
              </button>
            </div>

            {/* Sidebar Content - Conditional based on auth */}
            <SignedIn>
              {/* Sidebar Menu - Only visible when logged in */}
              <div className="flex-1 p-4 sm:p-6 space-y-2 overflow-y-auto">
                <SidebarLink 
                  icon={Home} 
                  text="Home" 
                  onClick={() => { toggleSidebar(); navigate("/"); }} 
                />
                <SidebarLink 
                  icon={User} 
                  text="Body Details" 
                  onClick={() => { toggleSidebar(); navigate("/body-details"); }} 
                />
                <SidebarLink 
                  icon={Info} 
                  text="Face Details" 
                  onClick={() => { toggleSidebar(); navigate("/face-details"); }} 
                />
                <SidebarLink 
                  icon={Sparkles} 
                  text="Preferences" 
                  onClick={() => { toggleSidebar(); navigate("/preferences"); }} 
                />
                <SidebarLink 
                  icon={Settings} 
                  text="Settings" 
                  onClick={() => { toggleSidebar(); navigate("/settings"); }} 
                />
                <SidebarLink 
                  icon={Mail} 
                  text="Support" 
                  onClick={() => { toggleSidebar(); navigate("/support"); }} 
                />
              </div>

              {/* User Info */}
              <div className="p-4 sm:p-6 border-t border-gray-100">
                <div className="flex items-center gap-3 mb-4 p-3 bg-gradient-to-r from-pink-50 to-rose-50 rounded-xl">
                  <div className="w-10 h-10 bg-gradient-to-br from-pink-500 to-rose-500 rounded-full flex items-center justify-center">
                    <User className="w-5 h-5 text-white" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-gray-900 truncate">
                      {user?.firstName || user?.emailAddresses[0]?.emailAddress}
                    </p>
                    <p className="text-xs text-gray-500">Premium Member</p>
                  </div>
                </div>
              </div>
            </SignedIn>

            <SignedOut>
              {/* Login Prompt - Only visible when logged out */}
              <div className="flex-1 flex items-center justify-center p-6">
                <div className="text-center space-y-6">
                  <div className="w-20 h-20 mx-auto bg-gradient-to-br from-pink-100 to-rose-100 rounded-full flex items-center justify-center">
                    <Lock className="w-10 h-10 text-pink-500" />
                  </div>
                  <div className="space-y-2">
                    <h3 className="text-lg font-bold text-gray-900">Please Login to Continue</h3>
                    <p className="text-sm text-gray-500 max-w-xs mx-auto">
                      Access personalized fashion recommendations and exclusive features
                    </p>
                  </div>
                  <div className="flex flex-col gap-2 pt-4">
                    <SignInButton 
                      mode="modal"
                      afterSignInUrl="/home"
                      afterSignUpUrl="/home"
                    >
                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        className="w-full bg-gradient-to-r from-pink-500 via-rose-500 to-red-400 text-white font-semibold py-3 rounded-xl shadow-lg hover:shadow-xl transition-all flex items-center justify-center gap-2"
                      >
                        <LogIn className="w-5 h-5" />
                        Sign In
                      </motion.button>
                    </SignInButton>
                    <SignUpButton 
                      mode="modal"
                      afterSignInUrl="/home"
                      afterSignUpUrl="/home"
                    >
                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        className="w-full bg-white text-gray-700 font-semibold py-3 rounded-xl border-2 border-gray-200 hover:border-pink-300 hover:bg-pink-50 transition-all"
                      >
                        Create Account
                      </motion.button>
                    </SignUpButton>
                  </div>
                </div>
              </div>
            </SignedOut>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <div className="relative z-10 flex flex-col items-center justify-center min-h-[calc(100vh-80px)] px-4 sm:px-6 py-8 sm:py-12 text-center">
        
        {/* Hero Heading */}
        <motion.div
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="space-y-4 mb-6 sm:mb-8"
        >
          <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-black text-gray-900 tracking-tight px-4">
            AI Fashion
            <span className="block text-transparent bg-clip-text bg-gradient-to-r from-pink-500 via-rose-500 to-red-400">
              Recommender
            </span>
          </h1>
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.4, type: "spring", stiffness: 200 }}
            className="flex items-center justify-center gap-2"
          >
            <div className="h-1 w-8 sm:w-12 bg-gradient-to-r from-pink-500 to-rose-500 rounded-full"></div>
            <Sparkles className="w-4 h-4 sm:w-5 sm:h-5 text-pink-500" />
            <div className="h-1 w-8 sm:w-12 bg-gradient-to-r from-rose-500 to-red-400 rounded-full"></div>
          </motion.div>
        </motion.div>

        {/* Subtitle */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.8 }}
          className="text-gray-600 text-base sm:text-lg md:text-xl max-w-2xl mb-8 sm:mb-12 leading-relaxed px-4"
        >
          Discover your unique style with{" "}
          <span className="font-semibold text-pink-600">AI-powered insights</span>
          {" "}tailored just for you
        </motion.p>

        {/* Video/Image Showcase */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.5, duration: 0.8 }}
          className="relative w-full max-w-4xl mb-6 sm:mb-8 px-4"
        >
          <div className="relative rounded-2xl sm:rounded-3xl overflow-hidden shadow-2xl border border-white/50">
            <video
              src={fashionVideo}
              controls
              autoPlay
              muted
              loop
              playsInline
              className="w-full h-[250px] sm:h-[300px] md:h-[400px] lg:h-[500px] object-cover"
            >
              Your browser does not support the video tag.
            </video>

            {/* Overlay gradient */}
            <div className="absolute inset-0 bg-gradient-to-t from-black/20 via-transparent to-transparent"></div>
          </div>

          {/* Floating decoration cards - hidden on mobile */}
          <motion.div
            animate={{ y: [0, -10, 0] }}
            transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
            className="absolute -top-4 -left-4 sm:-top-6 sm:-left-6 bg-white p-3 sm:p-4 rounded-xl sm:rounded-2xl shadow-xl hidden md:block"
          >
            <p className="text-3xl sm:text-4xl">👗</p>
          </motion.div>
          <motion.div
            animate={{ y: [0, 10, 0] }}
            transition={{ duration: 3, repeat: Infinity, ease: "easeInOut", delay: 1 }}
            className="absolute -bottom-4 -right-4 sm:-bottom-6 sm:-right-6 bg-white p-3 sm:p-4 rounded-xl sm:rounded-2xl shadow-xl hidden md:block"
          >
            <p className="text-3xl sm:text-4xl">👠</p>
          </motion.div>
        </motion.div>

        {/* Upload Section - Only visible when logged in */}
        <SignedIn>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7, duration: 0.7 }}
            className="w-full max-w-md mb-6 sm:mb-8 px-4"
          >
            <label 
              htmlFor="file-upload"
              className="group cursor-pointer block"
            >
              <div className="relative border-2 border-dashed border-pink-300 hover:border-pink-500 rounded-2xl p-6 sm:p-8 bg-white/50 backdrop-blur-sm hover:bg-white/70 transition-all">
                <input
                  id="file-upload"
                  type="file"
                  accept="image/*"
                  onChange={handleFileUpload}
                  className="hidden"
                />
                <div className="flex flex-col items-center gap-3">
                  <div className="w-12 h-12 sm:w-14 sm:h-14 bg-gradient-to-br from-pink-500 to-rose-500 rounded-full flex items-center justify-center group-hover:scale-110 transition-transform">
                    <Upload className="w-6 h-6 sm:w-7 sm:h-7 text-white" />
                  </div>
                  <div className="text-center">
                    <p className="font-semibold text-gray-900 text-sm sm:text-base">
                      {uploadedFile ? uploadedFile.name : "Upload Your Photo"}
                    </p>
                    <p className="text-xs sm:text-sm text-gray-500 mt-1">
                      Get personalized style recommendations
                    </p>
                  </div>
                </div>
              </div>
            </label>
          </motion.div>
        </SignedIn>

        {/* CTA Button */}
        <SignedOut>
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8, duration: 0.7 }}
            className="px-4"
          >
            <SignInButton mode="modal">
              <motion.button
                whileHover={{ scale: 1.05, y: -2 }}
                whileTap={{ scale: 0.95 }}
                className="group relative bg-gradient-to-r from-pink-500 via-rose-500 to-red-400 text-white font-bold text-base sm:text-lg px-8 sm:px-12 py-3 sm:py-4 rounded-full shadow-xl hover:shadow-2xl transition-all duration-300 overflow-hidden"
              >
                <span className="relative z-10 flex items-center gap-2">
                  Get Started
                  <motion.span
                    animate={{ x: [0, 5, 0] }}
                    transition={{ duration: 1.5, repeat: Infinity }}
                  >
                    →
                  </motion.span>
                </span>
                <div className="absolute inset-0 bg-gradient-to-r from-pink-600 via-rose-600 to-red-500 opacity-0 group-hover:opacity-100 transition-opacity"></div>
              </motion.button>
            </SignInButton>
          </motion.div>
        </SignedOut>

        <SignedIn>
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8, duration: 0.7 }}
            className="px-4"
          >
            <motion.button
              whileHover={{ scale: 1.05, y: -2 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => navigate("/body-details")}
              className="group relative bg-gradient-to-r from-pink-500 via-rose-500 to-red-400 text-white font-bold text-base sm:text-lg px-8 sm:px-12 py-3 sm:py-4 rounded-full shadow-xl hover:shadow-2xl transition-all duration-300 overflow-hidden"
            >
              <span className="relative z-10 flex items-center gap-2">
                Start Your Journey
                <motion.span
                  animate={{ x: [0, 5, 0] }}
                  transition={{ duration: 1.5, repeat: Infinity }}
                >
                  →
                </motion.span>
              </span>
              <div className="absolute inset-0 bg-gradient-to-r from-pink-600 via-rose-600 to-red-500 opacity-0 group-hover:opacity-100 transition-opacity"></div>
            </motion.button>
          </motion.div>
        </SignedIn>

        {/* Feature Pills */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1, duration: 0.8 }}
          className="flex flex-wrap gap-2 sm:gap-3 justify-center mt-8 sm:mt-12 max-w-2xl px-4"
        >
          {["AI Powered", "Personalized", "Trendy Styles", "Smart Picks"].map((feature, index) => (
            <motion.span
              key={feature}
              initial={{ opacity: 0, scale: 0 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 1.2 + index * 0.1 }}
              className="px-3 sm:px-4 py-1.5 sm:py-2 bg-white/80 backdrop-blur-sm rounded-full text-xs sm:text-sm font-medium text-gray-700 shadow-md"
            >
              {feature}
            </motion.span>
          ))}
        </motion.div>
      </div>
    </div>
  );
};

// Sidebar Link Component
const SidebarLink = ({ icon: Icon, text, onClick }) => (
  <motion.button
    whileHover={{ x: 4 }}
    onClick={onClick}
    className="w-full flex items-center gap-3 px-3 sm:px-4 py-2.5 sm:py-3 rounded-xl hover:bg-gray-50 transition-colors text-left group"
  >
    <Icon className="w-4 h-4 sm:w-5 sm:h-5 text-gray-400 group-hover:text-pink-500 transition-colors flex-shrink-0" />
    <span className="text-sm sm:text-base text-gray-700 font-medium group-hover:text-gray-900 truncate">{text}</span>
  </motion.button>
);

export default HomePage;