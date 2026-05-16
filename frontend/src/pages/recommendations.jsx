import { useState, useEffect, useCallback, useMemo } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import axios from "axios";
import { motion, AnimatePresence } from "framer-motion";

import {
  Loader,
  Heart,
  ShoppingBag,
  ArrowLeft,
  ChevronDown,
  X,
  AlertTriangle,
  CheckCircle,
} from "lucide-react";

// ─────────────────────────────────────────────────────────────
// FILTER OPTIONS
// ─────────────────────────────────────────────────────────────

const COLOR_OPTIONS = [
  "All Colors",
  "Red",
  "Blue",
  "Black",
  "White",
  "Green",
  "Yellow",
  "Pink",
  "Brown",
  "Grey",
  "Purple",
  "Orange",
  "Multi",
];

const SLEEVE_OPTIONS = [
  "All Sleeves",
  "long",
  "short",
  "sleeveless",
];

const OCCASION_OPTIONS = [
  "All Occasions",
  "Casual",
  "Party",
  "Formal",
  "Sports",
  "Ethnic",
];

const CATEGORY_OPTIONS = [
  "All Categories",

  "Tshirts",
  "Shirts",
  "Tops",
  "Blouses",

  "Sweatshirts",
  "Jackets",
  "Blazers",

  "Kurtas",
  "Tunics",

  "Dresses",

  "Jeans",
  "Trousers",
  "Shorts",
  "Skirts",
  "Leggings",
];

const INITIAL_FILTERS = {

  color: "All Colors",

  sleeve: "All Sleeves",

  occasion: "All Occasions",

  category: "All Categories",
};

const isDefault = (key, value) =>
  value === INITIAL_FILTERS[key];

// ─────────────────────────────────────────────────────────────
// SKIN TONE COLORS
// ─────────────────────────────────────────────────────────────

const SKIN_TONE_COLORS = {

  Fair: [
    "blue",
    "pink",
    "purple",
    "red",
    "green",
    "black",
    "white",
    "grey",
  ],

  Medium: [
    "red",
    "blue",
    "green",
    "yellow",
    "brown",
    "white",
    "black",
    "orange",
  ],

  Tan: [
    "white",
    "yellow",
    "orange",
    "red",
    "green",
    "blue",
    "brown",
    "multi",
  ],

  Deep: [
    "white",
    "yellow",
    "red",
    "orange",
    "green",
    "blue",
    "multi",
    "pink",
  ],
};

function isColorSuitable(color, skinTone) {

  if (!color || !skinTone) return true;

  const ok = SKIN_TONE_COLORS[skinTone];

  if (!ok) return true;

  return ok.includes(
    color.toLowerCase().trim()
  );
}

// ─────────────────────────────────────────────────────────────
// FILTER FUNCTION
// ─────────────────────────────────────────────────────────────

function applyFilters(items, filters) {

  return items.filter((item) => {

    if (!isDefault("color", filters.color)) {

      if (

        (item.color || "")
          .toLowerCase()
          .trim()

        !==

        filters.color
          .toLowerCase()
          .trim()

      ) return false;
    }

    if (!isDefault("sleeve", filters.sleeve)) {

      if (

        (item.sleeves || "")
          .toLowerCase()
          .trim()

        !==

        filters.sleeve
          .toLowerCase()
          .trim()

      ) return false;
    }

    if (!isDefault("occasion", filters.occasion)) {

      if (

        (item.occasion || "")
          .toLowerCase()
          .trim()

        !==

        filters.occasion
          .toLowerCase()
          .trim()

      ) return false;
    }

    if (!isDefault("category", filters.category)) {

      if (

        (item.category || "")
          .toLowerCase()
          .trim()

        !==

        filters.category
          .toLowerCase()
          .trim()

      ) return false;
    }

    return true;
  });
}

// ─────────────────────────────────────────────────────────────
// COLOR DOTS
// ─────────────────────────────────────────────────────────────

const COLOR_DOT_MAP = {

  red: "bg-red-500",

  blue: "bg-blue-500",

  black: "bg-gray-900",

  white:
    "bg-gray-100 border border-gray-300",

  green: "bg-green-500",

  yellow: "bg-yellow-400",

  pink: "bg-pink-400",

  brown: "bg-amber-700",

  grey: "bg-gray-400",

  purple: "bg-purple-500",

  orange: "bg-orange-500",

  multi:
    "bg-gradient-to-r from-pink-400 via-yellow-400 to-blue-400",
};

// ─────────────────────────────────────────────────────────────
// HIGH QUALITY IMAGE COMPONENT
// ─────────────────────────────────────────────────────────────

function OutfitImage({ src, alt }) {

  const [loaded, setLoaded] = useState(false);

  const [error, setError] = useState(false);

  if (!src || error) {

    return (

      <div className="w-full h-full flex items-center justify-center text-6xl bg-gradient-to-br from-purple-100 to-pink-100">

        👗

      </div>
    );
  }

  return (

    <>

      {!loaded && (

        <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-purple-50 to-pink-50">

          <Loader className="w-8 h-8 text-purple-400 animate-spin" />

        </div>
      )}

      <img

        src={src}

        alt={alt}

        loading="lazy"

        decoding="async"

        onLoad={() => setLoaded(true)}

        onError={() => setError(true)}

        className={`

          w-full
          h-full

          object-contain

          bg-white

          transition-all
          duration-500

          hover:scale-105

          ${loaded
            ? "opacity-100"
            : "opacity-0"
          }

        `}
      />

    </>
  );
}

