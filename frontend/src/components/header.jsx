import { motion, AnimatePresence } from "framer-motion";
import { UserButton } from "@clerk/clerk-react";
import { Menu, X, Sparkles, Filter, ChevronDown } from "lucide-react";
import { useState } from "react";

export default function Header({ 
  onMenuClick,
  filters,
  onFilterChange,
  selectedOccasion,
  onOccasionChange 
}) {
  const [showColorFilter, setShowColorFilter] = useState(false);
  const [showSleeveFilter, setShowSleeveFilter] = useState(false);
  const [showOccasionFilter, setShowOccasionFilter] = useState(false);
  const [showPriceFilter, setShowPriceFilter] = useState(false);

  const COLORS = ["Black", "White", "Red", "Blue", "Green", "Yellow", "Pink", "Purple"];
  const SLEEVES = ["Sleeveless", "Short", "3/4 Sleeves", "Full Sleeves"];
  const OCCASIONS = ["All", "Casual", "Office", "Wedding", "Party", "Sports"];
  const PRICES = ["All", "Under $50", "$50-$100", "$100-$200"];

  return (
    <header className="bg-white shadow-md border-b border-gray-100 z-20 sticky top-0">
      <div className="px-4 sm:px-6 py-4 flex items-center justify-between gap-4">
        {/* Left: Menu + Logo */}
        <div className="flex items-center gap-3 min-w-fit">
          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
            onClick={onMenuClick}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <Menu className="w-6 h-6 text-gray-700" />
          </motion.button>

          <div className="hidden sm:flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center shadow-md">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <h1 className="font-bold text-gray-900 text-base">Fashion AI</h1>
          </div>
        </div>

        {/* Center: Filters */}
        <div className="flex items-center gap-2 flex-wrap justify-center flex-1">
          {/* Color Filter */}
          <div className="relative group">
            <motion.button
              whileHover={{ scale: 1.05 }}
              onClick={() => setShowColorFilter(!showColorFilter)}
              className="flex items-center gap-2 px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-all text-sm font-medium text-gray-700"
            >
              <span>🎨 Color</span>
              <ChevronDown className={`w-4 h-4 transition-transform ${showColorFilter ? 'rotate-180' : ''}`} />
            </motion.button>

            <AnimatePresence>
              {showColorFilter && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="absolute top-full left-0 mt-2 bg-white border-2 border-gray-200 rounded-lg shadow-xl z-50 min-w-max"
                >
                  <div className="p-3 space-y-2 max-h-64 overflow-y-auto">
                    <button
                      onClick={() => {
                        onFilterChange("color", "");
                        setShowColorFilter(false);
                      }}
                      className="block w-full text-left px-3 py-2 hover:bg-gray-100 rounded text-sm font-medium text-gray-700"
                    >
                      All Colors
                    </button>
                    {COLORS.map((color) => (
                      <button
                        key={color}
                        onClick={() => {
                          onFilterChange("color", color);
                          setShowColorFilter(false);
                        }}
                        className={`block w-full text-left px-3 py-2 rounded text-sm font-medium transition-all ${
                          filters.color === color
                            ? "bg-purple-100 text-purple-700"
                            : "hover:bg-gray-100 text-gray-700"
                        }`}
                      >
                        {color}
                      </button>
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Sleeve Filter */}
          <div className="relative group">
            <motion.button
              whileHover={{ scale: 1.05 }}
              onClick={() => setShowSleeveFilter(!showSleeveFilter)}
              className="flex items-center gap-2 px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-all text-sm font-medium text-gray-700"
            >
              <span>👕 Sleeves</span>
              <ChevronDown className={`w-4 h-4 transition-transform ${showSleeveFilter ? 'rotate-180' : ''}`} />
            </motion.button>

            <AnimatePresence>
              {showSleeveFilter && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="absolute top-full left-0 mt-2 bg-white border-2 border-gray-200 rounded-lg shadow-xl z-50 min-w-max"
                >
                  <div className="p-3 space-y-2">
                    <button
                      onClick={() => {
                        onFilterChange("sleeve", "");
                        setShowSleeveFilter(false);
                      }}
                      className="block w-full text-left px-3 py-2 hover:bg-gray-100 rounded text-sm font-medium text-gray-700"
                    >
                      All Sleeves
                    </button>
                    {SLEEVES.map((sleeve) => (
                      <button
                        key={sleeve}
                        onClick={() => {
                          onFilterChange("sleeve", sleeve);
                          setShowSleeveFilter(false);
                        }}
                        className={`block w-full text-left px-3 py-2 rounded text-sm font-medium transition-all ${
                          filters.sleeve === sleeve
                            ? "bg-pink-100 text-pink-700"
                            : "hover:bg-gray-100 text-gray-700"
                        }`}
                      >
                        {sleeve}
                      </button>
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Occasion Filter */}
          <div className="relative group">
            <motion.button
              whileHover={{ scale: 1.05 }}
              onClick={() => setShowOccasionFilter(!showOccasionFilter)}
              className="flex items-center gap-2 px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-all text-sm font-medium text-gray-700"
            >
              <span>📅 Occasion</span>
              <ChevronDown className={`w-4 h-4 transition-transform ${showOccasionFilter ? 'rotate-180' : ''}`} />
            </motion.button>

            <AnimatePresence>
              {showOccasionFilter && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="absolute top-full left-0 mt-2 bg-white border-2 border-gray-200 rounded-lg shadow-xl z-50 min-w-max"
                >
                  <div className="p-3 space-y-2">
                    {OCCASIONS.map((occasion) => (
                      <button
                        key={occasion}
                        onClick={() => {
                          onOccasionChange(occasion.toLowerCase());
                          setShowOccasionFilter(false);
                        }}
                        className={`block w-full text-left px-3 py-2 rounded text-sm font-medium transition-all ${
                          selectedOccasion === occasion.toLowerCase()
                            ? "bg-blue-100 text-blue-700"
                            : "hover:bg-gray-100 text-gray-700"
                        }`}
                      >
                        {occasion}
                      </button>
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Price Filter */}
          <div className="relative group">
            <motion.button
              whileHover={{ scale: 1.05 }}
              onClick={() => setShowPriceFilter(!showPriceFilter)}
              className="flex items-center gap-2 px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-all text-sm font-medium text-gray-700"
            >
              <span>💰 Price</span>
              <ChevronDown className={`w-4 h-4 transition-transform ${showPriceFilter ? 'rotate-180' : ''}`} />
            </motion.button>

            <AnimatePresence>
              {showPriceFilter && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="absolute top-full left-0 mt-2 bg-white border-2 border-gray-200 rounded-lg shadow-xl z-50 min-w-max"
                >
                  <div className="p-3 space-y-2">
                    <button
                      onClick={() => {
                        onFilterChange("price", "");
                        setShowPriceFilter(false);
                      }}
                      className="block w-full text-left px-3 py-2 hover:bg-gray-100 rounded text-sm font-medium text-gray-700"
                    >
                      All Prices
                    </button>
                    {PRICES.slice(1).map((price) => (
                      <button
                        key={price}
                        onClick={() => {
                          onFilterChange("price", price);
                          setShowPriceFilter(false);
                        }}
                        className={`block w-full text-left px-3 py-2 rounded text-sm font-medium transition-all ${
                          filters.price === price
                            ? "bg-green-100 text-green-700"
                            : "hover:bg-gray-100 text-gray-700"
                        }`}
                      >
                        {price}
                      </button>
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>

        {/* Right: User Button */}
        <div className="flex items-center gap-2 min-w-fit">
          <UserButton 
            appearance={{
              elements: {
                avatarBox: "w-9 h-9 sm:w-10 sm:h-10"
              }
            }}
          />
        </div>
      </div>
    </header>
  );
}