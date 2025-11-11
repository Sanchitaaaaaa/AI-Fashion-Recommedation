import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Moon, Sun, LogOut, Edit3, Trash2, Cog, CheckCircle , ArrowLeft } from "lucide-react";
import { useClerk, useUser } from "@clerk/clerk-react";
import { motion, AnimatePresence } from "framer-motion";

const Settings = () => {
  const navigate = useNavigate();
  const { signOut } = useClerk();
  const { user } = useUser();
  const [theme, setTheme] = useState("light");
  const [showEditModal, setShowEditModal] = useState(false);
  const [editType, setEditType] = useState("");
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState("");

  // Initialize from React state instead of localStorage
  const [faceDetails, setFaceDetails] = useState({
    skinTone: "",
    faceShape: "",
    eyeColor: "",
  });

  const [bodyDetails, setBodyDetails] = useState({
    height: "",
    weight: "",
    bodyShape: "",
  });

  const [editFaceData, setEditFaceData] = useState({
    skinTone: "",
    faceShape: "",
    eyeColor: "",
  });

  const [editBodyData, setEditBodyData] = useState({
    height: "",
    weight: "",
    bodyShape: "",
  });

  // Toast display function
  const displayToast = (message) => {
    setToastMessage(message);
    setShowToast(true);
    setTimeout(() => {
      setShowToast(false);
    }, 3000);
  };

  // Load data on component mount
  useEffect(() => {
    // In a real app, you'd fetch this from your backend or use window.storage
    // For now, we'll initialize with empty values
    const savedFace = {
      skinTone: "",
      faceShape: "",
      eyeColor: "",
    };
    const savedBody = {
      height: "",
      weight: "",
      bodyShape: "",
    };

    setFaceDetails(savedFace);
    setBodyDetails(savedBody);
    setEditFaceData(savedFace);
    setEditBodyData(savedBody);
  }, []);

  // Toggle Theme
  const handleThemeToggle = () => {
    const newTheme = theme === "light" ? "dark" : "light";
    setTheme(newTheme);
    
    if (newTheme === "dark") {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  };

  // Open edit modal
  const openEditModal = (type) => {
    setEditType(type);
    if (type === "face") {
      setEditFaceData(faceDetails);
    } else {
      setEditBodyData(bodyDetails);
    }
    setShowEditModal(true);
  };

  // Save edited data
  const saveEdit = () => {
    if (editType === "face") {
      setFaceDetails(editFaceData);
      // In a real app, save to backend or window.storage
    } else if (editType === "body") {
      setBodyDetails(editBodyData);
      // In a real app, save to backend or window.storage
    }
    setShowEditModal(false);
    displayToast("Details updated successfully!");
  };

  // Clear all stored data
  const clearData = () => {
    if (window.confirm("Are you sure you want to clear all saved data?")) {
      setFaceDetails({
        skinTone: "",
        faceShape: "",
        eyeColor: "",
      });
      setBodyDetails({
        height: "",
        weight: "",
        bodyShape: "",
      });
      displayToast("All data cleared successfully!");
    }
  };

  // Logout with Clerk
  const handleLogout = async () => {
    if (window.confirm("Are you sure you want to logout?")) {
      try {
        await signOut();
        displayToast("Successfully logged out. See you soon!");
        setTimeout(() => {
          navigate("/");
        }, 1500);
      } catch (error) {
        console.error("Error signing out:", error);
        displayToast("Failed to logout. Please try again.");
      }
    }
  };

  // Dropdown options
  const skinTones = ["Fair", "Light", "Medium", "Olive", "Tan", "Brown", "Dark"];
  const faceShapes = ["Oval", "Round", "Square", "Heart", "Diamond", "Long"];
  const eyeColors = ["Brown", "Blue", "Green", "Hazel", "Gray", "Amber"];
  const bodyShapes = [
    "Rectangle",
    "Triangle",
    "Inverted Triangle",
    "Hourglass",
    "Round",
  ];

  return (
    <div className={`min-h-screen ${theme === "dark" ? "bg-gradient-to-br from-gray-900 to-gray-800" : "bg-gradient-to-br from-green-50 to-teal-50"} p-6 transition-colors duration-300`}>
      
      {/* Toast Notification */}
      <AnimatePresence>
        {showToast && (
          <motion.div
            initial={{ opacity: 0, y: -50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -50 }}
            className="fixed top-4 left-1/2 transform -translate-x-1/2 z-50 flex items-center gap-3 bg-white shadow-2xl rounded-full px-6 py-3 border border-green-200"
          >
            <CheckCircle className="w-5 h-5 text-green-500" />
            <p className="text-gray-800 font-medium">{toastMessage}</p>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="max-w-4xl mx-auto">
         <button
          onClick={() => navigate('/home')}
          className="mb-4 flex items-center gap-2 text-gray-600 hover:text-blue-600 transition-colors group"
        >
          <ArrowLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
          <span className="font-medium">Back to Home</span>
        </button>
        <div className={`${theme === "dark" ? "bg-gray-800" : "bg-white"} rounded-2xl shadow-lg p-8 transition-colors duration-300`}>
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <h1 className={`text-3xl font-bold ${theme === "dark" ? "text-white" : "text-gray-800"}`}>Settings</h1>
            <Cog className={`w-8 h-8 ${theme === "dark" ? "text-teal-400" : "text-teal-600"}`} />
          </div>

          {/* Appearance */}
          <div className="space-y-6">
            <div className={`border-2 ${theme === "dark" ? "border-gray-700" : "border-gray-200"} rounded-xl p-6`}>
              <h2 className={`text-xl font-semibold ${theme === "dark" ? "text-white" : "text-gray-800"} mb-4`}>
                Appearance
              </h2>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  {theme === "light" ? (
                    <Sun className={`w-6 h-6 ${theme === "dark" ? "text-gray-300" : "text-gray-700"}`} />
                  ) : (
                    <Moon className={`w-6 h-6 ${theme === "dark" ? "text-gray-300" : "text-gray-700"}`} />
                  )}
                  <div>
                    <p className={`font-medium ${theme === "dark" ? "text-gray-200" : "text-gray-700"}`}>Theme</p>
                    <p className={`text-sm ${theme === "dark" ? "text-gray-400" : "text-gray-500"}`}>
                      Switch between light and dark mode
                    </p>
                  </div>
                </div>
                <button
                  onClick={handleThemeToggle}
                  className={`relative w-14 h-8 rounded-full transition-colors ${
                    theme === "dark" ? "bg-teal-600" : "bg-gray-300"
                  }`}
                >
                  <div
                    className={`absolute top-1 left-1 w-6 h-6 rounded-full bg-white transition-transform ${
                      theme === "dark" ? "translate-x-6" : ""
                    }`}
                  />
                </button>
              </div>
            </div>

            {/* Profile Details */}
            <div className={`border-2 ${theme === "dark" ? "border-gray-700" : "border-gray-200"} rounded-xl p-6`}>
              <h2 className={`text-xl font-semibold ${theme === "dark" ? "text-white" : "text-gray-800"} mb-4`}>
                Profile Details
              </h2>

              <div className="space-y-4">
                {/* Face Details */}
                <div className={`flex items-center justify-between p-4 ${theme === "dark" ? "bg-gray-700" : "bg-gray-50"} rounded-lg`}>
                  <div>
                    <p className={`font-medium ${theme === "dark" ? "text-gray-200" : "text-gray-700"}`}>Face Details</p>
                    <p className={`text-sm ${theme === "dark" ? "text-gray-400" : "text-gray-500"} mt-1`}>
                      Skin Tone: {faceDetails.skinTone || "Not set"} | Face
                      Shape: {faceDetails.faceShape || "Not set"}
                    </p>
                  </div>
                  <button
                    onClick={() => openEditModal("face")}
                    className={`p-2 ${theme === "dark" ? "text-teal-400 hover:bg-gray-600" : "text-teal-600 hover:bg-teal-50"} rounded-lg transition-colors`}
                  >
                    <Edit3 className="w-5 h-5" />
                  </button>
                </div>

                {/* Body Details */}
                <div className={`flex items-center justify-between p-4 ${theme === "dark" ? "bg-gray-700" : "bg-gray-50"} rounded-lg`}>
                  <div>
                    <p className={`font-medium ${theme === "dark" ? "text-gray-200" : "text-gray-700"}`}>Body Details</p>
                    <p className={`text-sm ${theme === "dark" ? "text-gray-400" : "text-gray-500"} mt-1`}>
                      Height: {bodyDetails.height || "Not set"} cm | Weight:{" "}
                      {bodyDetails.weight || "Not set"} kg
                    </p>
                  </div>
                  <button
                    onClick={() => openEditModal("body")}
                    className={`p-2 ${theme === "dark" ? "text-teal-400 hover:bg-gray-600" : "text-teal-600 hover:bg-teal-50"} rounded-lg transition-colors`}
                  >
                    <Edit3 className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>

            {/* Data Management */}
            <div className={`border-2 ${theme === "dark" ? "border-gray-700" : "border-gray-200"} rounded-xl p-6`}>
              <h2 className={`text-xl font-semibold ${theme === "dark" ? "text-white" : "text-gray-800"} mb-4`}>
                Data Management
              </h2>

              <button
                onClick={clearData}
                className={`w-full flex items-center justify-center gap-3 p-4 ${theme === "dark" ? "bg-red-900/30 text-red-400 hover:bg-red-900/50" : "bg-red-50 text-red-600 hover:bg-red-100"} rounded-lg transition-colors`}
              >
                <Trash2 className="w-5 h-5" />
                Clear All Data
              </button>
            </div>

            {/* Account Section */}
            <div className={`border-2 ${theme === "dark" ? "border-gray-700" : "border-gray-200"} rounded-xl p-6`}>
              <h2 className={`text-xl font-semibold ${theme === "dark" ? "text-white" : "text-gray-800"} mb-4`}>
                Account
              </h2>

              {user && (
                <div className={`mb-4 p-4 ${theme === "dark" ? "bg-gray-700" : "bg-gray-50"} rounded-lg`}>
                  <p className={`text-sm ${theme === "dark" ? "text-gray-400" : "text-gray-500"}`}>Logged in as</p>
                  <p className={`font-medium ${theme === "dark" ? "text-gray-200" : "text-gray-700"} mt-1`}>
                    {user.firstName || user.emailAddresses[0]?.emailAddress}
                  </p>
                </div>
              )}

              <button
                onClick={handleLogout}
                className={`w-full flex items-center justify-center gap-3 p-4 ${theme === "dark" ? "bg-gray-700 text-gray-200 hover:bg-gray-600" : "bg-gray-100 text-gray-700 hover:bg-gray-200"} rounded-lg transition-colors`}
              >
                <LogOut className="w-5 h-5" />
                Logout
              </button>
            </div>
          </div>
        </div>

        {/* Edit Modal */}
        {showEditModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className={`${theme === "dark" ? "bg-gray-800" : "bg-white"} rounded-2xl p-6 max-w-md w-full`}>
              <h3 className={`text-2xl font-bold ${theme === "dark" ? "text-white" : "text-gray-800"} mb-4`}>
                Edit {editType === "face" ? "Face" : "Body"} Details
              </h3>

              {/* Face Edit */}
              {editType === "face" && (
                <div className="space-y-4">
                  <div>
                    <label className={`block text-sm font-semibold ${theme === "dark" ? "text-gray-200" : "text-gray-700"} mb-2`}>
                      Skin Tone
                    </label>
                    <select
                      value={editFaceData.skinTone}
                      onChange={(e) =>
                        setEditFaceData({
                          ...editFaceData,
                          skinTone: e.target.value,
                        })
                      }
                      className={`w-full p-3 border-2 ${theme === "dark" ? "border-gray-600 bg-gray-700 text-white" : "border-gray-200 bg-white text-gray-900"} rounded-lg focus:border-teal-600 focus:outline-none`}
                    >
                      <option value="">Select</option>
                      {skinTones.map((tone) => (
                        <option key={tone} value={tone}>
                          {tone}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className={`block text-sm font-semibold ${theme === "dark" ? "text-gray-200" : "text-gray-700"} mb-2`}>
                      Face Shape
                    </label>
                    <select
                      value={editFaceData.faceShape}
                      onChange={(e) =>
                        setEditFaceData({
                          ...editFaceData,
                          faceShape: e.target.value,
                        })
                      }
                      className={`w-full p-3 border-2 ${theme === "dark" ? "border-gray-600 bg-gray-700 text-white" : "border-gray-200 bg-white text-gray-900"} rounded-lg focus:border-teal-600 focus:outline-none`}
                    >
                      <option value="">Select</option>
                      {faceShapes.map((shape) => (
                        <option key={shape} value={shape}>
                          {shape}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className={`block text-sm font-semibold ${theme === "dark" ? "text-gray-200" : "text-gray-700"} mb-2`}>
                      Eye Color
                    </label>
                    <select
                      value={editFaceData.eyeColor}
                      onChange={(e) =>
                        setEditFaceData({
                          ...editFaceData,
                          eyeColor: e.target.value,
                        })
                      }
                      className={`w-full p-3 border-2 ${theme === "dark" ? "border-gray-600 bg-gray-700 text-white" : "border-gray-200 bg-white text-gray-900"} rounded-lg focus:border-teal-600 focus:outline-none`}
                    >
                      <option value="">Select</option>
                      {eyeColors.map((color) => (
                        <option key={color} value={color}>
                          {color}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              )}

              {/* Body Edit */}
              {editType === "body" && (
                <div className="space-y-4">
                  <div>
                    <label className={`block text-sm font-semibold ${theme === "dark" ? "text-gray-200" : "text-gray-700"} mb-2`}>
                      Height (cm)
                    </label>
                    <input
                      type="number"
                      value={editBodyData.height}
                      onChange={(e) =>
                        setEditBodyData({
                          ...editBodyData,
                          height: e.target.value,
                        })
                      }
                      className={`w-full p-3 border-2 ${theme === "dark" ? "border-gray-600 bg-gray-700 text-white" : "border-gray-200 bg-white text-gray-900"} rounded-lg focus:border-teal-600 focus:outline-none`}
                    />
                  </div>

                  <div>
                    <label className={`block text-sm font-semibold ${theme === "dark" ? "text-gray-200" : "text-gray-700"} mb-2`}>
                      Weight (kg)
                    </label>
                    <input
                      type="number"
                      value={editBodyData.weight}
                      onChange={(e) =>
                        setEditBodyData({
                          ...editBodyData,
                          weight: e.target.value,
                        })
                      }
                      className={`w-full p-3 border-2 ${theme === "dark" ? "border-gray-600 bg-gray-700 text-white" : "border-gray-200 bg-white text-gray-900"} rounded-lg focus:border-teal-600 focus:outline-none`}
                    />
                  </div>

                  <div>
                    <label className={`block text-sm font-semibold ${theme === "dark" ? "text-gray-200" : "text-gray-700"} mb-2`}>
                      Body Shape
                    </label>
                    <select
                      value={editBodyData.bodyShape}
                      onChange={(e) =>
                        setEditBodyData({
                          ...editBodyData,
                          bodyShape: e.target.value,
                        })
                      }
                      className={`w-full p-3 border-2 ${theme === "dark" ? "border-gray-600 bg-gray-700 text-white" : "border-gray-200 bg-white text-gray-900"} rounded-lg focus:border-teal-600 focus:outline-none`}
                    >
                      <option value="">Select</option>
                      {bodyShapes.map((shape) => (
                        <option key={shape} value={shape}>
                          {shape}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              )}

              {/* Buttons */}
              <div className="flex gap-3 mt-6">
                <button
                  onClick={() => setShowEditModal(false)}
                  className={`flex-1 px-4 py-3 ${theme === "dark" ? "bg-gray-700 text-gray-200 hover:bg-gray-600" : "bg-gray-200 text-gray-700 hover:bg-gray-300"} rounded-lg transition-colors`}
                >
                  Cancel
                </button>
                <button
                  onClick={saveEdit}
                  className="flex-1 px-4 py-3 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors"
                >
                  Save Changes
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Settings;