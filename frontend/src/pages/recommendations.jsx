import { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import axios from "axios";
import { motion, AnimatePresence } from "framer-motion";
import { Loader, Heart, ShoppingBag, ArrowLeft, ChevronDown } from "lucide-react";

export default function RecommendationsPage() {
  const location = useLocation();
  const navigate = useNavigate();

  const [selectedImageId, setSelectedImageId] = useState(null);
  const [selectedDetails, setSelectedDetails] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [filteredRecommendations, setFilteredRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [wishlist, setWishlist] = useState([]);
  
  const [openDropdown, setOpenDropdown] = useState(null);
  
  const [filters, setFilters] = useState({
    color: "All Colors",
    sleeve: "All Sleeves",
    occasion: "All Occasions",
    category: "All Categories",
  });

  const colorOptions = ["All Colors", "red", "blue", "black", "white", "green", "yellow", "pink", "brown", "grey", "multi"];
  const sleeveOptions = ["All Sleeves", "long", "short", "sleeveless", "unknown"];
  const occasionOptions = ["All Occasions", "casual", "party", "formal", "sports", "beach"];
  const categoryOptions = ["All Categories", "dress", "hat", "longsleeve", "outwear", "pants", "shirt", "shoes", "shorts", "skirt", "t-shirt"];

  // Get data from navigation state
  useEffect(() => {
    if (location.state) {
      setSelectedImageId(location.state.selectedImageId);
      setSelectedDetails(location.state.selectedDetails);
    }
  }, [location.state]);

  // Generate recommendations
  useEffect(() => {
    if (!selectedImageId || !selectedDetails) return;

    setLoading(true);
    setError(null);

    const generateRecommendations = async () => {
      try {
        const response = await axios.post(
          "http://127.0.0.1:8000/recommend/generate",
          {
            image_id: selectedImageId,
            top_k: 20,
            body_type: selectedDetails.body_type,
            skin_tone: selectedDetails.skin_tone,
          }
        );

        if (response.data.success) {
          console.log("✅ Recommendations received:", response.data.recommendations.length);
          console.log("Sample outfit:", response.data.recommendations[0]);
          setRecommendations(response.data.recommendations);
          setFilteredRecommendations(response.data.recommendations);
        } else {
          setError(response.data.error || "Failed to generate");
        }
      } catch (err) {
        console.error("❌ Error:", err);
        setError("Error generating recommendations");
      } finally {
        setLoading(false);
      }
    };

    generateRecommendations();
  }, [selectedImageId, selectedDetails]);

  // Apply filters ONLY when filters change
  useEffect(() => {
    console.log("\n🔄 FILTERING TRIGGERED");
    console.log("Current filters:", filters);
    console.log("Total recommendations:", recommendations.length);

    let filtered = recommendations;

    // COLOR FILTER
    if (filters.color !== "All Colors") {
      const targetColor = filters.color.toLowerCase();
      filtered = filtered.filter((item) => {
        const itemColor = (item.color || "").toLowerCase();
        const match = itemColor.includes(targetColor);
        return match;
      });
      console.log(`After color filter (${filters.color}):`, filtered.length);
    }

    // SLEEVE FILTER
    if (filters.sleeve !== "All Sleeves") {
      const targetSleeve = filters.sleeve.toLowerCase();
      filtered = filtered.filter((item) => {
        const itemSleeve = (item.sleeves || "").toLowerCase();
        const match = itemSleeve.includes(targetSleeve);
        return match;
      });
      console.log(`After sleeve filter (${filters.sleeve}):`, filtered.length);
    }

    // OCCASION FILTER
    if (filters.occasion !== "All Occasions") {
      const targetOccasion = filters.occasion.toLowerCase();
      filtered = filtered.filter((item) => {
        const itemOccasion = (item.occasion || "").toLowerCase();
        const match = itemOccasion.includes(targetOccasion);
        return match;
      });
      console.log(`After occasion filter (${filters.occasion}):`, filtered.length);
    }

    // CATEGORY FILTER
    if (filters.category !== "All Categories") {
      const targetCategory = filters.category.toLowerCase();
      filtered = filtered.filter((item) => {
        const itemCategory = (item.category || "").toLowerCase();
        const match = itemCategory === targetCategory;
        return match;
      });
      console.log(`After category filter (${filters.category}):`, filtered.length);
    }

    console.log("Final result:", filtered.length, "\n");
    setFilteredRecommendations(filtered);
  }, [filters, recommendations]);

  const handleFilterChange = (filterType, value) => {
    console.log(`Changing ${filterType} from ${filters[filterType]} to ${value}`);
    setFilters({
      ...filters,
      [filterType]: value,
    });
    setOpenDropdown(null);
  };

  const handleAddToWishlist = (outfit) => {
    const isInWishlist = wishlist.find((item) => item.rank === outfit.rank);
    if (isInWishlist) {
      setWishlist(wishlist.filter((item) => item.rank !== outfit.rank));
    } else {
      setWishlist([...wishlist, outfit]);
    }
  };

  if (!selectedImageId || !selectedDetails) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 flex items-center justify-center p-6">
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-center">
          <ShoppingBag className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <p className="text-2xl font-bold text-gray-900 mb-2">No Image Selected</p>
          <button
            onClick={() => navigate("/home")}
            className="px-6 py-3 bg-gradient-to-r from-pink-500 to-rose-500 text-white font-semibold rounded-lg hover:shadow-lg transition-all flex items-center gap-2 mx-auto"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Upload
          </button>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 relative overflow-hidden">
      <div className="absolute top-0 right-0 w-72 sm:w-96 h-72 sm:h-96 bg-pink-200 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse"></div>
      <div className="absolute bottom-0 left-0 w-72 sm:w-96 h-72 sm:h-96 bg-purple-200 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse" style={{ animationDelay: "700ms" }}></div>

      <div className="relative z-10 min-h-screen flex flex-col px-4 sm:px-6 py-8 sm:py-12">
        <div className="max-w-7xl mx-auto w-full">
          {/* Header */}
          <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
            <div className="flex items-center gap-4 mb-6">
              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => navigate("/home")}
                className="p-2 hover:bg-white rounded-lg transition-colors shadow-md"
              >
                <ArrowLeft className="w-6 h-6 text-gray-700" />
              </motion.button>
              <h1 className="text-4xl sm:text-5xl font-bold text-gray-900">👗 Clothes for {selectedDetails.body_type}</h1>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
              <motion.div whileHover={{ y: -5 }} className="bg-white rounded-2xl shadow-lg p-6 border-l-4 border-purple-500">
                <p className="text-sm text-gray-600 font-semibold uppercase">Body Type</p>
                <p className="text-3xl font-bold text-purple-600 mt-2">{selectedDetails.body_type}</p>
              </motion.div>

              <motion.div whileHover={{ y: -5 }} className="bg-white rounded-2xl shadow-lg p-6 border-l-4 border-pink-500">
                <p className="text-sm text-gray-600 font-semibold uppercase">Skin Tone</p>
                <p className="text-3xl font-bold text-pink-600 mt-2">{selectedDetails.skin_tone}</p>
              </motion.div>

              <motion.div whileHover={{ y: -5 }} className="bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl shadow-lg p-6 text-white">
                <p className="text-sm text-white/80 font-semibold uppercase">Total Matches</p>
                <p className="text-3xl font-bold mt-2">{filteredRecommendations.length}</p>
              </motion.div>
            </div>

            {/* Filters - ALL 4 FILTERS */}
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="bg-white rounded-2xl shadow-lg p-6 mb-8 relative">
              <h3 className="text-xl font-bold text-gray-900 mb-4">🎨 Refine Your Search</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                
                {/* Color Dropdown */}
                <div className="relative">
                  <button
                    onClick={() => setOpenDropdown(openDropdown === "color" ? null : "color")}
                    className="w-full flex items-center justify-between px-4 py-3 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors text-gray-900 font-semibold"
                  >
                    <span>💎 {filters.color}</span>
                    <ChevronDown className={`w-5 h-5 transition-transform ${openDropdown === "color" ? "rotate-180" : ""}`} />
                  </button>
                  {openDropdown === "color" && (
                    <motion.div
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="absolute top-full left-0 right-0 mt-2 bg-white border-2 border-gray-200 rounded-lg shadow-xl z-50"
                    >
                      {colorOptions.map((option) => (
                        <button
                          key={option}
                          onClick={() => handleFilterChange("color", option)}
                          className={`w-full text-left px-4 py-3 hover:bg-purple-100 transition-colors ${filters.color === option ? "bg-purple-200 font-bold" : ""}`}
                        >
                          {option}
                        </button>
                      ))}
                    </motion.div>
                  )}
                </div>

                {/* Sleeve Dropdown */}
                <div className="relative">
                  <button
                    onClick={() => setOpenDropdown(openDropdown === "sleeve" ? null : "sleeve")}
                    className="w-full flex items-center justify-between px-4 py-3 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors text-gray-900 font-semibold"
                  >
                    <span>👕 {filters.sleeve}</span>
                    <ChevronDown className={`w-5 h-5 transition-transform ${openDropdown === "sleeve" ? "rotate-180" : ""}`} />
                  </button>
                  {openDropdown === "sleeve" && (
                    <motion.div
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="absolute top-full left-0 right-0 mt-2 bg-white border-2 border-gray-200 rounded-lg shadow-xl z-50"
                    >
                      {sleeveOptions.map((option) => (
                        <button
                          key={option}
                          onClick={() => handleFilterChange("sleeve", option)}
                          className={`w-full text-left px-4 py-3 hover:bg-green-100 transition-colors ${filters.sleeve === option ? "bg-green-200 font-bold" : ""}`}
                        >
                          {option}
                        </button>
                      ))}
                    </motion.div>
                  )}
                </div>

                {/* Occasion Dropdown */}
                <div className="relative">
                  <button
                    onClick={() => setOpenDropdown(openDropdown === "occasion" ? null : "occasion")}
                    className="w-full flex items-center justify-between px-4 py-3 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors text-gray-900 font-semibold"
                  >
                    <span>🎉 {filters.occasion}</span>
                    <ChevronDown className={`w-5 h-5 transition-transform ${openDropdown === "occasion" ? "rotate-180" : ""}`} />
                  </button>
                  {openDropdown === "occasion" && (
                    <motion.div
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="absolute top-full left-0 right-0 mt-2 bg-white border-2 border-gray-200 rounded-lg shadow-xl z-50"
                    >
                      {occasionOptions.map((option) => (
                        <button
                          key={option}
                          onClick={() => handleFilterChange("occasion", option)}
                          className={`w-full text-left px-4 py-3 hover:bg-blue-100 transition-colors ${filters.occasion === option ? "bg-blue-200 font-bold" : ""}`}
                        >
                          {option}
                        </button>
                      ))}
                    </motion.div>
                  )}
                </div>

                {/* Category Dropdown */}
                <div className="relative">
                  <button
                    onClick={() => setOpenDropdown(openDropdown === "category" ? null : "category")}
                    className="w-full flex items-center justify-between px-4 py-3 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors text-gray-900 font-semibold"
                  >
                    <span>👗 {filters.category}</span>
                    <ChevronDown className={`w-5 h-5 transition-transform ${openDropdown === "category" ? "rotate-180" : ""}`} />
                  </button>
                  {openDropdown === "category" && (
                    <motion.div
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="absolute top-full left-0 right-0 mt-2 bg-white border-2 border-gray-200 rounded-lg shadow-xl z-50 max-h-64 overflow-y-auto"
                    >
                      {categoryOptions.map((option) => (
                        <button
                          key={option}
                          onClick={() => handleFilterChange("category", option)}
                          className={`w-full text-left px-4 py-3 hover:bg-yellow-100 transition-colors ${filters.category === option ? "bg-yellow-200 font-bold" : ""}`}
                        >
                          {option}
                        </button>
                      ))}
                    </motion.div>
                  )}
                </div>
              </div>
            </motion.div>
          </motion.div>

          {/* Loading */}
          {loading && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex items-center justify-center py-20">
              <Loader className="w-12 h-12 text-purple-600 animate-spin mr-4" />
              <p className="text-xl font-semibold text-gray-900">Finding perfect clothes...</p>
            </motion.div>
          )}

          {/* Error */}
          {error && !loading && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="bg-red-100 border border-red-400 text-red-700 px-6 py-4 rounded-xl mb-8">
              ⚠️ {error}
            </motion.div>
          )}

          {/* Recommendations Grid */}
          {!loading && !error && filteredRecommendations.length > 0 && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 pb-12">
              {filteredRecommendations.map((outfit, index) => {
                const isInWishlist = wishlist.find((item) => item.rank === outfit.rank);
                return (
                  <motion.div
                    key={outfit.rank}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                    whileHover={{ y: -15 }}
                    className="group bg-white rounded-2xl overflow-hidden shadow-lg hover:shadow-2xl transition-all"
                  >
                    <div className="relative h-56 bg-gradient-to-br from-purple-200 via-pink-200 to-blue-200 flex items-center justify-center group-hover:scale-105 transition-transform">
                      {outfit.image ? (
                        <img src={`data:image/jpeg;base64,${outfit.image}`} alt={outfit.outfit_name} className="w-full h-full object-cover" />
                      ) : (
                        <div className="text-7xl">👗</div>
                      )}
                      <div className="absolute top-3 right-3 bg-white rounded-full w-12 h-12 flex items-center justify-center font-bold text-purple-600 shadow-lg">
                        #{outfit.rank}
                      </div>
                      <div className="absolute top-3 left-3 bg-gradient-to-r from-green-400 to-emerald-500 text-white px-3 py-1.5 rounded-full font-bold text-sm">
                        {outfit.similarity_percentage}
                      </div>
                      <motion.button
                        whileHover={{ scale: 1.15 }}
                        whileTap={{ scale: 0.9 }}
                        onClick={() => handleAddToWishlist(outfit)}
                        className={`absolute bottom-3 right-3 rounded-full p-3 ${isInWishlist ? "bg-red-500 text-white" : "bg-white text-red-500"}`}
                      >
                        <Heart className={`w-5 h-5 ${isInWishlist ? "fill-current" : ""}`} />
                      </motion.button>
                    </div>
                    <div className="p-5">
                      <h3 className="font-bold text-gray-900 text-lg mb-3 truncate">{outfit.outfit_name}</h3>
                      <div className="mb-4">
                        <div className="flex justify-between mb-2">
                          <p className="text-xs font-semibold text-gray-600">Perfect Match</p>
                          <p className="text-sm font-bold text-emerald-600">{(outfit.similarity_score * 100).toFixed(0)}%</p>
                        </div>
                        <div className="w-full h-2.5 bg-gray-200 rounded-full">
                          <motion.div initial={{ width: 0 }} animate={{ width: `${outfit.similarity_score * 100}%` }} transition={{ duration: 1 }} className="h-full bg-gradient-to-r from-green-400 to-emerald-600" />
                        </div>
                      </div>
                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => handleAddToWishlist(outfit)}
                        className={`w-full py-2.5 rounded-lg font-semibold text-sm transition-all flex items-center justify-center gap-2 ${
                          isInWishlist ? "bg-red-100 text-red-600" : "bg-gray-100 text-gray-700"
                        }`}
                      >
                        <Heart className={`w-4 h-4 ${isInWishlist ? "fill-current" : ""}`} />
                        {isInWishlist ? "Saved" : "Save"}
                      </motion.button>
                    </div>
                  </motion.div>
                );
              })}
            </motion.div>
          )}

          {/* Empty */}
          {!loading && !error && filteredRecommendations.length === 0 && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-center py-20">
              <ShoppingBag className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-2xl font-bold text-gray-900">No Matches Found</p>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}