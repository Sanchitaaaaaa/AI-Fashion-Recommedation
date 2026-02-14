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