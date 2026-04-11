import { useState, useEffect, useCallback, useMemo } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import axios from "axios";
import { motion, AnimatePresence } from "framer-motion";
import { Loader, Heart, ShoppingBag, ArrowLeft, ChevronDown, X } from "lucide-react";

// ── Filter options ────────────────────────────────────────────────────────────
const COLOR_OPTIONS    = ["All Colors",    "red", "blue", "black", "white", "green", "yellow", "pink", "brown", "grey", "purple", "orange", "multi"];
const SLEEVE_OPTIONS   = ["All Sleeves",   "long", "short", "sleeveless"];
const OCCASION_OPTIONS = ["All Occasions", "casual", "party", "formal"];
const CATEGORY_OPTIONS = ["All Categories","dress", "longsleeve",  "pants", "shirt", "shorts", "skirt", "t-shirt"];

const INITIAL_FILTERS = {
  color:    "All Colors",
  sleeve:   "All Sleeves",
  occasion: "All Occasions",
  category: "All Categories",
};

const isDefault = (key, value) => value === INITIAL_FILTERS[key];

// ── Apply ALL 4 filters together ─────────────────────────────────────────────
function applyFilters(items, filters) {
  return items.filter((item) => {
    // COLOR filter
    if (!isDefault("color", filters.color)) {
      const itemColor = (item.color || "").toLowerCase().trim();
      const target    = filters.color.toLowerCase().trim();
      if (itemColor !== target) return false;
    }

    // SLEEVE filter
    if (!isDefault("sleeve", filters.sleeve)) {
      const itemSleeve = (item.sleeves || "").toLowerCase().trim();
      const target     = filters.sleeve.toLowerCase().trim();
      if (itemSleeve !== target) return false;
    }

    // OCCASION filter
    if (!isDefault("occasion", filters.occasion)) {
      const itemOccasion = (item.occasion || "").toLowerCase().trim();
      const target       = filters.occasion.toLowerCase().trim();
      if (itemOccasion !== target) return false;
    }

    // CATEGORY filter
    if (!isDefault("category", filters.category)) {
      const itemCategory = (item.category || "").toLowerCase().trim();
      const target       = filters.category.toLowerCase().trim();
      if (itemCategory !== target) return false;
    }

    return true;
  });
}

// ── Color dot component ───────────────────────────────────────────────────────
const COLOR_DOT_MAP = {
  red: "bg-red-500", blue: "bg-blue-500", black: "bg-gray-900",
  white: "bg-gray-100 border border-gray-300", green: "bg-green-500",
  yellow: "bg-yellow-400", pink: "bg-pink-400", brown: "bg-amber-700",
  grey: "bg-gray-400", purple: "bg-purple-500", orange: "bg-orange-500",
  multi: "bg-gradient-to-r from-pink-400 via-yellow-400 to-blue-400",
};

// ── Lazy image component ──────────────────────────────────────────────────────
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

