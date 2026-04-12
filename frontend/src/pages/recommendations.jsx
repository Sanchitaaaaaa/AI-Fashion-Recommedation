import { useState, useEffect, useCallback, useMemo } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import axios from "axios";
import { motion, AnimatePresence } from "framer-motion";
import { Loader, Heart, ShoppingBag, ArrowLeft, ChevronDown, X, AlertTriangle, CheckCircle } from "lucide-react";

// ── Filter options ────────────────────────────────────────────────────────────
const COLOR_OPTIONS    = ["All Colors", "red", "blue", "black", "white", "green", "yellow", "pink", "brown", "grey", "purple", "orange", "multi"];
const SLEEVE_OPTIONS   = ["All Sleeves", "long", "short", "sleeveless"];
const OCCASION_OPTIONS = ["All Occasions", "casual", "party", "formal"];
const CATEGORY_OPTIONS = ["All Categories", "dress", "pants", "shirt", "shorts", "skirt", "t-shirt"];

const INITIAL_FILTERS = {
  color:    "All Colors",
  sleeve:   "All Sleeves",
  occasion: "All Occasions",
  category: "All Categories",
};

const isDefault = (key, value) => value === INITIAL_FILTERS[key];

// ── Skin tone → suitable colors map ──────────────────────────────────────────
const SKIN_TONE_COLORS = {
  Fair:    ["blue", "pink", "purple", "red", "green", "black", "white", "grey"],
  Medium:  ["red", "blue", "green", "yellow", "brown", "white", "black", "orange"],
  Tan:     ["white", "yellow", "orange", "red", "green", "blue", "brown", "multi"],
  Deep:    ["white", "yellow", "red", "orange", "green", "blue", "multi", "pink"],
};

function isColorSuitable(color, skinTone) {
  if (!color || !skinTone) return true;
  const suitable = SKIN_TONE_COLORS[skinTone];
  if (!suitable) return true;
  return suitable.includes(color.toLowerCase().trim());
}

function applyFilters(items, filters) {
  return items.filter((item) => {
    if (!isDefault("color", filters.color)) {
      if ((item.color || "").toLowerCase().trim() !== filters.color.toLowerCase().trim()) return false;
    }
    if (!isDefault("sleeve", filters.sleeve)) {
      if ((item.sleeves || "").toLowerCase().trim() !== filters.sleeve.toLowerCase().trim()) return false;
    }
    if (!isDefault("occasion", filters.occasion)) {
      if ((item.occasion || "").toLowerCase().trim() !== filters.occasion.toLowerCase().trim()) return false;
    }
    if (!isDefault("category", filters.category)) {
      if ((item.category || "").toLowerCase().trim() !== filters.category.toLowerCase().trim()) return false;
    }
    return true;
  });
}

const COLOR_DOT_MAP = {
  red:    "bg-red-500",
  blue:   "bg-blue-500",
  black:  "bg-gray-900",
  white:  "bg-gray-100 border border-gray-300",
  green:  "bg-green-500",
  yellow: "bg-yellow-400",
  pink:   "bg-pink-400",
  brown:  "bg-amber-700",
  grey:   "bg-gray-400",
  purple: "bg-purple-500",
  orange: "bg-orange-500",
  multi:  "bg-gradient-to-r from-pink-400 via-yellow-400 to-blue-400",
};

// ── Lazy image ────────────────────────────────────────────────────────────────
function OutfitImage({ src, alt }) {
  const [loaded, setLoaded] = useState(false);
  const [error,  setError]  = useState(false);

  if (!src || error) {
    return (
      <div className="w-full h-full flex items-center justify-center text-5xl select-none bg-gradient-to-br from-purple-100 to-pink-100">
        👗
      </div>
    );
  }

  return (
    <>
      {!loaded && (
        <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-purple-50 to-pink-50">
          <Loader className="w-7 h-7 text-purple-300 animate-spin" />
        </div>
      )}
      <img
        src={src}
        alt={alt}
        loading="lazy"
        decoding="async"
        onLoad={() => setLoaded(true)}
        onError={() => setError(true)}
        className={`w-full h-full object-cover transition-opacity duration-300 ${loaded ? "opacity-100" : "opacity-0"}`}
      />
    </>
  );
}

