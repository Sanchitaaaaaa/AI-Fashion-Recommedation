import React from "react";
import { motion } from "framer-motion";
import fashionVideo from "../assets/fashion.mp4";
import { useNavigate } from "react-router-dom";

const HomePage = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-rose-50 via-pink-50 to-rose-100 flex flex-col items-center justify-center px-6 py-10 text-center">
      
      {/* Heading */}
      <motion.h1
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="text-4xl md:text-5xl lg:text-6xl font-extrabold text-gray-900 mb-4"
      >
        AI Fashion Recommender
      </motion.h1>

      {/* Subtitle */}
      <motion.p
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2, duration: 0.8 }}
        className="text-gray-700 text-base md:text-lg lg:text-xl mb-10 max-w-2xl leading-relaxed"
      >
        Discover your style with{" "}
        <span className="text-pink-600 font-semibold">
          AI-powered fashion insights
        </span>{" "}
        — tailored just for you.
      </motion.p>

      {/* Video Container */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.4, duration: 0.8 }}
        className="relative w-full max-w-1xl rounded-2xl overflow-hidden shadow-xl border border-pink-200"
      >
        <video
          src={fashionVideo}
          autoPlay
          loop
          muted
          playsInline
          className="w-full h-[220px] md:h-[350px] lg:h-[400px] object-cover rounded-3xl"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/30 via-transparent to-transparent rounded-3xl"></div>
      </motion.div>

      {/* Button */}
      <motion.div
        initial={{ opacity: 0, y: 25 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8, duration: 0.7 }}
        className="mt-10"
      >
        <motion.button
          whileHover={{ scale: 1.07 }}
          whileTap={{ scale: 0.96 }}
          onClick={() => navigate("/login")}
          className="bg-gradient-to-r from-pink-500 via-rose-500 to-red-400 text-white font-bold text-lg md:text-xl px-10 py-4 rounded-full shadow-lg hover:shadow-pink-300 transition-all duration-300"
        >
          Login / Sign Up
        </motion.button>
      </motion.div>
    </div>
  );
};

export default HomePage;
