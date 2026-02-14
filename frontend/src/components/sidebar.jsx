import { X, Heart, Settings, Mail, User, LogOut, Menu } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useClerk } from "@clerk/clerk-react";

export default function Sidebar({
  isOpen,
  onClose,
}) {
  const navigate = useNavigate();
  const { signOut } = useClerk();

  const handleSignOut = async () => {
    await signOut();
    navigate("/");
  };

  const menuItems = [
    { icon: User, label: "User Details", path: "/user-details" },
    { icon: Heart, label: "Wishlist", path: "/wishlist" },
    { icon: Settings, label: "Settings", path: "/settings" },
    { icon: Mail, label: "Support", path: "/support" },
  ];

  const navigateTo = (path) => {
    navigate(path);
    onClose();
  };

  return (
    <>
      {/* Overlay */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/40 backdrop-blur-sm z-30 md:hidden"
          />
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ x: -400 }}
            animate={{ x: 0 }}
            exit={{ x: -400 }}
            transition={{ type: "spring", damping: 25, stiffness: 200 }}
            className="fixed left-0 top-0 h-full w-80 bg-white shadow-2xl z-40 flex flex-col overflow-hidden"
          >
            {/* Header */}
            <div className="p-6 border-b border-gray-100 bg-gradient-to-r from-purple-50 to-pink-50 sticky top-0">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-bold text-gray-900">Fashion AI</h2>
                  <p className="text-xs text-gray-600">Style Recommender</p>
                </div>
                <button
                  onClick={onClose}
                  className="p-2 hover:bg-gray-200 rounded-lg"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Menu Items */}
            <div className="p-4 space-y-2 border-b border-gray-100">
              {menuItems.map((item) => {
                const Icon = item.icon;
                return (
                  <motion.button
                    key={item.path}
                    whileHover={{ x: 4 }}
                    onClick={() => navigateTo(item.path)}
                    className="w-full flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-gradient-to-r hover:from-purple-50 hover:to-pink-50 transition-all group"
                  >
                    <Icon className="w-5 h-5 text-gray-400 group-hover:text-purple-600 transition-colors flex-shrink-0" />
                    <span className="text-sm text-gray-700 group-hover:text-gray-900 font-medium">
                      {item.label}
                    </span>
                  </motion.button>
                );
              })}
            </div>

            {/* Spacer */}
            <div className="flex-1" />

            {/* Sign Out Button */}
            <div className="border-t border-gray-100 p-4 bg-gray-50">
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={handleSignOut}
                className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-white border-2 border-gray-200 text-gray-700 font-semibold rounded-lg hover:border-red-300 hover:text-red-600 hover:bg-red-50 transition-all text-sm"
              >
                <LogOut className="w-4 h-4" />
                Sign Out
              </motion.button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}