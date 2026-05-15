import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { SignedIn, SignedOut, SignInButton } from "@clerk/clerk-react";
import fashionVideo from "../assets/fashion.mp4";
import { Upload, CheckCircle, Loader, AlertCircle } from "lucide-react";
import { useAuth } from "@clerk/clerk-react";
import LoadingSpinner from "../components/LoadingSpinner";
import Header from "../components/header";
import Sidebar from "../components/sidebar";
import axios from "axios";

// ── Gender Card ────────────────────────────────────────────────────────────
function GenderCard({ value, label, emoji, selected, onClick }) {
  return (
    <motion.button
      whileHover={{ scale: 1.04 }}
      whileTap={{ scale: 0.97 }}
      onClick={() => onClick(value)}
      className={`flex-1 flex flex-col items-center gap-2 py-6 rounded-2xl border-2 font-semibold transition-all
        ${selected
          ? "border-purple-500 bg-gradient-to-br from-purple-50 to-pink-50 text-purple-700 shadow-md"
          : "border-gray-200 bg-white text-gray-600 hover:border-purple-300 hover:bg-purple-50"
        }`}
    >
      <span className="text-4xl">{emoji}</span>
      <span className="text-base">{label}</span>
      {selected && <span className="w-2.5 h-2.5 rounded-full bg-purple-500" />}
    </motion.button>
  );
}

