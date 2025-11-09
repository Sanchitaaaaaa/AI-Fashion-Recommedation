import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';

const HomePage = () => {
  const navigate = useNavigate();

  return (
    <motion.div
      initial={{ opacity: 0, scale: 1.5 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.5 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      className="min-h-screen w-full bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 p-4 sm:p-6 md:p-8"
    >
      {/* Header */}
      <motion.header
        initial={{ y: -50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="max-w-7xl mx-auto mb-8"
      >
        <div className="flex items-center justify-between">
          <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
            Fashion Hub
          </h1>
          <button
            onClick={() => navigate('/')}
            className="px-4 py-2 bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow text-gray-700 font-medium text-sm sm:text-base"
          >
            ← Back
          </button>
        </div>
      </motion.header>

      {/* Main Content */}
      <motion.main
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
        className="max-w-7xl mx-auto"
      >
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 md:gap-8">
          {[1, 2, 3, 4, 5, 6].map((item, index) => (
            <motion.div
              key={item}
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 + index * 0.1 }}
              whileHover={{ scale: 1.05, y: -10 }}
              className="bg-white rounded-xl shadow-lg overflow-hidden cursor-pointer group"
            >
              <div className="h-48 sm:h-56 md:h-64 bg-gradient-to-br from-purple-200 to-pink-200 relative overflow-hidden">
                <motion.div
                  className="absolute inset-0 bg-black opacity-0 group-hover:opacity-20 transition-opacity"
                />
                <div className="absolute inset-0 flex items-center justify-center text-white text-6xl font-bold">
                  {item}
                </div>
              </div>
              <div className="p-4 sm:p-6">
                <h3 className="text-lg sm:text-xl font-bold text-gray-800 mb-2">
                  Product {item}
                </h3>
                <p className="text-gray-600 text-sm sm:text-base">
                  Discover amazing fashion recommendations powered by AI
                </p>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="mt-4 w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white py-2 sm:py-3 rounded-lg font-medium text-sm sm:text-base hover:shadow-lg transition-shadow"
                >
                  View Details
                </motion.button>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.main>

      {/* Footer */}
      <motion.footer
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1 }}
        className="max-w-7xl mx-auto mt-12 text-center text-gray-600 text-sm sm:text-base"
      >
        <p>© 2024 AI Fashion Recommendations. All rights reserved.</p>
      </motion.footer>
    </motion.div>
  );
};

export default HomePage;
