import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useNavigate } from "react-router-dom";
import fashionVideo from "../assets/fashion.mp4";
import { Menu, X, Sparkles, LogIn, Home, Info, Mail } from "lucide-react";

const HomePage = () => {
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const toggleSidebar = () => setSidebarOpen(!sidebarOpen);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-rose-50 to-pink-50 relative overflow-hidden">
      
      {/* Decorative Background Elements */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-pink-200 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse"></div>
      <div className="absolute bottom-0 left-0 w-96 h-96 bg-rose-200 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse" style={{animationDelay: '700ms'}}></div>

      {/* Top Navigation Bar */}
      <nav className="relative z-20 px-6 py-4 flex items-center justify-between">
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={toggleSidebar}
          className="p-2 rounded-lg bg-white/80 backdrop-blur-sm shadow-md hover:shadow-lg transition-all"
        >
          <Menu className="w-6 h-6 text-gray-800" />
        </motion.button>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="flex items-center gap-2 bg-white/80 backdrop-blur-sm px-4 py-2 rounded-full shadow-md"
        >
          <Sparkles className="w-5 h-5 text-pink-500" />
          <span className="font-bold text-gray-800 hidden sm:inline">AI Fashion</span>
        </motion.div>
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
            className="fixed left-0 top-0 h-full w-80 bg-white shadow-2xl z-40 flex flex-col"
          >
            {/* Sidebar Header */}
            <div className="p-6 border-b border-gray-100 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-gradient-to-br from-pink-500 to-rose-500 rounded-xl flex items-center justify-center shadow-lg">
                  <Sparkles className="w-7 h-7 text-white" />
                </div>
                <div>
                  <h2 className="font-bold text-gray-900 text-lg">AI Fashion</h2>
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

            {/* Sidebar Menu */}
            <div className="flex-1 p-6 space-y-2">
              <SidebarLink icon={Home} text="Home" onClick={toggleSidebar} />
              <SidebarLink icon={Info} text="About" onClick={toggleSidebar} />
              <SidebarLink icon={Mail} text="Contact" onClick={toggleSidebar} />
            </div>

            {/* Sidebar Footer - Login Button */}
            <div className="p-6 border-t border-gray-100">
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => {
                  toggleSidebar();
                  navigate("/login");
                }}
                className="w-full bg-gradient-to-r from-pink-500 via-rose-500 to-red-400 text-white font-semibold py-3 rounded-xl shadow-lg hover:shadow-xl transition-all flex items-center justify-center gap-2"
              >
                <LogIn className="w-5 h-5" />
                Login / Sign Up
              </motion.button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <div className="relative z-10 flex flex-col items-center justify-center min-h-[calc(100vh-80px)] px-6 py-12 text-center">
        
        {/* Hero Heading */}
        <motion.div
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="space-y-4 mb-8"
        >
          <h1 className="text-5xl md:text-6xl lg:text-7xl font-black text-gray-900 tracking-tight">
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
            <div className="h-1 w-12 bg-gradient-to-r from-pink-500 to-rose-500 rounded-full"></div>
            <Sparkles className="w-5 h-5 text-pink-500" />
            <div className="h-1 w-12 bg-gradient-to-r from-rose-500 to-red-400 rounded-full"></div>
          </motion.div>
        </motion.div>

        {/* Subtitle */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.8 }}
          className="text-gray-600 text-lg md:text-xl max-w-2xl mb-12 leading-relaxed"
        >
          Discover your unique style with{" "}
          <span className="font-semibold text-pink-600">AI-powered insights</span>
          {" "}tailored just for you
        </motion.p>

        {/* Video/Image Showcase */}
        {/* Video/Image Showcase */}
<motion.div
  initial={{ opacity: 0, scale: 0.9 }}
  animate={{ opacity: 1, scale: 1 }}
  transition={{ delay: 0.5, duration: 0.8 }}
  className="relative w-full max-w-4xl mb-12"
>
  <div className="relative rounded-3xl overflow-hidden shadow-2xl border border-white/50">
    {/* Replace with your video */}
    <video
      src={fashionVideo}
      controls
      autoPlay
      muted
      loop
      className="w-full h-[300px] md:h-[400px] lg:h-[500px] object-cover"
    >
      Your browser does not support the video tag.
    </video>

    {/* Overlay gradient */}
    <div className="absolute inset-0 bg-gradient-to-t from-black/20 via-transparent to-transparent"></div>
  </div>

  {/* Floating decoration cards */}
  <motion.div
    animate={{ y: [0, -10, 0] }}
    transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
    className="absolute -top-6 -left-6 bg-white p-4 rounded-2xl shadow-xl hidden lg:block"
  >
    <p className="text-4xl">👗</p>
  </motion.div>
  <motion.div
    animate={{ y: [0, 10, 0] }}
    transition={{ duration: 3, repeat: Infinity, ease: "easeInOut", delay: 1 }}
    className="absolute -bottom-6 -right-6 bg-white p-4 rounded-2xl shadow-xl hidden lg:block"
  >
    <p className="text-4xl">👠</p>
  </motion.div>
</motion.div>


        {/* CTA Button */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8, duration: 0.7 }}
        >
          <motion.button
            whileHover={{ scale: 1.05, y: -2 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => navigate("/login")}
            className="group relative bg-gradient-to-r from-pink-500 via-rose-500 to-red-400 text-white font-bold text-lg px-12 py-4 rounded-full shadow-xl hover:shadow-2xl transition-all duration-300 overflow-hidden"
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
        </motion.div>

        {/* Feature Pills */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1, duration: 0.8 }}
          className="flex flex-wrap gap-3 justify-center mt-12 max-w-2xl"
        >
          {["AI Powered", "Personalized", "Trendy Styles", "Smart Picks"].map((feature, index) => (
            <motion.span
              key={feature}
              initial={{ opacity: 0, scale: 0 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 1.2 + index * 0.1 }}
              className="px-4 py-2 bg-white/80 backdrop-blur-sm rounded-full text-sm font-medium text-gray-700 shadow-md"
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
    className="w-full flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-gray-50 transition-colors text-left group"
  >
    <Icon className="w-5 h-5 text-gray-400 group-hover:text-pink-500 transition-colors" />
    <span className="text-gray-700 font-medium group-hover:text-gray-900">{text}</span>
  </motion.button>
);

export default HomePage;