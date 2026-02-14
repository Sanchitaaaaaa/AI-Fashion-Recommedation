import { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import axios from "axios";
import { motion, AnimatePresence } from "framer-motion";
import { Loader, Heart, ShoppingBag, ArrowLeft } from "lucide-react";

const COLORS = [
  "Black",
  "White",
  "Red",
  "Blue",
  "Green",
  "Yellow",
  "Pink",
  "Purple",
  "Brown",
  "Gray",
  "Navy",
  "Cream",
];
const SLEEVES = [
  "Sleeveless",
  "Short Sleeves",
  "3/4 Sleeves",
  "Full Sleeves",
  "Off Shoulder",
];
const OCCASIONS = [
  "Casual",
  "Office",
  "Wedding",
  "Party",
  "Sports",
  "Formal",
  "Beach",
  "Dinner",
];
const PRICES = ["Under $50", "$50-$100", "$100-$200", "$200+"];

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
  const [filters, setFilters] = useState({
    color: "",
    sleeve: "",
    occasion: "",
    price: "",
  });

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
          }
        );

        if (response.data.success) {
          // Fetch outfit details with images from MongoDB
          const outfitsResponse = await axios.get(
            "http://127.0.0.1:8000/recommend/outfits"
          );

          if (outfitsResponse.data.outfits) {
            // Map recommendations with outfit images
            const recommendationsWithImages = response.data.recommendations.map(
              (rec, index) => {
                const outfit = outfitsResponse.data.outfits[index] || {};
                return {
                  ...rec,
                  outfit_name: outfit.name || rec.outfit_name,
                  image: outfit.image || null,
                  type: outfit.type || "dress",
                  color: outfit.color || "Multi",
                };
              }
            );

            setRecommendations(recommendationsWithImages);
            setFilteredRecommendations(recommendationsWithImages);
          } else {
            setRecommendations(response.data.recommendations);
            setFilteredRecommendations(response.data.recommendations);
          }
        } else {
          setError(response.data.error || "Failed to generate recommendations");
        }
      } catch (err) {
        console.error(err);
        setError("Error generating recommendations");
      } finally {
        setLoading(false);
      }
    };

    generateRecommendations();
  }, [selectedImageId, selectedDetails]);

  // Apply filters
  useEffect(() => {
    let filtered = recommendations;

    if (filters.color) {
      filtered = filtered.filter((item) =>
        item.outfit_name.toLowerCase().includes(filters.color.toLowerCase())
      );
    }

    if (filters.sleeve) {
      filtered = filtered.filter((item) =>
        item.outfit_name.toLowerCase().includes(filters.sleeve.toLowerCase())
      );
    }

    if (filters.occasion) {
      filtered = filtered.filter((item) =>
        item.outfit_name.toLowerCase().includes(filters.occasion.toLowerCase())
      );
    }

    setFilteredRecommendations(filtered);
  }, [filters, recommendations]);

  const handleFilterChange = (filterType, value) => {
    setFilters({
      ...filters,
      [filterType]: value,
    });
  };

  const handleAddToWishlist = async (outfit) => {
    const isInWishlist = wishlist.find((item) => item.rank === outfit.rank);

    if (isInWishlist) {
      setWishlist(wishlist.filter((item) => item.rank !== outfit.rank));
      try {
        await axios.post("http://127.0.0.1:8000/wishlist/remove", {
          user_id: "default_user",
          outfit_name: outfit.outfit_name,
        });
      } catch (error) {
        console.error("Error removing from wishlist:", error);
      }
    } else {
      setWishlist([...wishlist, outfit]);
      try {
        await axios.post("http://127.0.0.1:8000/wishlist/add", {
          user_id: "default_user",
          outfit_name: outfit.outfit_name,
          similarity_score: outfit.similarity_score,
          image_id: selectedImageId,
        });
      } catch (error) {
        console.error("Error saving to wishlist:", error);
      }
    }
  };

  if (!selectedImageId || !selectedDetails) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 flex items-center justify-center p-6">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center"
        >
          <ShoppingBag className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <p className="text-2xl font-bold text-gray-900 mb-2">
            No Image Selected
          </p>
          <p className="text-gray-600 mb-6">
            Upload a photo to see personalized recommendations
          </p>
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
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 relative overflow-hidden flex flex-col">
      {/* Background decorations */}
      <div className="absolute top-0 right-0 w-72 sm:w-96 h-72 sm:h-96 bg-pink-200 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse"></div>
      <div
        className="absolute bottom-0 left-0 w-72 sm:w-96 h-72 sm:h-96 bg-purple-200 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse"
        style={{ animationDelay: "700ms" }}
      ></div>

      {/* Main content */}
      <div className="relative z-10 flex-1 flex flex-col px-4 sm:px-6 py-8 sm:py-12 overflow-y-auto">
        <div className="max-w-7xl mx-auto w-full">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8"
          >
            <div className="flex items-center gap-4 mb-6">
              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => navigate("/home")}
                className="p-2 hover:bg-white rounded-lg transition-colors shadow-md"
              >
                <ArrowLeft className="w-6 h-6 text-gray-700" />
              </motion.button>
              <h1 className="text-5xl font-bold text-gray-900">
                👗 Clothes for {selectedDetails.body_type}
              </h1>
            </div>

            {/* Stats cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <motion.div
                whileHover={{ y: -5 }}
                className="bg-white rounded-2xl shadow-lg p-6 border-l-4 border-purple-500"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm text-gray-600 font-semibold uppercase">
                      Your Body Type
                    </p>
                    <p className="text-3xl font-bold text-purple-600 mt-2">
                      {selectedDetails.body_type}
                    </p>
                    <div className="mt-3 w-full bg-gray-200 rounded-full h-2">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{
                          width: `${
                            (selectedDetails.body_type_confidence || 0.85) * 100
                          }%`,
                        }}
                        transition={{ duration: 1 }}
                        className="h-full bg-gradient-to-r from-purple-400 to-purple-600 rounded-full"
                      />
                    </div>
                    <p className="text-xs text-gray-500 mt-2">
                      {(
                        (selectedDetails.body_type_confidence || 0.85) * 100
                      ).toFixed(0)}
                      % confidence
                    </p>
                  </div>
                  <div className="text-4xl">👗</div>
                </div>
              </motion.div>

              <motion.div
                whileHover={{ y: -5 }}
                className="bg-white rounded-2xl shadow-lg p-6 border-l-4 border-pink-500"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm text-gray-600 font-semibold uppercase">
                      Your Skin Tone
                    </p>
                    <p className="text-3xl font-bold text-pink-600 mt-2">
                      {selectedDetails.skin_tone}
                    </p>
                    <div className="mt-3 w-full bg-gray-200 rounded-full h-2">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{
                          width: `${
                            (selectedDetails.skin_tone_confidence || 0.85) * 100
                          }%`,
                        }}
                        transition={{ duration: 1 }}
                        className="h-full bg-gradient-to-r from-pink-400 to-pink-600 rounded-full"
                      />
                    </div>
                    <p className="text-xs text-gray-500 mt-2">
                      {(
                        (selectedDetails.skin_tone_confidence || 0.85) * 100
                      ).toFixed(0)}
                      % confidence
                    </p>
                  </div>
                  <div className="text-4xl">🎨</div>
                </div>
              </motion.div>

              <motion.div
                whileHover={{ y: -5 }}
                className="bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl shadow-lg p-6 text-white"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm text-white/80 font-semibold uppercase">
                      Total Matches
                    </p>
                    <p className="text-3xl font-bold mt-2">
                      {filteredRecommendations.length}
                    </p>
                    <p className="text-xs text-white/70 mt-2">
                      Personalized for your style
                    </p>
                  </div>
                  <div className="text-4xl">✨</div>
                </div>
              </motion.div>
            </div>
          </motion.div>

          {/* Filters */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white rounded-2xl shadow-lg p-6 mb-8"
          >
            <h2 className="text-xl font-bold text-gray-900 mb-6">
              🎯 Refine Your Search
            </h2>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-3">
                  🎨 Color
                </label>
                <select
                  value={filters.color}
                  onChange={(e) => handleFilterChange("color", e.target.value)}
                  className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-purple-500 focus:outline-none transition"
                >
                  <option value="">All Colors</option>
                  {COLORS.map((color) => (
                    <option key={color} value={color}>
                      {color}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-3">
                  👕 Sleeves
                </label>
                <select
                  value={filters.sleeve}
                  onChange={(e) =>
                    handleFilterChange("sleeve", e.target.value)
                  }
                  className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-pink-500 focus:outline-none transition"
                >
                  <option value="">All Sleeves</option>
                  {SLEEVES.map((sleeve) => (
                    <option key={sleeve} value={sleeve}>
                      {sleeve}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-3">
                  📅 Occasion
                </label>
                <select
                  value={filters.occasion}
                  onChange={(e) =>
                    handleFilterChange("occasion", e.target.value)
                  }
                  className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:outline-none transition"
                >
                  <option value="">All Occasions</option>
                  {OCCASIONS.map((occasion) => (
                    <option key={occasion} value={occasion}>
                      {occasion}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-3">
                  💰 Price Range
                </label>
                <select
                  value={filters.price}
                  onChange={(e) => handleFilterChange("price", e.target.value)}
                  className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-green-500 focus:outline-none transition"
                >
                  <option value="">All Prices</option>
                  {PRICES.map((price) => (
                    <option key={price} value={price}>
                      {price}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </motion.div>

          {/* Loading */}
          {loading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex items-center justify-center py-20"
            >
              <div className="text-center">
                <Loader className="w-12 h-12 text-purple-600 animate-spin mx-auto mb-4" />
                <p className="text-xl font-semibold text-gray-900">
                  Finding perfect clothes for you...
                </p>
              </div>
            </motion.div>
          )}

          {/* Error */}
          {error && !loading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="bg-red-100 border border-red-400 text-red-700 px-6 py-4 rounded-xl mb-8"
            >
              <p className="font-bold">⚠️ {error}</p>
            </motion.div>
          )}

          {/* Recommendations Grid */}
          {!loading && !error && filteredRecommendations.length > 0 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3 }}
              className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
            >
              <AnimatePresence mode="popLayout">
                {filteredRecommendations.map((outfit, index) => {
                  const isInWishlist = wishlist.find(
                    (item) => item.rank === outfit.rank
                  );

                  return (
                    <motion.div
                      key={outfit.rank}
                      layout
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ delay: index * 0.05 }}
                      whileHover={{ y: -15 }}
                      className="group bg-white rounded-2xl overflow-hidden shadow-lg hover:shadow-2xl transition-all"
                    >
                      {/* Image section - DISPLAY REAL IMAGES */}
                      <div className="relative h-56 bg-gradient-to-br from-purple-200 via-pink-200 to-blue-200 overflow-hidden flex items-center justify-center group-hover:scale-105 transition-transform duration-300">
                        {outfit.image ? (
                          <img
                            src={`http://127.0.0.1:8000/outfit_images/${outfit.image}`}

                            alt={outfit.outfit_name}
                            className="w-full h-full object-cover"
                            onError={(e) => {
                              e.target.style.display = "none";
                              e.target.nextSibling.style.display = "flex";
                            }}
                          />
                        ) : null}
                        <div
                          className="text-7xl flex items-center justify-center"
                          style={{
                            display: outfit.image ? "none" : "flex",
                          }}
                        >
                          👗
                        </div>

                        {/* Rank badge */}
                        <motion.div
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          className="absolute top-3 right-3 bg-white rounded-full w-12 h-12 flex items-center justify-center font-bold text-purple-600 shadow-lg text-lg"
                        >
                          #{outfit.rank}
                        </motion.div>

                        {/* Match percentage */}
                        <div className="absolute top-3 left-3 bg-gradient-to-r from-green-400 to-emerald-500 text-white px-3 py-1.5 rounded-full font-bold text-sm shadow-lg">
                          {outfit.similarity_percentage}
                        </div>

                        {/* Wishlist button */}
                        <motion.button
                          whileHover={{ scale: 1.15 }}
                          whileTap={{ scale: 0.9 }}
                          onClick={() => handleAddToWishlist(outfit)}
                          className={`absolute bottom-3 right-3 rounded-full p-3 shadow-lg transition-all ${
                            isInWishlist
                              ? "bg-red-500 text-white"
                              : "bg-white text-red-500 hover:bg-red-50"
                          }`}
                        >
                          <Heart
                            className={`w-5 h-5 ${
                              isInWishlist ? "fill-current" : ""
                            }`}
                          />
                        </motion.button>
                      </div>

                      {/* Content */}
                      <div className="p-5">
                        <h3 className="font-bold text-gray-900 text-lg mb-3 truncate">
                          {outfit.outfit_name}
                        </h3>

                        {/* Match score */}
                        <div className="mb-4">
                          <div className="flex items-center justify-between mb-2">
                            <p className="text-xs font-semibold text-gray-600">
                              Perfect Match
                            </p>
                            <p className="text-sm font-bold text-emerald-600">
                              {(outfit.similarity_score * 100).toFixed(0)}%
                            </p>
                          </div>
                          <div className="w-full h-2.5 bg-gray-200 rounded-full overflow-hidden">
                            <motion.div
                              initial={{ width: 0 }}
                              animate={{
                                width: `${outfit.similarity_score * 100}%`,
                              }}
                              transition={{ duration: 1 }}
                              className="h-full bg-gradient-to-r from-green-400 to-emerald-600"
                            />
                          </div>
                        </div>

                        {/* Save button */}
                        <motion.button
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                          onClick={() => handleAddToWishlist(outfit)}
                          className={`w-full py-2.5 rounded-lg font-semibold text-sm transition-all flex items-center justify-center gap-2 ${
                            isInWishlist
                              ? "bg-red-100 hover:bg-red-200 text-red-600"
                              : "bg-gray-100 text-gray-700 hover:bg-red-100 hover:text-red-600"
                          }`}
                        >
                          <Heart
                            className={`w-4 h-4 ${
                              isInWishlist ? "fill-current" : ""
                            }`}
                          />
                          {isInWishlist ? "Saved" : "Save"}
                        </motion.button>
                      </div>
                    </motion.div>
                  );
                })}
              </AnimatePresence>
            </motion.div>
          )}

          {/* Empty state */}
          {!loading && !error && filteredRecommendations.length === 0 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-center py-20"
            >
              <ShoppingBag className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-2xl font-bold text-gray-900 mb-2">
                No Matches Found
              </p>
              <p className="text-gray-600">
                Try adjusting your filters to see more recommendations
              </p>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}