// ── Dropdown ──────────────────────────────────────────────────────────────────
function FilterDropdown({ id, emoji, options, value, onChange, openDropdown, setOpenDropdown, skinTone }) {
  const isOpen   = openDropdown === id;
  const isActive = !isDefault(id === "sleeve" ? "sleeve" : id, value);
  const selectedColorUnsafe = id === "color" && !isDefault("color", value) && !isColorSuitable(value, skinTone);

  return (
    <div className="relative">
      <button
        onClick={(e) => { e.stopPropagation(); setOpenDropdown(isOpen ? null : id); }}
        className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl transition-all font-semibold text-sm border-2 ${
          selectedColorUnsafe
            ? "bg-red-50 border-red-300 text-red-700"
            : isActive
            ? "bg-purple-50 border-purple-400 text-purple-800"
            : "bg-gray-50 border-gray-200 text-gray-700 hover:bg-gray-100"
        }`}
      >
        <span className="flex items-center gap-2 truncate">
          <span>{emoji}</span>
          <span className="truncate">{value}</span>
          {selectedColorUnsafe && <AlertTriangle className="w-3.5 h-3.5 text-red-500 flex-shrink-0" />}
        </span>
        <ChevronDown className={`w-4 h-4 flex-shrink-0 transition-transform ${isOpen ? "rotate-180" : ""}`} />
      </button>

      {selectedColorUnsafe && (
        <p className="text-xs text-red-500 mt-1 px-1 font-medium">
          Not ideal for your {skinTone} skin tone
        </p>
      )}

      <AnimatePresence>
        {isOpen && (
          <motion.div
            key="dd"
            initial={{ opacity: 0, y: -6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={{ duration: 0.12 }}
            className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-xl shadow-2xl z-50 max-h-52 overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            {options.map((option) => {
              const dotClass   = id === "color" ? COLOR_DOT_MAP[option] : null;
              const isUnsafe   = id === "color" && option !== "All Colors" && !isColorSuitable(option, skinTone);
              const isSelected = value === option;

              return (
                <button
                  key={option}
                  onClick={() => { onChange(id, option); setOpenDropdown(null); }}
                  className={`w-full text-left px-3 py-2.5 text-sm flex items-center gap-2 transition-colors ${
                    isSelected
                      ? "bg-purple-100 font-bold text-purple-800"
                      : isUnsafe
                      ? "hover:bg-red-50 text-gray-700"
                      : "hover:bg-purple-50 text-gray-700"
                  }`}
                >
                  {dotClass && <span className={`w-3 h-3 rounded-full flex-shrink-0 ${dotClass}`} />}
                  <span className="capitalize flex-1">{option}</span>
                  {isUnsafe && (
                    <span className="text-xs text-red-400 font-medium flex items-center gap-0.5">
                      <AlertTriangle className="w-3 h-3" /> not ideal
                    </span>
                  )}
                </button>
              );
            })}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

// ── Main Page ─────────────────────────────────────────────────────────────────
export default function RecommendationsPage() {
  const location = useLocation();
  const navigate  = useNavigate();

  const [selectedImageId, setSelectedImageId] = useState(null);
  const [selectedDetails, setSelectedDetails] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [loading,         setLoading]         = useState(false);
  const [error,           setError]           = useState(null);
  // wishlist is now a Set of outfit_names that are saved in backend
  const [wishlist,        setWishlist]        = useState(new Set());
  const [wishlistLoading, setWishlistLoading] = useState(new Set()); // tracks which cards are mid-request
  const [toast,           setToast]           = useState(null); // { message, type: "success"|"error" }
  const [openDropdown,    setOpenDropdown]    = useState(null);
  const [filters,         setFilters]         = useState(INITIAL_FILTERS);

  // ── Load state from navigation ────────────────────────────────────────────
  useEffect(() => {
    if (location.state) {
      setSelectedImageId(location.state.selectedImageId);
      setSelectedDetails(location.state.selectedDetails);
    }
  }, [location.state]);

  // ── Fetch existing wishlist from backend on mount ─────────────────────────
  useEffect(() => {
    const fetchWishlist = async () => {
      try {
        const res = await axios.get("http://127.0.0.1:8000/wishlist/get", {
          params: { user_id: "default_user" },
        });
        if (res.data.success) {
          const names = new Set((res.data.items || []).map((i) => i.outfit_name));
          setWishlist(names);
        }
      } catch (err) {
        console.error("Could not fetch wishlist:", err);
      }
    };
    fetchWishlist();
  }, []);

  // ── Show toast helper ─────────────────────────────────────────────────────
  const showToast = useCallback((message, type = "success") => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 2500);
  }, []);

  // ── Fetch recommendations ─────────────────────────────────────────────────
  useEffect(() => {
    if (!selectedImageId || !selectedDetails) return;

    const fetchRecs = async () => {
      setLoading(true);
      setError(null);
      setFilters(INITIAL_FILTERS);
      try {
        const res = await axios.post("http://127.0.0.1:8000/recommend/generate", {
          image_id:  selectedImageId,
          top_k:     100,
          body_type: selectedDetails.body_type,
          skin_tone: selectedDetails.skin_tone,
        });

        if (res.data.success) {
          setRecommendations(res.data.recommendations || []);
        } else {
          setError(res.data.error || "Failed to generate recommendations");
        }
      } catch (err) {
        console.error("❌", err);
        setError("Cannot connect to backend. Is it running?");
      } finally {
        setLoading(false);
      }
    };

    fetchRecs();
  }, [selectedImageId, selectedDetails]);

  // ── Apply filters (memoized) ──────────────────────────────────────────────
  const filtered = useMemo(
    () => applyFilters(recommendations, filters),
    [filters, recommendations]
  );

  // ── Handlers ─────────────────────────────────────────────────────────────
  const handleFilterChange = useCallback((key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  }, []);

  const resetFilters = useCallback(() => {
    setFilters(INITIAL_FILTERS);
    setOpenDropdown(null);
  }, []);

  // ── Toggle wishlist: calls backend, updates local Set ────────────────────
  const toggleWishlist = useCallback(async (outfit) => {
    const name = outfit.outfit_name;

    // Prevent double-click while request is in flight
    if (wishlistLoading.has(name)) return;

    setWishlistLoading((prev) => new Set(prev).add(name));

    const alreadySaved = wishlist.has(name);

    // Optimistic UI update
    setWishlist((prev) => {
      const next = new Set(prev);
      alreadySaved ? next.delete(name) : next.add(name);
      return next;
    });

    try {
      if (alreadySaved) {
        // Remove from wishlist
        await axios.post("http://127.0.0.1:8000/wishlist/remove", {
          user_id:     "default_user",
          outfit_name: name,
        });
        showToast("Removed from wishlist", "error");
      } else {
        // Add to wishlist
        await axios.post("http://127.0.0.1:8000/wishlist/add", {
          user_id:          "default_user",
          outfit_name:      name,
          similarity_score: outfit.similarity_score || 0,
          image_id:         selectedImageId,
          occasion:         outfit.occasion || "",
        });
        showToast("Saved to wishlist ❤️", "success");
      }
    } catch (err) {
      console.error("Wishlist error:", err);
      // Revert optimistic update on failure
      setWishlist((prev) => {
        const next = new Set(prev);
        alreadySaved ? next.add(name) : next.delete(name);
        return next;
      });
      showToast("Something went wrong. Try again.", "error");
    } finally {
      setWishlistLoading((prev) => {
        const next = new Set(prev);
        next.delete(name);
        return next;
      });
    }
  }, [wishlist, wishlistLoading, selectedImageId, showToast]);

  // Close dropdowns on outside click
  useEffect(() => {
    const close = () => setOpenDropdown(null);
    document.addEventListener("click", close);
    return () => document.removeEventListener("click", close);
  }, []);

  const activeFilterCount = Object.entries(filters).filter(([k, v]) => !isDefault(k, v)).length;
  const skinTone = selectedDetails?.skin_tone || null;

  // ── Guard ─────────────────────────────────────────────────────────────────
  if (!selectedImageId || !selectedDetails) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 flex items-center justify-center p-6">
        <div className="text-center">
          <ShoppingBag className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <p className="text-2xl font-bold text-gray-900 mb-4">No Image Selected</p>
          <button
            onClick={() => navigate("/home")}
            className="px-6 py-3 bg-gradient-to-r from-pink-500 to-rose-500 text-white font-semibold rounded-xl hover:shadow-lg transition-all flex items-center gap-2 mx-auto"
          >
            <ArrowLeft className="w-4 h-4" /> Back to Upload
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">

      {/* ── Toast notification ────────────────────────────────────────────── */}
      <AnimatePresence>
        {toast && (
          <motion.div
            initial={{ opacity: 0, y: -40 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -40 }}
            className={`fixed top-5 left-1/2 -translate-x-1/2 z-50 flex items-center gap-2 px-5 py-3 rounded-full shadow-xl font-semibold text-sm ${
              toast.type === "success"
                ? "bg-white text-gray-800 border border-green-200"
                : "bg-white text-gray-800 border border-red-200"
            }`}
          >
            {toast.type === "success"
              ? <CheckCircle className="w-4 h-4 text-green-500" />
              : <Heart className="w-4 h-4 text-red-400" />
            }
            {toast.message}
          </motion.div>
        )}
      </AnimatePresence>

      <div className="relative z-10 px-4 sm:px-6 py-8 max-w-7xl mx-auto">

        {/* ── Header ───────────────────────────────────────────────────────── */}
        <div className="mb-6">
          <div className="flex items-center gap-4 mb-6">
            <motion.button
              whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.95 }}
              onClick={() => navigate("/home")}
              className="p-2 bg-white hover:bg-gray-50 rounded-xl shadow-md transition-colors"
            >
              <ArrowLeft className="w-5 h-5 text-gray-700" />
            </motion.button>
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">
                👗 Your Recommendations
              </h1>
              <p className="text-sm text-gray-500 mt-0.5">
                Based on your{" "}
                <span className="font-semibold text-purple-600">{selectedDetails.body_type}</span>{" "}
                body type &amp;{" "}
                <span className="font-semibold text-pink-600">{selectedDetails.skin_tone}</span>{" "}
                skin tone
              </p>
            </div>

            {/* Wishlist shortcut */}
            <motion.button
              whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
              onClick={() => navigate("/wishlist")}
              className="ml-auto flex items-center gap-2 px-4 py-2 bg-white rounded-xl shadow-md text-sm font-semibold text-red-500 hover:bg-red-50 transition-colors"
            >
              <Heart className="w-4 h-4 fill-red-500" />
              Wishlist
              {wishlist.size > 0 && (
                <span className="bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                  {wishlist.size}
                </span>
              )}
            </motion.button>
          </div>

          {/* Stats row */}
          <div className="grid grid-cols-3 gap-3 mb-6">
            <div className="bg-white rounded-2xl shadow-sm p-4 border-l-4 border-purple-400">
              <p className="text-xs text-gray-500 uppercase tracking-wide font-semibold">Body Type</p>
              <p className="text-lg font-bold text-purple-600 mt-0.5">{selectedDetails.body_type}</p>
            </div>
            <div className="bg-white rounded-2xl shadow-sm p-4 border-l-4 border-pink-400">
              <p className="text-xs text-gray-500 uppercase tracking-wide font-semibold">Skin Tone</p>
              <p className="text-lg font-bold text-pink-600 mt-0.5">{selectedDetails.skin_tone}</p>
            </div>
            <div className="bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl shadow-sm p-4 text-white">
              <p className="text-xs text-white/70 uppercase tracking-wide font-semibold">Showing</p>
              <p className="text-lg font-bold mt-0.5">
                {filtered.length}
                <span className="text-sm font-normal text-white/60"> / {recommendations.length}</span>
              </p>
            </div>
          </div>

          {/* ── Filter Panel ─────────────────────────────────────────────────── */}
          <div
            className="bg-white rounded-2xl shadow-sm p-4 mb-6 border border-gray-100"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-bold text-gray-900">🎨 Filter Results</h3>
              <div className="flex items-center gap-2">
                {activeFilterCount > 0 && (
                  <span className="text-xs bg-purple-100 text-purple-700 font-bold px-2 py-0.5 rounded-full">
                    {activeFilterCount} active
                  </span>
                )}
                {activeFilterCount > 0 && (
                  <button
                    onClick={resetFilters}
                    className="flex items-center gap-1 text-xs text-red-500 hover:text-red-700 font-semibold px-2.5 py-1 rounded-full border border-red-200 hover:bg-red-50 transition-colors"
                  >
                    <X className="w-3 h-3" /> Clear all
                  </button>
                )}
              </div>
            </div>

            <div className="grid grid-cols-2 lg:grid-cols-4 gap-2">
              <FilterDropdown
                id="color" emoji="🎨" label="Color"
                options={COLOR_OPTIONS} value={filters.color}
                onChange={handleFilterChange}
                openDropdown={openDropdown} setOpenDropdown={setOpenDropdown}
                skinTone={skinTone}
              />
              <FilterDropdown
                id="sleeve" emoji="👕" label="Sleeve"
                options={SLEEVE_OPTIONS} value={filters.sleeve}
                onChange={handleFilterChange}
                openDropdown={openDropdown} setOpenDropdown={setOpenDropdown}
                skinTone={skinTone}
              />
              <FilterDropdown
                id="occasion" emoji="🎉" label="Occasion"
                options={OCCASION_OPTIONS} value={filters.occasion}
                onChange={handleFilterChange}
                openDropdown={openDropdown} setOpenDropdown={setOpenDropdown}
                skinTone={skinTone}
              />
              <FilterDropdown
                id="category" emoji="👗" label="Category"
                options={CATEGORY_OPTIONS} value={filters.category}
                onChange={handleFilterChange}
                openDropdown={openDropdown} setOpenDropdown={setOpenDropdown}
                skinTone={skinTone}
              />
            </div>

            {activeFilterCount > 0 && (
              <div className="flex flex-wrap gap-1.5 mt-3 pt-3 border-t border-gray-100">
                {Object.entries(filters).map(([key, value]) =>
                  !isDefault(key, value) ? (
                    <span
                      key={key}
                      className="flex items-center gap-1 px-2.5 py-1 bg-purple-100 text-purple-700 rounded-full text-xs font-semibold"
                    >
                      <span className="capitalize">{value}</span>
                      <button onClick={() => handleFilterChange(key, INITIAL_FILTERS[key])}>
                        <X className="w-3 h-3 hover:text-purple-900" />
                      </button>
                    </span>
                  ) : null
                )}
              </div>
            )}
          </div>
        </div>

        {/* ── Loading ───────────────────────────────────────────────────────── */}
        {loading && (
          <div className="flex items-center justify-center py-20">
            <Loader className="w-10 h-10 text-purple-500 animate-spin mr-3" />
            <p className="text-lg font-semibold text-gray-600">Finding perfect outfits...</p>
          </div>
        )}

        {/* ── Error ─────────────────────────────────────────────────────────── */}
        {error && !loading && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-5 py-4 rounded-xl mb-6 text-sm">
            ⚠️ {error}
          </div>
        )}

        {/* ── Grid ──────────────────────────────────────────────────────────── */}
        {!loading && !error && filtered.length > 0 && (
          <motion.div
            layout
            className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4 pb-12"
          >
            <AnimatePresence mode="popLayout">
              {filtered.map((outfit, index) => {
                const inWishlist   = wishlist.has(outfit.outfit_name);
                const isProcessing = wishlistLoading.has(outfit.outfit_name);
                const dotClass     = COLOR_DOT_MAP[outfit.color] || "bg-gray-300";
                const colorUnsafe  = !isColorSuitable(outfit.color, skinTone);

                return (
                  <motion.div
                    key={`${outfit.rank}-${outfit.outfit_name}`}
                    layout
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.9 }}
                    transition={{ duration: 0.18, delay: Math.min(index * 0.025, 0.25) }}
                    whileHover={{ y: -6, transition: { duration: 0.2 } }}
                    className="bg-white rounded-2xl overflow-hidden shadow-md hover:shadow-xl transition-shadow"
                  >
                    {/* Image */}
                    <div className="relative h-48 overflow-hidden">
                      <OutfitImage src={outfit.image_url} alt={outfit.outfit_name} />

                      {/* Rank badge */}
                      <div className="absolute top-2 right-2 bg-white/90 backdrop-blur-sm rounded-full w-7 h-7 flex items-center justify-center font-bold text-purple-600 text-xs shadow">
                        #{outfit.rank}
                      </div>

                      {/* Match % */}
                      <div className="absolute top-2 left-2 bg-emerald-500 text-white px-2 py-0.5 rounded-full font-bold text-xs shadow">
                        {outfit.similarity_percentage}
                      </div>

                      {/* Skin tone warning banner */}
                      {colorUnsafe && (
                        <div className="absolute bottom-0 left-0 right-0 bg-red-500/90 text-white px-2 py-1 flex items-center gap-1">
                          <AlertTriangle className="w-3 h-3 flex-shrink-0" />
                          <span className="text-xs font-semibold truncate">
                            Not ideal for {skinTone} skin
                          </span>
                        </div>
                      )}

                      {/* ── Heart / Wishlist button ──────────────────────── */}
                      <button
                        onClick={() => toggleWishlist(outfit)}
                        disabled={isProcessing}
                        className={`absolute right-2 rounded-full p-2 shadow-md transition-all ${
                          colorUnsafe ? "bottom-8" : "bottom-2"
                        } ${
                          isProcessing
                            ? "bg-gray-100 text-gray-400 cursor-wait"
                            : inWishlist
                            ? "bg-red-500 text-white scale-110"
                            : "bg-white/90 text-red-400 hover:bg-red-50"
                        }`}
                      >
                        {isProcessing
                          ? <Loader className="w-4 h-4 animate-spin" />
                          : <Heart className={`w-4 h-4 ${inWishlist ? "fill-current" : ""}`} />
                        }
                      </button>
                    </div>

                    {/* Card body */}
                    <div className="p-3">
                      <h3 className="font-bold text-gray-900 text-xs mb-2 truncate">{outfit.outfit_name}</h3>

                      <div className="flex flex-wrap gap-1 mb-2">
                        {outfit.category && (
                          <span className="text-xs bg-purple-100 text-purple-700 px-1.5 py-0.5 rounded-full capitalize font-medium">
                            {outfit.category}
                          </span>
                        )}
                        {outfit.occasion && (
                          <span className="text-xs bg-green-100 text-green-700 px-1.5 py-0.5 rounded-full capitalize font-medium">
                            {outfit.occasion}
                          </span>
                        )}
                        {outfit.sleeves && outfit.sleeves !== "unknown" && (
                          <span className="text-xs bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded-full capitalize font-medium">
                            {outfit.sleeves}
                          </span>
                        )}
                        {outfit.color && (
                          <span className="flex items-center gap-1 text-xs bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded-full font-medium">
                            <span className={`w-2.5 h-2.5 rounded-full ${dotClass}`} />
                            {outfit.color}
                          </span>
                        )}
                      </div>

                      {colorUnsafe && (
                        <div className="flex items-center gap-1 mb-2 px-1.5 py-1 bg-red-50 border border-red-200 rounded-lg">
                          <AlertTriangle className="w-3 h-3 text-red-500 flex-shrink-0" />
                          <span className="text-xs text-red-600 font-medium">
                            Not ideal for your skin tone
                          </span>
                        </div>
                      )}

                      <div className="w-full h-1.5 bg-gray-100 rounded-full overflow-hidden">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${outfit.similarity_score * 100}%` }}
                          transition={{ duration: 0.7, delay: index * 0.025 }}
                          className="h-full bg-gradient-to-r from-purple-400 to-pink-500 rounded-full"
                        />
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </AnimatePresence>
          </motion.div>
        )}

        {/* ── No filter matches ─────────────────────────────────────────────── */}
        {!loading && !error && filtered.length === 0 && recommendations.length > 0 && (
          <div className="text-center py-20">
            <ShoppingBag className="w-14 h-14 text-gray-200 mx-auto mb-4" />
            <p className="text-xl font-bold text-gray-800 mb-2">No Matches Found</p>
            <p className="text-gray-400 text-sm mb-6 max-w-xs mx-auto">
              No outfits match your current filters. Try removing some filters.
            </p>
            <button
              onClick={resetFilters}
              className="px-6 py-2.5 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-semibold rounded-xl hover:shadow-lg transition-all"
            >
              Clear All Filters
            </button>
          </div>
        )}

        {/* ── No recommendations ────────────────────────────────────────────── */}
        {!loading && !error && recommendations.length === 0 && (
          <div className="text-center py-20">
            <ShoppingBag className="w-14 h-14 text-gray-200 mx-auto mb-4" />
            <p className="text-xl font-bold text-gray-800 mb-1">No Recommendations Found</p>
            <p className="text-gray-400 text-sm">Make sure your outfit database is populated.</p>
          </div>
        )}

      </div>
    </div>
  );
}