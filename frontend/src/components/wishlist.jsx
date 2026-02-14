import { useState, useEffect } from "react";
import axios from "axios";
import { motion } from "framer-motion";
import { Trash2, Heart, ShoppingBag, ArrowLeft } from "lucide-react";
import { useNavigate } from "react-router-dom";

export default function WishlistPage() {
  const navigate = useNavigate();
  const [wishlistItems, setWishlistItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterOccasion, setFilterOccasion] = useState("");

  const OCCASIONS = ["All", "Casual", "Office", "Wedding", "Party", "Sports", "Formal"];

  // Fetch wishlist from backend
  useEffect(() => {
    fetchWishlist();
  }, []);

  const fetchWishlist = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(
        "http://127.0.0.1:8000/wishlist/get",
        {
          params: {
            user_id: "default_user",
          },
        }
      );

      if (response.data.success) {
        setWishlistItems(response.data.items || []);
      } else {
        setError(response.data.error || "Failed to fetch wishlist");
      }
    } catch (err) {
      console.error("Error fetching wishlist:", err);
      setError("Error loading wishlist. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  // Remove from wishlist
  const handleRemoveFromWishlist = async (outfitName) => {
    try {
      await axios.post("http://127.0.0.1:8000/wishlist/remove", {
        user_id: "default_user",
        outfit_name: outfitName,
      });

      setWishlistItems(
        wishlistItems.filter((item) => item.outfit_name !== outfitName)
      );
    } catch (error) {
      console.error("Error removing from wishlist:", error);
      alert("Failed to remove from wishlist");
    }
  };

  // Clear entire wishlist
  const handleClearWishlist = async () => {
    if (!window.confirm("Are you sure you want to clear your entire wishlist?")) {
      return;
    }

    try {
      await axios.post("http://127.0.0.1:8000/wishlist/clear", {
        user_id: "default_user",
      });

      setWishlistItems([]);
    } catch (error) {
      console.error("Error clearing wishlist:", error);
      alert("Failed to clear wishlist");
    }
  };

  // Filter wishlist by occasion
  const filteredItems =
    filterOccasion === "All" || filterOccasion === ""
      ? wishlistItems
      : wishlistItems.filter((item) =>
          item.outfit_name.toLowerCase().includes(filterOccasion.toLowerCase())
        );

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 via-pink-50 to-rose-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8 flex items-center justify-between"
        >
          <div className="flex items-center gap-4">
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => navigate("/recommendations")}
              className="p-2 hover:bg-white rounded-lg transition-colors shadow-md"
            >
              <ArrowLeft className="w-6 h-6 text-gray-700" />
            </motion.button>
            <div>
              <h1 className="text-5xl font-bold text-gray-900">
                ❤️ My Wishlist
              </h1>
              <p className="text-gray-600 mt-2">
                {wishlistItems.length} items saved
              </p>
            </div>
          </div>

          {wishlistItems.length > 0 && (
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleClearWishlist}
              className="px-6 py-3 bg-red-500 hover:bg-red-600 text-white font-semibold rounded-lg transition-all shadow-lg"
            >
              Clear Wishlist
            </motion.button>
          )}
        </motion.div>

        {/* Loading */}
        {loading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-20"
          >
            <div className="inline-block">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                className="w-12 h-12 border-4 border-pink-300 border-t-pink-600 rounded-full"
              />
            </div>
            <p className="mt-4 text-xl font-semibold text-gray-900">
              Loading your wishlist...
            </p>
          </motion.div>
        )}

        {/* Error */}
        {error && !loading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="bg-red-100 border border-red-400 text-red-700 px-6 py-4 rounded-xl mb-6"
          >
            <p className="font-bold">⚠️ {error}</p>
          </motion.div>
        )}

        {/* Empty State */}
        {!loading && !error && wishlistItems.length === 0 && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-center py-20 bg-white rounded-2xl shadow-lg"
          >
            <Heart className="w-20 h-20 text-gray-300 mx-auto mb-4" />
            <p className="text-2xl font-bold text-gray-900 mb-2">
              Your wishlist is empty
            </p>
            <p className="text-gray-600 mb-6">
              Click the heart icon on clothes to save them here
            </p>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => navigate("/recommendations")}
              className="px-6 py-3 bg-gradient-to-r from-pink-500 to-rose-500 text-white font-semibold rounded-lg hover:shadow-lg transition-all"
            >
              Back to Recommendations →
            </motion.button>
          </motion.div>
        )}

        {/* Filter Section */}
        {!loading && !error && wishlistItems.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 20 }}
            transition={{ delay: 0.2 }}
            className="bg-white rounded-2xl shadow-lg p-6 mb-8"
          >
            <h2 className="text-lg font-bold text-gray-900 mb-4">
              🎯 Filter by Occasion
            </h2>
            <div className="flex flex-wrap gap-3">
              {OCCASIONS.map((occasion) => (
                <motion.button
                  key={occasion}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setFilterOccasion(occasion === "All" ? "" : occasion)}
                  className={`px-4 py-2 rounded-lg font-semibold transition-all ${
                    (occasion === "All" && filterOccasion === "") ||
                    filterOccasion === occasion
                      ? "bg-gradient-to-r from-pink-500 to-rose-500 text-white shadow-lg"
                      : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                  }`}
                >
                  {occasion}
                </motion.button>
              ))}
            </div>
          </motion.div>
        )}

        {/* Wishlist Grid */}
        {!loading && !error && filteredItems.length > 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
          >
            {filteredItems.map((item, index) => (
              <motion.div
                key={item.outfit_name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                whileHover={{ y: -10 }}
                className="group bg-white rounded-2xl overflow-hidden shadow-lg hover:shadow-2xl transition-all"
              >
                {/* Image */}
                <div className="relative h-56 bg-gradient-to-br from-pink-200 via-rose-200 to-red-200 overflow-hidden flex items-center justify-center">
                  <div className="text-6xl group-hover:scale-110 transition-transform">
                    👗
                  </div>

                  {/* Heart Badge */}
                  <div className="absolute top-3 right-3 bg-white rounded-full w-10 h-10 flex items-center justify-center shadow-lg">
                    <Heart className="w-6 h-6 text-red-500 fill-red-500" />
                  </div>

                  {/* Match Badge */}
                  {item.similarity_score && (
                    <div className="absolute top-3 left-3 bg-gradient-to-r from-green-400 to-emerald-500 text-white px-3 py-1 rounded-full font-bold text-sm shadow-lg">
                      {Math.round(item.similarity_score * 100)}%
                    </div>
                  )}
                </div>

                {/* Content */}
                <div className="p-5">
                  <h3 className="font-bold text-gray-900 text-lg mb-3 truncate">
                    {item.outfit_name}
                  </h3>

                  {/* Match Score */}
                  {item.similarity_score && (
                    <div className="mb-4">
                      <p className="text-xs text-gray-600 font-semibold mb-2">
                        Match Score
                      </p>
                      <div className="w-full h-2.5 bg-gray-200 rounded-full overflow-hidden">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${item.similarity_score * 100}%` }}
                          transition={{ duration: 1, ease: "easeOut" }}
                          className="h-full bg-gradient-to-r from-pink-500 to-rose-500"
                        />
                      </div>
                      <p className="text-xs text-gray-600 mt-2">
                        {Math.round(item.similarity_score * 100)}% match
                      </p>
                    </div>
                  )}

                  {/* Date Added */}
                  {item.saved_date && (
                    <p className="text-xs text-gray-500 mb-3">
                      📅 Added {new Date(item.saved_date).toLocaleDateString()}
                    </p>
                  )}

                  {/* Remove Button */}
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => handleRemoveFromWishlist(item.outfit_name)}
                    className="w-full py-2.5 bg-red-100 hover:bg-red-200 text-red-600 font-semibold rounded-lg transition-all flex items-center justify-center gap-2"
                  >
                    <Trash2 className="w-4 h-4" />
                    Remove
                  </motion.button>
                </div>
              </motion.div>
            ))}
          </motion.div>
        )}

        {/* No Filtered Results */}
        {!loading && !error && wishlistItems.length > 0 && filteredItems.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-20 bg-white rounded-2xl shadow-lg"
          >
            <ShoppingBag className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-2xl font-bold text-gray-900 mb-2">
              No items match "{filterOccasion}" occasion
            </p>
            <p className="text-gray-600 mb-6">
              Try selecting a different occasion filter
            </p>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setFilterOccasion("")}
              className="px-6 py-3 bg-gradient-to-r from-pink-500 to-rose-500 text-white font-semibold rounded-lg hover:shadow-lg transition-all"
            >
              Clear Filter
            </motion.button>
          </motion.div>
        )}

        {/* Stats Section */}
        {!loading && !error && wishlistItems.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="mt-12 grid grid-cols-1 sm:grid-cols-3 gap-6"
          >
            {/* Total Items */}
            <motion.div
              whileHover={{ y: -5 }}
              className="bg-gradient-to-br from-pink-100 to-rose-100 rounded-2xl p-6 border-l-4 border-pink-500 shadow-lg"
            >
              <p className="text-sm text-gray-600 font-semibold">TOTAL ITEMS</p>
              <p className="text-4xl font-bold text-pink-600 mt-2">
                {wishlistItems.length}
              </p>
              <p className="text-xs text-gray-600 mt-2">clothes saved</p>
            </motion.div>

            {/* Average Match */}
            <motion.div
              whileHover={{ y: -5 }}
              className="bg-gradient-to-br from-purple-100 to-pink-100 rounded-2xl p-6 border-l-4 border-purple-500 shadow-lg"
            >
              <p className="text-sm text-gray-600 font-semibold">AVG MATCH</p>
              <p className="text-4xl font-bold text-purple-600 mt-2">
                {wishlistItems.length > 0
                  ? Math.round(
                      (wishlistItems.reduce((sum, item) => sum + (item.similarity_score || 0), 0) /
                        wishlistItems.length) *
                        100
                    )
                  : 0}
                %
              </p>
              <p className="text-xs text-gray-600 mt-2">perfect matches</p>
            </motion.div>

            {/* Continue Shopping */}
            <motion.button
              whileHover={{ y: -5, scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => navigate("/recommendations")}
              className="bg-gradient-to-br from-rose-500 to-pink-500 text-white rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all flex flex-col items-center justify-center"
            >
              <ShoppingBag className="w-8 h-8 mb-2" />
              <p className="text-sm font-semibold">Continue Shopping</p>
              <p className="text-xs text-white/80 mt-1">Find more clothes →</p>
            </motion.button>
          </motion.div>
        )}
      </div>
    </div>
  );
}