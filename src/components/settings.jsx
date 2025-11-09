import { useState } from 'react';
import { Moon, Sun, User, LogOut, Edit3, Trash2, Cog } from 'lucide-react';

const Settings = () => {
  const [theme, setTheme] = useState('light');
  const [showEditModal, setShowEditModal] = useState(false);
  const [editType, setEditType] = useState('');

  const faceDetails = JSON.parse(localStorage.getItem('faceDetails') || '{}');
  const bodyDetails = JSON.parse(localStorage.getItem('bodyDetails') || '{}');

  const [editFaceData, setEditFaceData] = useState({
    skinTone: faceDetails.skinTone || '',
    faceShape: faceDetails.faceShape || '',
    eyeColor: faceDetails.eyeColor || ''
  });

  const [editBodyData, setEditBodyData] = useState({
    height: bodyDetails.height || '',
    weight: bodyDetails.weight || '',
    bodyShape: bodyDetails.bodyShape || ''
  });

  const handleThemeToggle = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    document.body.classList.toggle('dark');
  };

  const openEditModal = (type) => {
    setEditType(type);
    setShowEditModal(true);
  };

  const saveEdit = () => {
    if (editType === 'face') {
      localStorage.setItem('faceDetails', JSON.stringify({...faceDetails, ...editFaceData}));
    } else if (editType === 'body') {
      localStorage.setItem('bodyDetails', JSON.stringify({...bodyDetails, ...editBodyData}));
    }
    setShowEditModal(false);
    alert('Details updated successfully!');
  };

  const clearData = () => {
    if (confirm('Are you sure you want to clear all saved data?')) {
      localStorage.removeItem('faceDetails');
      localStorage.removeItem('bodyDetails');
      alert('All data cleared successfully!');
    }
  };

  const handleLogout = () => {
    if (confirm('Are you sure you want to logout?')) {
      localStorage.clear();
      alert('Logged out successfully!');
    }
  };

  const skinTones = ['Fair', 'Light', 'Medium', 'Olive', 'Tan', 'Brown', 'Dark'];
  const faceShapes = ['Oval', 'Round', 'Square', 'Heart', 'Diamond', 'Long'];
  const eyeColors = ['Brown', 'Blue', 'Green', 'Hazel', 'Gray', 'Amber'];
  const bodyShapes = ['Rectangle', 'Triangle', 'Inverted Triangle', 'Hourglass', 'Round'];

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-teal-50 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-2xl shadow-lg p-8">
          <div className="flex items-center justify-between mb-8">
            <h1 className="text-3xl font-bold text-gray-800">Settings</h1>
            <Cog className="w-8 h-8 text-teal-600" />
          </div>

          <div className="space-y-6">
            <div className="border-2 border-gray-200 rounded-xl p-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">Appearance</h2>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  {theme === 'light' ? <Sun className="w-6 h-6" /> : <Moon className="w-6 h-6" />}
                  <div>
                    <p className="font-medium text-gray-700">Theme</p>
                    <p className="text-sm text-gray-500">Switch between light and dark mode</p>
                  </div>
                </div>
                <button
                  onClick={handleThemeToggle}
                  className={`relative w-14 h-8 rounded-full transition-colors ${
                    theme === 'dark' ? 'bg-teal-600' : 'bg-gray-300'
                  }`}
                >
                  <div className={`absolute top-1 left-1 w-6 h-6 rounded-full bg-white transition-transform ${
                    theme === 'dark' ? 'transform translate-x-6' : ''
                  }`} />
                </button>
              </div>
            </div>

            <div className="border-2 border-gray-200 rounded-xl p-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">Profile Details</h2>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-700">Face Details</p>
                    <p className="text-sm text-gray-500 mt-1">
                      Skin Tone: {faceDetails.skinTone || 'Not set'} | 
                      Face Shape: {faceDetails.faceShape || 'Not set'}
                    </p>
                  </div>
                  <button
                    onClick={() => openEditModal('face')}
                    className="p-2 text-teal-600 hover:bg-teal-50 rounded-lg transition-colors"
                  >
                    <Edit3 className="w-5 h-5" />
                  </button>
                </div>

                <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-700">Body Details</p>
                    <p className="text-sm text-gray-500 mt-1">
                      Height: {bodyDetails.height || 'Not set'} cm | 
                      Weight: {bodyDetails.weight || 'Not set'} kg
                    </p>
                  </div>
                  <button
                    onClick={() => openEditModal('body')}
                    className="p-2 text-teal-600 hover:bg-teal-50 rounded-lg transition-colors"
                  >
                    <Edit3 className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>

            <div className="border-2 border-gray-200 rounded-xl p-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">Data Management</h2>
              
              <button
                onClick={clearData}
                className="w-full flex items-center justify-center gap-3 p-4 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-colors"
              >
                <Trash2 className="w-5 h-5" />
                Clear All Data
              </button>
            </div>

            <div className="border-2 border-gray-200 rounded-xl p-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">Account</h2>
              
              <button
                onClick={handleLogout}
                className="w-full flex items-center justify-center gap-3 p-4 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
              >
                <LogOut className="w-5 h-5" />
                Logout
              </button>
            </div>
          </div>
        </div>

        {showEditModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-2xl p-6 max-w-md w-full">
              <h3 className="text-2xl font-bold text-gray-800 mb-4">
                Edit {editType === 'face' ? 'Face' : 'Body'} Details
              </h3>

              {editType === 'face' && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">Skin Tone</label>
                    <select
                      value={editFaceData.skinTone}
                      onChange={(e) => setEditFaceData({...editFaceData, skinTone: e.target.value})}
                      className="w-full p-3 border-2 border-gray-200 rounded-lg focus:border-teal-600 focus:outline-none"
                    >
                      <option value="">Select</option>
                      {skinTones.map(tone => <option key={tone} value={tone}>{tone}</option>)}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">Face Shape</label>
                    <select
                      value={editFaceData.faceShape}
                      onChange={(e) => setEditFaceData({...editFaceData, faceShape: e.target.value})}
                      className="w-full p-3 border-2 border-gray-200 rounded-lg focus:border-teal-600 focus:outline-none"
                    >
                      <option value="">Select</option>
                      {faceShapes.map(shape => <option key={shape} value={shape}>{shape}</option>)}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">Eye Color</label>
                    <select
                      value={editFaceData.eyeColor}
                      onChange={(e) => setEditFaceData({...editFaceData, eyeColor: e.target.value})}
                      className="w-full p-3 border-2 border-gray-200 rounded-lg focus:border-teal-600 focus:outline-none"
                    >
                      <option value="">Select</option>
                      {eyeColors.map(color => <option key={color} value={color}>{color}</option>)}
                    </select>
                  </div>
                </div>
              )}

              {editType === 'body' && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">Height (cm)</label>
                    <input
                      type="number"
                      value={editBodyData.height}
                      onChange={(e) => setEditBodyData({...editBodyData, height: e.target.value})}
                      className="w-full p-3 border-2 border-gray-200 rounded-lg focus:border-teal-600 focus:outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">Weight (kg)</label>
                    <input
                      type="number"
                      value={editBodyData.weight}
                      onChange={(e) => setEditBodyData({...editBodyData, weight: e.target.value})}
                      className="w-full p-3 border-2 border-gray-200 rounded-lg focus:border-teal-600 focus:outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">Body Shape</label>
                    <select
                      value={editBodyData.bodyShape}
                      onChange={(e) => setEditBodyData({...editBodyData, bodyShape: e.target.value})}
                      className="w-full p-3 border-2 border-gray-200 rounded-lg focus:border-teal-600 focus:outline-none"
                    >
                      <option value="">Select</option>
                      {bodyShapes.map(shape => <option key={shape} value={shape}>{shape}</option>)}
                    </select>
                  </div>
                </div>
              )}

              <div className="flex gap-3 mt-6">
                <button
                  onClick={() => setShowEditModal(false)}
                  className="flex-1 px-4 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
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