import { motion, AnimatePresence } from "framer-motion";
import { useUser } from "@clerk/clerk-react";
import { useState, useEffect } from "react";
import { Trash2, Download, ArrowLeft } from "lucide-react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

export default function UserDetails() {
  const navigate = useNavigate();
  const { user } = useUser();
  const [uploadedImages, setUploadedImages] = useState([]);
  const [selectedImageId, setSelectedImageId] = useState(null);
  const [selectedDetails, setSelectedDetails] = useState(null);
  const [loading, setLoading] = useState(true);

  // Fetch user images on mount
  useEffect(() => {
    fetchUserImages();
  }, []);

  const fetchUserImages = async () => {
    setLoading(true);
    try {
      const response = await axios.get(
        `http://127.0.0.1:8000/user/images/default_user`
      );

      if (response.data.success) {
        setUploadedImages(response.data.images || []);
      }
    } catch (error) {
      console.error("Error fetching images:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectImage = async (imageId) => {
    setLoading(true);
    try {
      const response = await axios.get(
        `http://127.0.0.1:8000/user/features/${imageId}`
      );

      if (response.data.features) {
        setSelectedImageId(imageId);
        setSelectedDetails(response.data.features);
      }
    } catch (error) {
      console.error("Error fetching image details:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteImage = async (imageId) => {
    if (!window.confirm("Are you sure you want to delete this image?")) {
      return;
    }

    try {
      await axios.delete(`http://127.0.0.1:8000/user/images/${imageId}`);
      setUploadedImages(uploadedImages.filter((img) => img.image_id !== imageId));
      if (selectedImageId === imageId) {
        setSelectedImageId(null);
        setSelectedDetails(null);
      }
      alert("Image deleted successfully");
    } catch (error) {
      console.error("Error deleting image:", error);
      alert("Failed to delete image");
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 p-6"
    >
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
              <h1 className="text-5xl font-bold text-gray-900">👤 User Details</h1>
              <p className="text-gray-600 mt-2">Your uploaded photos and analysis</p>
            </div>
          </div>
        </motion.div>

        {loading ? (
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
              Loading your images...
            </p>
          </motion.div>
        ) : uploadedImages.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-center py-20 bg-white rounded-2xl shadow-lg"
          >
            <p className="text-2xl font-bold text-gray-900 mb-2">No Images Yet</p>
            <p className="text-gray-600 mb-6">
              Upload your first photo to get started with style recommendations
            </p>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => navigate("/recommendations")}
              className="px-6 py-3 bg-gradient-to-r from-pink-500 to-rose-500 text-white font-semibold rounded-lg hover:shadow-lg transition-all"
            >
              Upload Now →
            </motion.button>
          </motion.div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Images Gallery */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
              className="lg:col-span-1"
            >
              <div className="bg-white rounded-2xl shadow-lg p-6 sticky top-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4">
                  📸 Your Photos ({uploadedImages.length})
                </h2>

                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {uploadedImages.map((image) => (
                    <motion.div
                      key={image.image_id}
                      whileHover={{ scale: 1.02 }}
                      onClick={() => handleSelectImage(image.image_id)}
                      className={`relative rounded-lg overflow-hidden cursor-pointer border-2 transition-all group ${
                        selectedImageId === image.image_id
                          ? "border-purple-500 shadow-lg"
                          : "border-gray-200 hover:border-purple-300"
                      }`}
                    >
                      <img
                        src={`data:image/jpeg;base64,${image.image_data || ""}`}
                        alt="uploaded"
                        className="w-full h-32 object-cover"
                        onError={(e) => {
                          e.target.src =
                            "https://via.placeholder.com/200/cccccc/ffffff?text=Image";
                        }}
                      />

                      {selectedImageId === image.image_id && (
                        <div className="absolute inset-0 bg-purple-500/20 flex items-center justify-center">
                          <span className="text-white font-bold text-sm">✓ Selected</span>
                        </div>
                      )}

                      <motion.button
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.9 }}
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteImage(image.image_id);
                        }}
                        className="absolute top-2 right-2 bg-red-500 hover:bg-red-600 text-white rounded-full p-1.5 transition-colors shadow-lg opacity-0 group-hover:opacity-100"
                      >
                        <Trash2 className="w-4 h-4" />
                      </motion.button>

                      <div className="absolute bottom-0 left-0 right-0 bg-black/40 p-2">
                        <p className="text-white text-xs font-semibold truncate">
                          {image.file_name}
                        </p>
                        <p className="text-white/70 text-xs">
                          {new Date(image.uploaded_at).toLocaleDateString()}
                        </p>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>
            </motion.div>

            {/* Analysis Details */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 }}
              className="lg:col-span-2"
            >
              {selectedDetails ? (
                <div className="space-y-6">
                  {/* Large Image Preview */}
                  <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="bg-white rounded-2xl shadow-lg overflow-hidden border-4 border-purple-200"
                  >
                    <img
                      src={`data:image/jpeg;base64,${
                        uploadedImages.find((img) => img.image_id === selectedImageId)
                          ?.image_data || ""
                      }`}
                      alt="selected"
                      className="w-full h-96 object-cover"
                      onError={(e) => {
                        e.target.src =
                          "https://via.placeholder.com/400/cccccc/ffffff?text=Image";
                      }}
                    />
                  </motion.div>

                  {/* Analysis Cards */}
                  <div className="space-y-4">
                    {/* Body Type */}
                    <motion.div
                      whileHover={{ y: -5 }}
                      className="bg-white rounded-2xl shadow-lg p-6 border-l-4 border-purple-500"
                    >
                      <div className="flex items-start justify-between mb-4">
                        <div>
                          <p className="text-sm text-gray-600 font-semibold">
                            👗 BODY TYPE
                          </p>
                          <h3 className="text-3xl font-bold text-purple-600 mt-2">
                            {selectedDetails.body_type}
                          </h3>
                        </div>
                        <div className="text-5xl">👗</div>
                      </div>

                      {/* Confidence Bar */}
                      <div className="mt-4">
                        <div className="flex items-center justify-between mb-2">
                          <p className="text-xs font-semibold text-gray-600">Confidence</p>
                          <p className="text-sm font-bold text-purple-600">
                            {(
                              (selectedDetails.body_type_confidence || 0.85) * 100
                            ).toFixed(0)}
                            %
                          </p>
                        </div>
                        <div className="w-full h-3 bg-gray-200 rounded-full overflow-hidden">
                          <motion.div
                            initial={{ width: 0 }}
                            animate={{
                              width: `${(selectedDetails.body_type_confidence || 0.85) * 100}%`,
                            }}
                            transition={{ duration: 1, ease: "easeOut" }}
                            className="h-full bg-gradient-to-r from-purple-400 to-purple-600"
                          />
                        </div>
                      </div>

                      {/* Description */}
                      <p className="text-sm text-gray-600 mt-4">
                        {getBodyTypeDescription(selectedDetails.body_type)}
                      </p>
                    </motion.div>

                    {/* Skin Tone */}
                    <motion.div
                      whileHover={{ y: -5 }}
                      className="bg-white rounded-2xl shadow-lg p-6 border-l-4 border-pink-500"
                    >
                      <div className="flex items-start justify-between mb-4">
                        <div>
                          <p className="text-sm text-gray-600 font-semibold">
                            🎨 SKIN TONE
                          </p>
                          <h3 className="text-3xl font-bold text-pink-600 mt-2">
                            {selectedDetails.skin_tone}
                          </h3>
                        </div>
                        <div className="text-5xl">🎨</div>
                      </div>

                      {/* Confidence Bar */}
                      <div className="mt-4">
                        <div className="flex items-center justify-between mb-2">
                          <p className="text-xs font-semibold text-gray-600">Confidence</p>
                          <p className="text-sm font-bold text-pink-600">
                            {(
                              (selectedDetails.skin_tone_confidence || 0.85) * 100
                            ).toFixed(0)}
                            %
                          </p>
                        </div>
                        <div className="w-full h-3 bg-gray-200 rounded-full overflow-hidden">
                          <motion.div
                            initial={{ width: 0 }}
                            animate={{
                              width: `${(selectedDetails.skin_tone_confidence || 0.85) * 100}%`,
                            }}
                            transition={{ duration: 1, ease: "easeOut" }}
                            className="h-full bg-gradient-to-r from-pink-400 to-pink-600"
                          />
                        </div>
                      </div>

                      {/* Description */}
                      <p className="text-sm text-gray-600 mt-4">
                        {getSkinToneDescription(selectedDetails.skin_tone)}
                      </p>
                    </motion.div>

                    {/* Body Measurements */}
                    {selectedDetails.features && (
                      <motion.div
                        whileHover={{ y: -5 }}
                        className="bg-white rounded-2xl shadow-lg p-6 border-l-4 border-blue-500"
                      >
                        <p className="text-sm text-gray-600 font-semibold mb-4">
                          📏 BODY MEASUREMENTS
                        </p>

                        <div className="grid grid-cols-2 gap-4">
                          <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                            <p className="text-xs text-gray-600 font-semibold">
                              Shoulder/Hip Ratio
                            </p>
                            <p className="text-2xl font-bold text-blue-600 mt-2">
                              {(selectedDetails.features.shoulder_hip_ratio || 0).toFixed(
                                2
                              )}
                            </p>
                          </div>

                          <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
                            <p className="text-xs text-gray-600 font-semibold">
                              Waist/Hip Ratio
                            </p>
                            <p className="text-2xl font-bold text-purple-600 mt-2">
                              {(selectedDetails.features.waist_hip_ratio || 0).toFixed(2)}
                            </p>
                          </div>

                          <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                            <p className="text-xs text-gray-600 font-semibold">
                              Leg/Torso Ratio
                            </p>
                            <p className="text-2xl font-bold text-green-600 mt-2">
                              {(selectedDetails.features.leg_torso_ratio || 0).toFixed(2)}
                            </p>
                          </div>

                          <div className="bg-orange-50 p-4 rounded-lg border border-orange-200">
                            <p className="text-xs text-gray-600 font-semibold">
                              Arm/Body Ratio
                            </p>
                            <p className="text-2xl font-bold text-orange-600 mt-2">
                              {(selectedDetails.features.arm_body_ratio || 0).toFixed(2)}
                            </p>
                          </div>
                        </div>
                      </motion.div>
                    )}

                    {/* Action Buttons */}
                    <div className="flex gap-4 pt-4">
                      <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => navigate("/recommendations")}
                        className="flex-1 px-6 py-3 bg-gradient-to-r from-pink-500 to-rose-500 text-white font-semibold rounded-lg hover:shadow-lg transition-all"
                      >
                        View Recommendations →
                      </motion.button>

                      <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => handleDeleteImage(selectedImageId)}
                        className="px-6 py-3 bg-red-100 hover:bg-red-200 text-red-600 font-semibold rounded-lg transition-all flex items-center gap-2"
                      >
                        <Trash2 className="w-4 h-4" />
                        Delete
                      </motion.button>
                    </div>
                  </div>
                </div>
              ) : (
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="text-center py-20 bg-white rounded-2xl shadow-lg h-full flex flex-col items-center justify-center"
                >
                  <p className="text-2xl font-bold text-gray-900 mb-2">
                    Select an Image
                  </p>
                  <p className="text-gray-600">
                    Click on an image from the gallery to view analysis details
                  </p>
                </motion.div>
              )}
            </motion.div>
          </div>
        )}
      </div>
    </motion.div>
  );
}

// Helper functions
function getBodyTypeDescription(bodyType) {
  const descriptions = {
    Hourglass:
      "Curvy and balanced body type with similar shoulder and hip width and a defined waist.",
    Apple:
      "Weight is distributed around the midsection with broader shoulders and narrower hips.",
    Pear: "Wider hips and thighs with narrower shoulders. A classic pear-shaped silhouette.",
    Rectangle:
      "Balanced body with similar measurements throughout. A straight and uniform figure.",
    "Inverted Triangle":
      "Broad shoulders with a narrower hip area. An athletic, V-shaped silhouette.",
    Unknown: "Body type could not be determined. Please try another image.",
  };
  return descriptions[bodyType] || descriptions.Unknown;
}

function getSkinToneDescription(skinTone) {
  const descriptions = {
    Fair: "Light, fair complexion. This skin tone pair well with cool and jewel tones.",
    Medium: "Medium complexion. Versatile with both warm and cool color palettes.",
    Tan: "Warm, tan complexion. Earthy and warm colors complement this tone beautifully.",
    Deep: "Deep, rich complexion. Bold colors and jewel tones are particularly flattering.",
    Unknown: "Skin tone could not be determined. Please try another image.",
  };
  return descriptions[skinTone] || descriptions.Unknown;
}