const HomePage = () => {
  const navigate = useNavigate();

  // form state
  const [file,          setFile]          = useState(null);
  const [preview,       setPreview]       = useState(null);
  const [gender,        setGender]        = useState(null);   // "Male" | "Female"
  const [step,          setStep]          = useState("gender"); // "gender" | "upload"
  const [uploadLoading, setUploadLoading] = useState(false);
  const [uploadStatus,  setUploadStatus]  = useState(null);
  const [dragActive,    setDragActive]    = useState(false);

  // toast
  const [showToast,    setShowToast]    = useState(false);
  const [toastMessage, setToastMessage] = useState("");

  // sidebar
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const { isLoaded, isSignedIn } = useAuth();
  const [prevSignedIn, setPrevSignedIn] = useState(null);

  useEffect(() => {
    if (isLoaded && prevSignedIn !== null && isSignedIn && !prevSignedIn) {
      displayToast("Welcome back! You're successfully logged in.");
    }
    if (isLoaded) setPrevSignedIn(isSignedIn);
  }, [isLoaded, isSignedIn]);

  const displayToast = (msg) => {
    setToastMessage(msg);
    setShowToast(true);
    setTimeout(() => setShowToast(false), 3000);
  };

  if (!isLoaded) return <LoadingSpinner />;

  // ── File helpers ──────────────────────────────────────────────────────────
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
    e.preventDefault(); e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") setDragActive(true);
    else if (e.type === "dragleave") setDragActive(false);
  };

  const handleDrop = (e) => {
    e.preventDefault(); e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files?.[0]) handleFile(e.dataTransfer.files[0]);
  };

  // ── Step 1 confirm ────────────────────────────────────────────────────────
  const handleGenderConfirm = () => {
    if (!gender) { displayToast("Please select your gender first."); return; }
    setStep("upload");
  };

  // ── Upload ────────────────────────────────────────────────────────────────
  const handleUpload = async () => {
    if (!file)   { setUploadStatus("error"); return; }
    if (!gender) { setStep("gender"); displayToast("Please select gender first."); return; }

    setUploadLoading(true);
    const formData = new FormData();
    formData.append("file", file);
    formData.append("user_id", "default_user");

    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/user/upload",
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );

      if (response.data.success) {
        setUploadStatus("success");
        displayToast("Image uploaded! Redirecting...");

        setTimeout(() => {
          navigate("/recommendations", {
            state: {
              selectedImageId: response.data.imageId,
              selectedDetails: {
                body_type:            response.data.body_type,
                body_type_confidence: response.data.body_type_confidence,
                skin_tone:            response.data.skin_tone,
                skin_tone_confidence: response.data.skin_tone_confidence,
                gender,                        // ← critical: passed to recommendations
              },
            },
          });
          setFile(null); setPreview(null); setUploadStatus(null);
        }, 1500);
      }
    } catch (err) {
      console.error("Upload error:", err);
      setUploadStatus("error");
      displayToast("Upload failed. Please try again.");
    } finally {
      setUploadLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-rose-50 to-pink-50 relative overflow-hidden flex flex-col">

      {/* Toast */}
      <AnimatePresence>
        {showToast && (
          <motion.div
            initial={{ opacity: 0, y: -50 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -50 }}
            className="fixed top-4 left-1/2 -translate-x-1/2 z-50 flex items-center gap-3 bg-white shadow-2xl rounded-full px-6 py-3 border border-green-200"
          >
            <CheckCircle className="w-5 h-5 text-green-500" />
            <p className="text-gray-800 font-medium">{toastMessage}</p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* BG blobs */}
      <div className="absolute top-0 right-0 w-72 sm:w-96 h-72 sm:h-96 bg-pink-200 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse" />
      <div className="absolute bottom-0 left-0 w-72 sm:w-96 h-72 sm:h-96 bg-rose-200 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse" style={{ animationDelay: "700ms" }} />

      {/* Header / Sidebar */}
      <SignedIn>
        <Header onMenuClick={() => setSidebarOpen(!sidebarOpen)} filters={{}} onFilterChange={() => {}} selectedOccasion="all" onOccasionChange={() => {}} />
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      </SignedIn>

      {/* Content */}
      <div className="relative z-10 flex-1 flex flex-col items-center justify-center px-4 sm:px-6 py-8 sm:py-12 text-center overflow-y-auto">

        {/* Hero */}
        <motion.div initial={{ opacity: 0, y: -30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8 }} className="space-y-4 mb-6 sm:mb-8">
          <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-black text-gray-900 tracking-tight px-4">
            AI Fashion
            <span className="block text-transparent bg-clip-text bg-gradient-to-r from-pink-500 via-rose-500 to-red-400">Recommender</span>
          </h1>
        </motion.div>

        <motion.p initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3, duration: 0.8 }}
          className="text-gray-600 text-base sm:text-lg md:text-xl max-w-2xl mb-8 sm:mb-12 leading-relaxed px-4">
          Discover your unique style with{" "}
          <span className="font-semibold text-pink-600">AI-powered insights</span>{" "}tailored just for you
        </motion.p>

        {/* Signed out — video */}
        <SignedOut>
          <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.5 }}
            className="w-full max-w-2xl mb-8 rounded-2xl overflow-hidden shadow-2xl">
            <video src={fashionVideo} controls autoPlay muted loop playsInline
              className="w-full h-[250px] sm:h-[300px] md:h-[400px] lg:h-[500px] object-cover" />
          </motion.div>
        </SignedOut>

        {/* Signed in — 2-step flow */}
        <SignedIn>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }} className="w-full max-w-2xl">
            <div className="bg-white rounded-3xl shadow-xl p-8">

              {/* Step indicator */}
              <div className="flex items-center gap-2 mb-8">
                {[{ label: "Select Gender", key: "gender" }, { label: "Upload Photo", key: "upload" }].map((s, i) => {
                  const active = step === s.key;
                  const done   = i === 0 && step === "upload";
                  return (
                    <React.Fragment key={s.key}>
                      <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-bold transition-all
                        ${done ? "bg-green-100 text-green-700" : active ? "bg-purple-100 text-purple-700" : "bg-gray-100 text-gray-400"}`}>
                        <span className={`w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold
                          ${done ? "bg-green-500 text-white" : active ? "bg-purple-500 text-white" : "bg-gray-300 text-white"}`}>
                          {done ? "✓" : i + 1}
                        </span>
                        {s.label}
                      </div>
                      {i === 0 && <div className={`flex-1 h-0.5 rounded-full transition-all ${step === "upload" ? "bg-purple-300" : "bg-gray-200"}`} />}
                    </React.Fragment>
                  );
                })}
              </div>

              <AnimatePresence mode="wait">

                {/* ── STEP 1: Gender ─────────────────────────────────────────── */}
                {step === "gender" && (
                  <motion.div key="gender" initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 20 }} transition={{ duration: 0.25 }}>
                    <h3 className="text-xl font-bold text-gray-900 mb-1 text-left">Who are we styling today?</h3>
                    <p className="text-sm text-gray-500 mb-6 text-left">
                      This ensures you only see <span className="font-semibold text-purple-600">Men's</span> or <span className="font-semibold text-pink-600">Women's</span> clothing.
                    </p>

                    <div className="flex gap-4 mb-8">
                      <GenderCard value="Female" label="Women" emoji="👩" selected={gender === "Female"} onClick={setGender} />
                      <GenderCard value="Male"   label="Men"   emoji="👨" selected={gender === "Male"}   onClick={setGender} />
                    </div>

                    <motion.button
                      whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
                      onClick={handleGenderConfirm}
                      disabled={!gender}
                      className={`w-full py-3.5 rounded-xl font-bold text-white transition-all
                        ${gender ? "bg-gradient-to-r from-purple-500 to-pink-500 hover:shadow-lg" : "bg-gray-300 cursor-not-allowed"}`}
                    >
                      Continue →
                    </motion.button>
                  </motion.div>
                )}

                {/* ── STEP 2: Upload ─────────────────────────────────────────── */}
                {step === "upload" && (
                  <motion.div key="upload" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} transition={{ duration: 0.25 }}>

                    {/* Gender badge */}
                    <div className="flex items-center justify-between mb-6">
                      <div className="flex items-center gap-2 px-3 py-1.5 bg-purple-50 border border-purple-200 rounded-full">
                        <span>{gender === "Female" ? "👩" : "👨"}</span>
                        <span className="text-sm font-semibold text-purple-700">
                          Styling for {gender === "Female" ? "Women" : "Men"}
                        </span>
                      </div>
                      <button onClick={() => { setStep("gender"); setFile(null); setPreview(null); }}
                        className="text-xs text-gray-400 hover:text-purple-600 underline transition-colors">
                        Change
                      </button>
                    </div>

                    {!preview ? (
                      <div onDragEnter={handleDrag} onDragLeave={handleDrag} onDragOver={handleDrag} onDrop={handleDrop}
                        className={`border-3 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all
                          ${dragActive ? "border-purple-500 bg-purple-50" : "border-gray-300 hover:border-purple-400"}`}>
                        <input type="file" accept="image/*" onChange={(e) => handleFile(e.target.files?.[0])} className="hidden" id="file-input" />
                        <label htmlFor="file-input" className="cursor-pointer block">
                          <motion.div animate={{ y: [0, -10, 0] }} transition={{ duration: 2, repeat: Infinity }} className="flex justify-center mb-4">
                            <div className="w-20 h-20 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center">
                              <Upload className="w-10 h-10 text-white" />
                            </div>
                          </motion.div>
                          <h3 className="text-2xl font-bold text-gray-900 mb-2">Drop your photo here</h3>
                          <p className="text-gray-600 mb-2">or click to select</p>
                          <p className="text-sm text-gray-500">Full-body photo • JPG, PNG</p>
                        </label>
                      </div>
                    ) : (
                      <div className="space-y-6">
                        <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }}
                          className="relative rounded-2xl overflow-hidden border-4 border-purple-200">
                          <img src={preview} alt="Preview" className="w-full max-h-[500px] object-contain bg-gray-50" />
                        </motion.div>
                        <div className="flex gap-3">
                          <button onClick={() => { setFile(null); setPreview(null); }}
                            className="flex-1 px-6 py-3 border-2 border-gray-300 text-gray-700 font-semibold rounded-xl hover:bg-gray-50 transition">
                            Change Photo
                          </button>
                          <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
                            onClick={handleUpload} disabled={uploadLoading}
                            className={`flex-1 px-6 py-3 font-semibold rounded-xl text-white transition flex items-center justify-center gap-2
                              ${uploadLoading ? "bg-gray-400" : "bg-gradient-to-r from-purple-500 to-pink-500 hover:shadow-lg"}`}>
                            {uploadLoading
                              ? <><Loader className="w-5 h-5 animate-spin" /> Analyzing...</>
                              : <><CheckCircle className="w-5 h-5" /> Upload &amp; Analyze</>}
                          </motion.button>
                        </div>
                      </div>
                    )}

                    {uploadStatus === "success" && (
                      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                        className="mt-4 p-4 bg-green-100 border border-green-400 text-green-700 rounded-lg text-center">
                        ✅ Photo uploaded! Redirecting to recommendations...
                      </motion.div>
                    )}
                    {uploadStatus === "error" && (
                      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                        className="mt-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg flex items-center gap-2">
                        <AlertCircle className="w-5 h-5" />
                        <span>Please select a valid image</span>
                      </motion.div>
                    )}
                  </motion.div>
                )}

              </AnimatePresence>
            </div>
          </motion.div>
        </SignedIn>

        {/* CTA signed out */}
        <SignedOut>
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.8 }} className="px-4">
            <SignInButton mode="modal" afterSignInUrl="/home">
              <motion.button whileHover={{ scale: 1.05, y: -2 }} whileTap={{ scale: 0.95 }}
                className="bg-gradient-to-r from-pink-500 via-rose-500 to-red-400 text-white font-bold text-lg px-12 py-4 rounded-full shadow-xl hover:shadow-2xl transition-all">
                <span className="flex items-center gap-2">
                  Get Started
                  <motion.span animate={{ x: [0, 5, 0] }} transition={{ duration: 1.5, repeat: Infinity }}>→</motion.span>
                </span>
              </motion.button>
            </SignInButton>
          </motion.div>
        </SignedOut>

        {/* Tips */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
          className="mt-12 grid grid-cols-1 sm:grid-cols-3 gap-4">
          {[
            { icon: "📸", title: "Full Body",    desc: "Show full body in photo" },
            { icon: "💡", title: "Good Light",   desc: "Natural lighting works best" },
            { icon: "😊", title: "Face Visible", desc: "Face needed for skin tone" },
          ].map((tip, i) => (
            <motion.div key={i} whileHover={{ y: -5 }} className="bg-white rounded-xl p-4 text-center shadow-sm border border-gray-100">
              <p className="text-3xl mb-2">{tip.icon}</p>
              <p className="font-semibold text-gray-900 text-sm">{tip.title}</p>
              <p className="text-xs text-gray-600 mt-1">{tip.desc}</p>
            </motion.div>
          ))}
        </motion.div>

        {/* Feature pills */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1 }}
          className="flex flex-wrap gap-3 justify-center mt-8 sm:mt-12 max-w-2xl px-4">
          {["AI Powered", "Gender-Aware", "Personalized", "Trendy Styles"].map((f, i) => (
            <motion.span key={f} initial={{ opacity: 0, scale: 0 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 1.2 + i * 0.1 }}
              className="px-4 py-2 bg-white/80 backdrop-blur-sm rounded-full text-sm font-medium text-gray-700 shadow-md">
              {f}
            </motion.span>
          ))}
        </motion.div>

      </div>
    </div>
  );
};

export default HomePage;