// ── Dropdown component ────────────────────────────────────────────────────────
function FilterDropdown({ id, emoji, label, options, value, onChange, openDropdown, setOpenDropdown }) {
  const isOpen    = openDropdown === id;
  const isActive  = !isDefault(id === "sleeve" ? "sleeve" : id, value);

  return (
    <div className="relative">
      <button
        onClick={(e) => { e.stopPropagation(); setOpenDropdown(isOpen ? null : id); }}
        className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl transition-all font-semibold text-sm border-2 ${
          isActive
            ? "bg-purple-50 border-purple-400 text-purple-800"
            : "bg-gray-50 border-gray-200 text-gray-700 hover:bg-gray-100"
        }`}
      >
        <span className="flex items-center gap-2 truncate">
          <span>{emoji}</span>
          <span className="truncate">{value}</span>
        </span>
        <ChevronDown className={`w-4 h-4 flex-shrink-0 transition-transform ${isOpen ? "rotate-180" : ""}`} />
      </button>

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
              const dotClass = id === "color" ? COLOR_DOT_MAP[option] : null;
              return (
                <button
                  key={option}
                  onClick={() => { onChange(id, option); setOpenDropdown(null); }}
                  className={`w-full text-left px-3 py-2.5 text-sm flex items-center gap-2 transition-colors hover:bg-purple-50 ${
                    value === option ? "bg-purple-100 font-bold text-purple-800" : "text-gray-700"
                  }`}
                >
                  {dotClass && (
                    <span className={`w-3 h-3 rounded-full flex-shrink-0 ${dotClass}`} />
                  )}
                  <span className="capitalize">{option}</span>
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
  const [wishlist,        setWishlist]        = useState([]);
  const [openDropdown,    setOpenDropdown]    = useState(null);
  const [filters,         setFilters]         = useState(INITIAL_FILTERS);

  // ── Load state ───────────────────────────────────────────────────────────
  useEffect(() => {
    if (location.state) {
      setSelectedImageId(location.state.selectedImageId);
      setSelectedDetails(location.state.selectedDetails);
    }
  }, [location.state]);

  // ── Fetch recommendations (body type + skin tone pre-filter) ─────────────
  useEffect(() => {
    if (!selectedImageId || !selectedDetails) return;

    const fetch = async () => {
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
          const recs = res.data.recommendations || [];
          console.log("✅ Received", recs.length, "recommendations");

          // Debug log
          const colors    = [...new Set(recs.map(r => r.color))];
          const occasions = [...new Set(recs.map(r => r.occasion))];
          const cats      = [...new Set(recs.map(r => r.category))];
          const sleeves   = [...new Set(recs.map(r => r.sleeves))];
          console.log("Colors:", colors, "| Occasions:", occasions, "| Categories:", cats, "| Sleeves:", sleeves);

          setRecommendations(recs);
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

    fetch();
  }, [selectedImageId, selectedDetails]);

  // ── Apply all 4 filters (memoized) ───────────────────────────────────────
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

  const toggleWishlist = useCallback((outfit) => {
    setWishlist((prev) =>
      prev.find((i) => i.rank === outfit.rank)
        ? prev.filter((i) => i.rank !== outfit.rank)
        : [...prev, outfit]
    );
  }, []);

  // Close dropdowns on outside click
  useEffect(() => {
    const close = () => setOpenDropdown(null);
    document.addEventListener("click", close);
    return () => document.removeEventListener("click", close);
  }, []);

  const activeFilterCount = Object.entries(filters).filter(([k, v]) => !isDefault(k, v)).length;

  // ── Guard ────────────────────────────────────────────────────────────────
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
      <div className="relative z-10 px-4 sm:px-6 py-8 max-w-7xl mx-auto">

        {/* ── Header ─────────────────────────────────────────────────────── */}
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
                Based on your <span className="font-semibold text-purple-600">{selectedDetails.body_type}</span> body type
                &amp; <span className="font-semibold text-pink-600">{selectedDetails.skin_tone}</span> skin tone
              </p>
            </div>
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

          {/* ── Filter Panel ──────────────────────────────────────────────── */}
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
              />
              <FilterDropdown
                id="sleeve" emoji="👕" label="Sleeve"
                options={SLEEVE_OPTIONS} value={filters.sleeve}
                onChange={handleFilterChange}
                openDropdown={openDropdown} setOpenDropdown={setOpenDropdown}
              />
              <FilterDropdown
                id="occasion" emoji="🎉" label="Occasion"
                options={OCCASION_OPTIONS} value={filters.occasion}
                onChange={handleFilterChange}
                openDropdown={openDropdown} setOpenDropdown={setOpenDropdown}
              />
              <FilterDropdown
                id="category" emoji="👗" label="Category"
                options={CATEGORY_OPTIONS} value={filters.category}
                onChange={handleFilterChange}
                openDropdown={openDropdown} setOpenDropdown={setOpenDropdown}
              />
            </div>

            {/* Active filter chips */}
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

        {/* ── Loading ───────────────────────────────────────────────────── */}
        {loading && (
          <div className="flex items-center justify-center py-20">
            <Loader className="w-10 h-10 text-purple-500 animate-spin mr-3" />
            <p className="text-lg font-semibold text-gray-600">Finding perfect outfits...</p>
          </div>
        )}

        {/* ── Error ─────────────────────────────────────────────────────── */}
        {error && !loading && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-5 py-4 rounded-xl mb-6 text-sm">
            ⚠️ {error}
          </div>
        )}

        {/* ── Grid ──────────────────────────────────────────────────────── */}
        {!loading && !error && filtered.length > 0 && (
          <motion.div
            layout
            className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4 pb-12"
          >
            <AnimatePresence mode="popLayout">
              {filtered.map((outfit, index) => {
                const inWishlist = wishlist.some((i) => i.rank === outfit.rank);
                const dotClass   = COLOR_DOT_MAP[outfit.color] || "bg-gray-300";

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

                      {/* Wishlist button */}
                      <button
                        onClick={() => toggleWishlist(outfit)}
                        className={`absolute bottom-2 right-2 rounded-full p-2 shadow-md transition-all ${
                          inWishlist
                            ? "bg-red-500 text-white scale-110"
                            : "bg-white/90 text-red-400 hover:bg-red-50"
                        }`}
                      >
                        <Heart className={`w-4 h-4 ${inWishlist ? "fill-current" : ""}`} />
                      </button>
                    </div>

                    {/* Card body */}
                    <div className="p-3">
                      <h3 className="font-bold text-gray-900 text-xs mb-2 truncate">{outfit.outfit_name}</h3>

                      {/* Attribute badges */}
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
                        {/* Color dot */}
                        {outfit.color && (
                          <span className="flex items-center gap-1 text-xs bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded-full font-medium">
                            <span className={`w-2.5 h-2.5 rounded-full ${dotClass}`} />
                            {outfit.color}
                          </span>
                        )}
                      </div>

                      {/* Match bar */}
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

        {/* ── No filter matches ─────────────────────────────────────────── */}
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

        {/* ── No recommendations ────────────────────────────────────────── */}
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