// ─────────────────────────────────────────────────────────────
// MAIN PAGE
// ─────────────────────────────────────────────────────────────

export default function RecommendationsPage() {

  const location = useLocation();

  const navigate = useNavigate();

  const [selectedImageId, setSelectedImageId] =
    useState(null);

  const [selectedDetails, setSelectedDetails] =
    useState(null);

  const [recommendations, setRecommendations] =
    useState([]);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState(null);

  const [wishlist, setWishlist] =
    useState(new Set());

  const [toast, setToast] =
    useState(null);

  const [filters, setFilters] =
    useState(INITIAL_FILTERS);

  // ─────────────────────────────────────────────────────────

  useEffect(() => {

    if (location.state) {

      setSelectedImageId(
        location.state.selectedImageId
      );

      setSelectedDetails(
        location.state.selectedDetails
      );
    }

  }, [location.state]);

  // ─────────────────────────────────────────────────────────
  // FETCH RECOMMENDATIONS
  // ─────────────────────────────────────────────────────────

  useEffect(() => {

    if (
      !selectedImageId
      ||
      !selectedDetails
    ) return;

    const fetchRecommendations = async () => {

      try {

        setLoading(true);

        setError(null);

        const mappedGender =

          selectedDetails.gender === "Female"

            ? "Women"

            : "Men";

        const payload = {

          image_id:
            selectedImageId,

          top_k: 100,

          gender:
            mappedGender,

          body_type:
            selectedDetails.body_type,

          skin_tone:
            selectedDetails.skin_tone,

          height_category:
            selectedDetails.height_category
            || "Average",
        };

        console.log(
          "📤 Payload:",
          payload
        );

        const res = await axios.post(

          "http://127.0.0.1:8000/recommend/generate",

          payload
        );

        if (res.data.success) {

          setRecommendations(

            res.data.recommendations || []
          );

        } else {

          setError(
            res.data.error
          );
        }

      } catch (err) {

        console.error(err);

        setError(
          "Cannot connect to backend"
        );

      } finally {

        setLoading(false);
      }
    };

    fetchRecommendations();

  }, [selectedImageId, selectedDetails]);

  // ─────────────────────────────────────────────────────────

  const filtered = useMemo(

    () => applyFilters(
      recommendations,
      filters
    ),

    [recommendations, filters]
  );

  // ─────────────────────────────────────────────────────────

  const toggleWishlist = (name) => {

    setWishlist((prev) => {

      const next = new Set(prev);

      if (next.has(name)) {

        next.delete(name);

        setToast("Removed from wishlist");

      } else {

        next.add(name);

        setToast("Added to wishlist ❤️");
      }

      return next;
    });

    setTimeout(() => {

      setToast(null);

    }, 2000);
  };

  // ─────────────────────────────────────────────────────────

  if (
    !selectedImageId
    ||
    !selectedDetails
  ) {

    return (

      <div className="min-h-screen flex items-center justify-center">

        No image selected

      </div>
    );
  }

  // ─────────────────────────────────────────────────────────

  return (

    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">

      {/* TOAST */}

      <AnimatePresence>

        {toast && (

          <motion.div

            initial={{
              opacity: 0,
              y: -30,
            }}

            animate={{
              opacity: 1,
              y: 0,
            }}

            exit={{
              opacity: 0,
              y: -30,
            }}

            className="fixed top-5 left-1/2 -translate-x-1/2 bg-white shadow-xl px-5 py-3 rounded-full z-50 font-semibold"
          >

            {toast}

          </motion.div>
        )}

      </AnimatePresence>

      <div className="max-w-7xl mx-auto px-4 py-8">

        {/* HEADER */}

        <div className="flex items-center gap-4 mb-8">

          <button

            onClick={() => navigate("/home")}

            className="p-3 bg-white rounded-xl shadow hover:shadow-lg transition-all"
          >

            <ArrowLeft className="w-5 h-5" />

          </button>

          <div>

            <h1 className="text-3xl font-bold text-gray-900">

              👗 AI Fashion Recommendations

            </h1>

            <p className="text-gray-500 mt-1">

              Personalized outfit suggestions

            </p>

          </div>

        </div>

        {/* USER DETAILS */}

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">

          <div className="bg-white p-4 rounded-2xl shadow">

            <p className="text-xs text-gray-400">

              Gender

            </p>

            <p className="font-bold text-blue-600 mt-1">

              {
                selectedDetails.gender
              }

            </p>

          </div>

          <div className="bg-white p-4 rounded-2xl shadow">

            <p className="text-xs text-gray-400">

              Body Type

            </p>

            <p className="font-bold text-purple-600 mt-1">

              {
                selectedDetails.body_type
              }

            </p>

          </div>

          <div className="bg-white p-4 rounded-2xl shadow">

            <p className="text-xs text-gray-400">

              Skin Tone

            </p>

            <p className="font-bold text-pink-600 mt-1">

              {
                selectedDetails.skin_tone
              }

            </p>

          </div>

          <div className="bg-gradient-to-r from-purple-500 to-pink-500 text-white p-4 rounded-2xl shadow">

            <p className="text-xs opacity-80">

              Results

            </p>

            <p className="font-bold text-xl mt-1">

              {filtered.length}

            </p>

          </div>

        </div>

        {/* LOADING */}

        {loading && (

          <div className="flex items-center justify-center py-20">

            <Loader className="w-10 h-10 animate-spin text-purple-500 mr-3" />

            <p className="font-semibold text-lg">

              Finding best outfits...

            </p>

          </div>
        )}

        {/* ERROR */}

        {error && (

          <div className="bg-red-100 text-red-700 p-4 rounded-xl mb-6">

            {error}

          </div>
        )}

        {/* GRID */}

        {!loading && !error && (

          <motion.div

            layout

            className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
          >

            <AnimatePresence>

              {filtered.map((outfit, index) => {

                const inWishlist =
                  wishlist.has(
                    outfit.outfit_name
                  );

                const dotClass =
                  COLOR_DOT_MAP[
                    outfit.color
                      ?.toLowerCase()
                  ]
                  ||
                  "bg-gray-300";

                const colorUnsafe =

                  !isColorSuitable(
                    outfit.color,
                    selectedDetails.skin_tone
                  );

                return (

                  <motion.div

                    key={index}

                    layout

                    initial={{
                      opacity: 0,
                      scale: 0.92,
                    }}

                    animate={{
                      opacity: 1,
                      scale: 1,
                    }}

                    exit={{
                      opacity: 0,
                    }}

                    whileHover={{
                      y: -8,
                    }}

                    className="bg-white rounded-3xl overflow-hidden shadow-md hover:shadow-2xl transition-all border border-gray-100"
                  >

                    {/* IMAGE */}

                    <div className="relative h-80 bg-white overflow-hidden">

                      <OutfitImage

                        src={outfit.image_url}

                        alt={outfit.outfit_name}
                      />

                      {/* SCORE */}

                      <div className="absolute top-3 left-3 bg-emerald-500 text-white px-3 py-1 rounded-full text-xs font-bold shadow">

                        {
                          outfit.similarity_percentage
                        }

                      </div>

                      {/* RANK */}

                      <div className="absolute top-3 right-3 bg-white text-purple-600 w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold shadow">

                        #
                        {
                          outfit.rank
                        }

                      </div>

                      {/* WISHLIST */}

                      <button

                        onClick={() =>
                          toggleWishlist(
                            outfit.outfit_name
                          )
                        }

                        className={`

                          absolute
                          bottom-3
                          right-3

                          p-2
                          rounded-full
                          shadow-lg

                          transition-all

                          ${inWishlist

                            ? "bg-red-500 text-white"

                            : "bg-white text-red-400"

                          }

                        `}
                      >

                        <Heart

                          className={`w-5 h-5 ${
                            inWishlist
                              ? "fill-current"
                              : ""
                          }`}
                        />

                      </button>

                    </div>

                    {/* CONTENT */}

                    <div className="p-4">

                      <h3 className="font-bold text-gray-900 text-sm truncate mb-3">

                        {
                          outfit.outfit_name
                        }

                      </h3>

                      {/* TAGS */}

                      <div className="flex flex-wrap gap-2 mb-3">

                        {outfit.category && (

                          <span className="px-2 py-1 bg-purple-100 text-purple-700 rounded-full text-xs font-medium">

                            {
                              outfit.category
                            }

                          </span>
                        )}

                        {outfit.occasion && (

                          <span className="px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">

                            {
                              outfit.occasion
                            }

                          </span>
                        )}

                        {outfit.color && (

                          <span className="flex items-center gap-1 px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-xs font-medium">

                            <span
                              className={`w-3 h-3 rounded-full ${dotClass}`}
                            />

                            {
                              outfit.color
                            }

                          </span>
                        )}

                      </div>

                      {/* SKIN WARNING */}

                      {colorUnsafe && (

                        <div className="flex items-center gap-2 bg-red-50 border border-red-200 text-red-600 rounded-xl px-3 py-2 text-xs mb-3">

                          <AlertTriangle className="w-4 h-4" />

                          Not ideal for your skin tone

                        </div>
                      )}

                      {/* SCORE BAR */}

                      <div className="w-full h-2 bg-gray-100 rounded-full overflow-hidden">

                        <motion.div

                          initial={{
                            width: 0,
                          }}

                          animate={{
                            width:
                              `${outfit.similarity_score * 100}%`,
                          }}

                          transition={{
                            duration: 0.7,
                          }}

                          className="h-full bg-gradient-to-r from-purple-500 to-pink-500 rounded-full"
                        />

                      </div>

                    </div>

                  </motion.div>
                );
              })}

            </AnimatePresence>

          </motion.div>
        )}

      </div>

    </div>
  );
}