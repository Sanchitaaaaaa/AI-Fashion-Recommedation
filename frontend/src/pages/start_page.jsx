import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useState } from 'react';
import fashionImage from '../assets/fashion.jpeg';

const StartPage = () => {
  const navigate = useNavigate();
  const [isExiting, setIsExiting] = useState(false);

  const handleImageClick = () => {
    setIsExiting(true);
    setTimeout(() => {
      navigate('/home');
    }, 600);
  };

  return (
    <motion.div
      initial={{ opacity: 1, scale: 1 }}
      animate={isExiting ? { opacity: 0, scale: 0.5 } : { opacity: 1, scale: 1 }}
      transition={{ duration: 0.6, ease: "easeInOut" }}
      className="min-h-screen w-full flex items-center justify-center bg-gradient-to-br from-purple-50 via-blue-50 to-pink-50 p-4 overflow-hidden"
    >
      <motion.div
        initial={{ opacity: 0, scale: 0.5 }}
        animate={
          isExiting 
            ? { opacity: 0, scale: 1.5, rotate: 10 } 
            : { opacity: 1, scale: 1, rotate: 0 }
        }
        transition={{ duration: 0.6, ease: "easeInOut" }}
        className="relative flex flex-col items-center"
      >
        <motion.div
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={handleImageClick}
          className="cursor-pointer relative group"
        >
          {/* Image Container */}
          <motion.div
            className="relative w-64 h-64 sm:w-80 sm:h-80 md:w-96 md:h-96 rounded-2xl overflow-hidden shadow-2xl"
            whileHover={{ boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.25)" }}
          >
            <img
              src={fashionImage}
              alt="Fashion Store"
              className="w-full h-full object-cover"
            />
            
            {/* Overlay */}
            <motion.div
              initial={{ opacity: 0 }}
              whileHover={{ opacity: 1 }}
              className="absolute inset-0 bg-black bg-opacity-40 flex items-center justify-center"
            >
              <motion.div
                initial={{ y: 20, opacity: 0 }}
                whileHover={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.1 }}
                className="text-center"
              >
                <p className="text-white text-xl sm:text-2xl md:text-3xl font-bold mb-2">
                  Enter Store
                </p>
                <motion.div
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ repeat: Infinity, duration: 1.5 }}
                  className="text-white text-4xl"
                >
                  →
                </motion.div>
              </motion.div>
            </motion.div>
          </motion.div>

          {/* Glow Effect */}
          <motion.div
            className="absolute -inset-1 bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 rounded-2xl opacity-0 group-hover:opacity-30 blur-xl transition-opacity duration-500"
            animate={{ rotate: 360 }}
            transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
          />
        </motion.div>

        {/* Text Below Image */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.5 }}
          className="text-center mt-8"
        >
          <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent mb-2">
            AI Fashion Recommendations
          </h1>
          <p className="text-gray-600 text-sm sm:text-base md:text-lg">
            Click to discover your perfect style
          </p>
        </motion.div>
      </motion.div>

      {/* Floating Particles */}
      {!isExiting && [...Array(6)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute w-2 h-2 bg-purple-400 rounded-full opacity-30"
          animate={{
            x: [0, Math.random() * 100 - 50],
            y: [0, Math.random() * 100 - 50],
            scale: [1, 1.5, 1],
          }}
          transition={{
            duration: 3 + Math.random() * 2,
            repeat: Infinity,
            repeatType: "reverse",
          }}
          style={{
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
          }}
        />
      ))}
    </motion.div>
  );
};

export default StartPage;