import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useNavigate } from "react-router-dom";
import {
  SignedIn,
  SignedOut,
  useUser,
  SignInButton,
} from "@clerk/clerk-react";
import fashionVideo from "../assets/fashion.mp4";
import {
  Upload,
  CheckCircle,
  Loader,
  AlertCircle,
} from "lucide-react";
import { useAuth } from "@clerk/clerk-react";
import LoadingSpinner from "../components/LoadingSpinner";
import Header from "../components/header";
import Sidebar from "../components/sidebar";
import axios from "axios";

const HomePage = () => {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const { isLoaded, isSignedIn } = useAuth();
  const [prevSignedIn, setPrevSignedIn] = useState(null);

  useEffect(() => {
    if (isLoaded && prevSignedIn !== null) {
      if (isSignedIn && !prevSignedIn) {
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

  // Handle file selection
  const handleFile = (f) => {
    if (f && f.type.startsWith("image/")) {
      setFile(f);
      setPreview(URL.createObjectURL(f));
      setUploadStatus(null);
    } else {
      setUploadStatus("error");
      setTimeout(() => setUploadStatus(null), 3000);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  // Upload photo
  const handleUpload = async () => {
    if (!file) {
      setUploadStatus("error");
      return;
    }

    setUploadLoading(true);
    const formData = new FormData();
    formData.append("file", file);
    formData.append("user_id", "default_user");

    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/user/upload",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      if (response.data.success) {
        setUploadStatus("success");
        displayToast("Image uploaded! Redirecting to recommendations...");

        setTimeout(() => {
          // Redirect to recommendations page
          navigate("/recommendations", {
            state: {
              selectedImageId: response.data.imageId,
              selectedDetails: {
                body_type: response.data.body_type,
                body_type_confidence: response.data.body_type_confidence,
                skin_tone: response.data.skin_tone,
                skin_tone_confidence: response.data.skin_tone_confidence,
              },
            },
          });

          // Reset form
          setFile(null);
          setPreview(null);
          setUploadStatus(null);
        }, 1500);
      }
    } catch (error) {
      console.error("Upload error:", error);
      setUploadStatus("error");
      displayToast("Upload failed. Please try again.");
    } finally {
      setUploadLoading(false);
    }
  };

  const toggleSidebar = () => setSidebarOpen(!sidebarOpen);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-rose-50 to-pink-50 relative overflow-hidden flex flex-col">
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
      <div
        className="absolute bottom-0 left-0 w-72 sm:w-96 h-72 sm:h-96 bg-rose-200 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse"
        style={{ animationDelay: "700ms" }}
      ></div>

      {/* HEADER - Only when signed in */}
      <SignedIn>
        <Header
          onMenuClick={toggleSidebar}
          filters={{}}
          onFilterChange={() => {}}
          selectedOccasion="all"
          onOccasionChange={() => {}}
        />
      </SignedIn>

      {/* SIDEBAR */}
      <SignedIn>
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      </SignedIn>

      {/* MAIN CONTENT */}
      <div className="relative z-10 flex-1 flex flex-col items-center justify-center px-4 sm:px-6 py-8 sm:py-12 text-center overflow-y-auto">
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

        <SignedOut>
          {/* Video - Only for signed out users */}
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
            </div>
          </motion.div>
        </SignedOut>

        {/* SIGNED IN - Upload Section Only */}
        <SignedIn>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="w-full max-w-2xl"
          >
            <div className="bg-white rounded-3xl shadow-xl p-8">
              {!preview ? (
                <div
                  onDragEnter={handleDrag}
                  onDragLeave={handleDrag}
                  onDragOver={handleDrag}
                  onDrop={handleDrop}
                  className={`border-3 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all ${
                    dragActive
                      ? "border-purple-500 bg-purple-50"
                      : "border-gray-300 hover:border-purple-400"
                  }`}
                >
                  <input
                    type="file"
                    accept="image/*"
                    onChange={(e) => handleFile(e.target.files?.[0])}
                    className="hidden"
                    id="file-input"
                  />
                  <label htmlFor="file-input" className="cursor-pointer block">
                    <motion.div
                      animate={{ y: [0, -10, 0] }}
                      transition={{ duration: 2, repeat: Infinity }}
                      className="flex justify-center mb-4"
                    >
                      <div className="w-20 h-20 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center">
                        <Upload className="w-10 h-10 text-white" />
                      </div>
                    </motion.div>

                    <h3 className="text-2xl font-bold text-gray-900 mb-2">
                      Drop your photo here
                    </h3>
                    <p className="text-gray-600 mb-2">or click to select</p>
                    <p className="text-sm text-gray-500">
                      Full-body photo • JPG, PNG
                    </p>
                  </label>
                </div>
              ) : (
                <div className="space-y-6">
                  <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="relative rounded-2xl overflow-hidden border-4 border-purple-200"
                  >
                    <img
                      src={preview}
                      alt="Preview"
                      className="w-full h-64 sm:h-96 object-cover"
                    />
                  </motion.div>

                  <div className="flex gap-3">
                    <button
                      onClick={() => {
                        setFile(null);
                        setPreview(null);
                      }}
                      className="flex-1 px-6 py-3 border-2 border-gray-300 text-gray-700 font-semibold rounded-xl hover:bg-gray-50 transition"
                    >
                      Change Photo
                    </button>

                    <motion.button
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={handleUpload}
                      disabled={uploadLoading}
                      className={`flex-1 px-6 py-3 font-semibold rounded-xl text-white transition flex items-center justify-center gap-2 ${
                        uploadLoading
                          ? "bg-gray-400"
                          : "bg-gradient-to-r from-purple-500 to-pink-500 hover:shadow-lg"
                      }`}
                    >
                      {uploadLoading ? (
                        <>
                          <Loader className="w-5 h-5 animate-spin" />
                          Analyzing...
                        </>
                      ) : (
                        <>
                          <CheckCircle className="w-5 h-5" />
                          Upload & Analyze
                        </>
                      )}
                    </motion.button>
                  </div>
                </div>
              )}

              {uploadStatus === "success" && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-4 p-4 bg-green-100 border border-green-400 text-green-700 rounded-lg text-center"
                >
                  ✅ Photo uploaded! Redirecting to recommendations...
                </motion.div>
              )}

              {uploadStatus === "error" && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg flex items-center gap-2"
                >
                  <AlertCircle className="w-5 h-5" />
                  <span>Please select a valid image</span>
                </motion.div>
              )}
            </div>
          </motion.div>
        </SignedIn>

        {/* CTA for Signed Out */}
        <SignedOut>
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8 }}
            className="px-4"
          >
            <SignInButton mode="modal" afterSignInUrl="/home">
              <motion.button
                whileHover={{ scale: 1.05, y: -2 }}
                whileTap={{ scale: 0.95 }}
                className="group relative bg-gradient-to-r from-pink-500 via-rose-500 to-red-400 text-white font-bold text-lg px-12 py-4 rounded-full shadow-xl hover:shadow-2xl transition-all overflow-hidden"
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
              </motion.button>
            </SignInButton>
          </motion.div>
        </SignedOut>

        {/* Tips */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mt-12 grid grid-cols-1 sm:grid-cols-3 gap-4"
        >
          {[
            { icon: "📸", title: "Full Body", desc: "Show full body in photo" },
            { icon: "💡", title: "Good Light", desc: "Natural lighting works best" },
            { icon: "😊", title: "Face Visible", desc: "Face needed for skin tone" }
          ].map((tip, i) => (
            <motion.div
              key={i}
              whileHover={{ y: -5 }}
              className="bg-white rounded-xl p-4 text-center shadow-sm border border-gray-100"
            >
              <p className="text-3xl mb-2">{tip.icon}</p>
              <p className="font-semibold text-gray-900 text-sm">{tip.title}</p>
              <p className="text-xs text-gray-600 mt-1">{tip.desc}</p>
            </motion.div>
          ))}
        </motion.div>

        {/* Feature Pills */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
          className="flex flex-wrap gap-3 justify-center mt-8 sm:mt-12 max-w-2xl px-4"
        >
          {["AI Powered", "Personalized", "Trendy Styles", "Smart Picks"].map(
            (feature, index) => (
              <motion.span
                key={feature}
                initial={{ opacity: 0, scale: 0 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 1.2 + index * 0.1 }}
                className="px-4 py-2 bg-white/80 backdrop-blur-sm rounded-full text-sm font-medium text-gray-700 shadow-md"
              >
                {feature}
              </motion.span>
            )
          )}
        </motion.div>
      </div>
    </div>
  );
};

export default HomePage;