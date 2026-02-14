import { useState } from "react";
import axios from "axios";
import { motion } from "framer-motion";
import { Upload, Loader, CheckCircle, AlertCircle } from "lucide-react";

export default function UploadPage({ onUploadSuccess }) {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null);
  const [dragActive, setDragActive] = useState(false);

  const handleFile = (f) => {
    if (f && f.type.startsWith("image/")) {
      setFile(f);
      setPreview(URL.createObjectURL(f));
      setStatus(null);
    } else {
      setStatus("error");
      setTimeout(() => setStatus(null), 3000);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);
    formData.append("user_id", "default_user");

    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/user/upload",
        formData
      );

      if (response.data.success) {
        setStatus("success");
        const newImage = {
          id: response.data.imageId,
          url: preview,
          fileName: file.name,
        };
        if (onUploadSuccess) {
          onUploadSuccess(newImage);
        }
        setTimeout(() => {
          setFile(null);
          setPreview(null);
        }, 2000);
      }
    } catch (error) {
      console.error(error);
      setStatus("error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 p-6 flex items-center justify-center">
      <div className="w-full max-w-2xl">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-5xl font-bold text-gray-900 mb-3">
            Upload Your Photo
          </h1>
          <p className="text-lg text-gray-600">
            Get AI-powered style recommendations based on your body type
          </p>
        </motion.div>

        {/* Upload Area */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-3xl shadow-xl p-8 mb-6"
        >
          {!preview ? (
            <div
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              className={`relative border-3 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all ${
                dragActive
                  ? "border-purple-500 bg-purple-50"
                  : "border-gray-300 hover:border-purple-400 hover:bg-gray-50"
              }`}
            >
              <input
                type="file"
                accept="image/*"
                onChange={(e) => handleFile(e.target.files?.[0])}
                className="absolute inset-0 opacity-0 cursor-pointer"
              />

              <motion.div
                animate={{ y: [0, -10, 0] }}
                transition={{ duration: 2, repeat: Infinity }}
                className="flex justify-center mb-4"
              >
                <div className="w-20 h-20 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center shadow-lg">
                  <Upload className="w-10 h-10 text-white" />
                </div>
              </motion.div>

              <h3 className="text-2xl font-bold text-gray-900 mb-2">
                Drop your photo here
              </h3>
              <p className="text-gray-600 mb-4">or click to select a file</p>
              <p className="text-sm text-gray-500">
                Full-body photos work best • JPG, PNG • Max 10MB
              </p>
            </div>
          ) : (
            <div className="space-y-6">
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="relative rounded-2xl overflow-hidden border-4 border-purple-200"
              >
                <img
                  src={preview}
                  alt="Preview"
                  className="w-full h-64 sm:h-96 object-cover"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent"></div>
              </motion.div>

              <div className="flex gap-3">
                <button
                  onClick={() => {
                    setFile(null);
                    setPreview(null);
                  }}
                  className="flex-1 px-6 py-3 border-2 border-gray-300 text-gray-700 font-semibold rounded-xl hover:bg-gray-50 transition"
                >
                  Change Photo
                </button>

                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handleUpload}
                  disabled={loading}
                  className={`flex-1 px-6 py-3 font-semibold rounded-xl text-white transition flex items-center justify-center gap-2 ${
                    loading
                      ? "bg-gray-400"
                      : "bg-gradient-to-r from-purple-500 to-pink-500 hover:shadow-lg"
                  }`}
                >
                  {loading ? (
                    <>
                      <Loader className="w-5 h-5 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <CheckCircle className="w-5 h-5" />
                      Analyze & Continue
                    </>
                  )}
                </motion.button>
              </div>
            </div>
          )}
        </motion.div>

        {/* Status Messages */}
        {status === "success" && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="bg-green-100 border border-green-400 text-green-700 px-6 py-4 rounded-xl flex items-center gap-3"
          >
            <CheckCircle className="w-6 h-6" />
            <div>
              <p className="font-bold">✓ Photo uploaded successfully!</p>
              <p className="text-sm">Check your sidebar for recommendations →</p>
            </div>
          </motion.div>
        )}

        {status === "error" && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="bg-red-100 border border-red-400 text-red-700 px-6 py-4 rounded-xl flex items-center gap-3"
          >
            <AlertCircle className="w-6 h-6" />
            <p className="font-bold">Please select a valid image file</p>
          </motion.div>
        )}

        {/* Tips */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mt-12 grid grid-cols-1 sm:grid-cols-3 gap-4"
        >
          {[
            { icon: "📸", title: "Full Body", desc: "Show full body in photo" },
            { icon: "💡", title: "Good Light", desc: "Natural lighting works best" },
            { icon: "😊", title: "Face Visible", desc: "Face needed for skin tone" }
          ].map((tip, i) => (
            <motion.div
              key={i}
              whileHover={{ y: -5 }}
              className="bg-white rounded-xl p-4 text-center shadow-sm border border-gray-100"
            >
              <p className="text-3xl mb-2">{tip.icon}</p>
              <p className="font-semibold text-gray-900 text-sm">{tip.title}</p>
              <p className="text-xs text-gray-600 mt-1">{tip.desc}</p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </div>
  );
}