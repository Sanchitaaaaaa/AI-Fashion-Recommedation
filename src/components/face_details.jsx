import { useState } from 'react';
import { Camera, Check, ArrowRight } from 'lucide-react';

const FaceDetails = () => {
  const [formData, setFormData] = useState({
    skinTone: '',
    faceShape: '',
    eyeColor: '',
    hairColor: '',
    hairType: '',
    preferences: []
  });

  const skinTones = ['Fair', 'Light', 'Medium', 'Olive', 'Tan', 'Brown', 'Dark'];
  const faceShapes = ['Oval', 'Round', 'Square', 'Heart', 'Diamond', 'Long'];
  const eyeColors = ['Brown', 'Blue', 'Green', 'Hazel', 'Gray', 'Amber'];
  const hairColors = ['Black', 'Brown', 'Blonde', 'Red', 'Gray', 'White', 'Other'];
  const hairTypes = ['Straight', 'Wavy', 'Curly', 'Coily'];
  const colorPreferences = ['Bright Colors', 'Pastels', 'Neutrals', 'Dark Tones', 'Earth Tones'];

  const handleSubmit = () => {
    if (!formData.skinTone || !formData.faceShape || !formData.eyeColor || !formData.hairColor || !formData.hairType) {
      alert('Please fill in all required fields');
      return;
    }
    localStorage.setItem('faceDetails', JSON.stringify(formData));
    alert('Face details saved successfully!');
  };

  const togglePreference = (pref) => {
    setFormData(prev => ({
      ...prev,
      preferences: prev.preferences.includes(pref)
        ? prev.preferences.filter(p => p !== pref)
        : [...prev.preferences, pref]
    }));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 p-6">
      <div className="max-w-3xl mx-auto">
        <div className="bg-white rounded-2xl shadow-lg p-8">
          <div className="flex items-center justify-between mb-8">
            <h1 className="text-3xl font-bold text-gray-800">Face Details</h1>
            <Camera className="w-8 h-8 text-purple-600" />
          </div>

          <div className="space-y-6">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                Skin Tone *
              </label>
              <div className="grid grid-cols-4 gap-3">
                {skinTones.map(tone => (
                  <button
                    key={tone}
                    type="button"
                    onClick={() => setFormData({...formData, skinTone: tone})}
                    className={`p-3 rounded-lg border-2 transition-all ${
                      formData.skinTone === tone
                        ? 'border-purple-600 bg-purple-50 text-purple-700'
                        : 'border-gray-200 hover:border-purple-300'
                    }`}
                  >
                    {tone}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                Face Shape *
              </label>
              <div className="grid grid-cols-3 gap-3">
                {faceShapes.map(shape => (
                  <button
                    key={shape}
                    type="button"
                    onClick={() => setFormData({...formData, faceShape: shape})}
                    className={`p-3 rounded-lg border-2 transition-all ${
                      formData.faceShape === shape
                        ? 'border-purple-600 bg-purple-50 text-purple-700'
                        : 'border-gray-200 hover:border-purple-300'
                    }`}
                  >
                    {shape}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                Eye Color *
              </label>
              <div className="grid grid-cols-3 gap-3">
                {eyeColors.map(color => (
                  <button
                    key={color}
                    type="button"
                    onClick={() => setFormData({...formData, eyeColor: color})}
                    className={`p-3 rounded-lg border-2 transition-all ${
                      formData.eyeColor === color
                        ? 'border-purple-600 bg-purple-50 text-purple-700'
                        : 'border-gray-200 hover:border-purple-300'
                    }`}
                  >
                    {color}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                Hair Color *
              </label>
              <div className="grid grid-cols-4 gap-3">
                {hairColors.map(color => (
                  <button
                    key={color}
                    type="button"
                    onClick={() => setFormData({...formData, hairColor: color})}
                    className={`p-3 rounded-lg border-2 transition-all ${
                      formData.hairColor === color
                        ? 'border-purple-600 bg-purple-50 text-purple-700'
                        : 'border-gray-200 hover:border-purple-300'
                    }`}
                  >
                    {color}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                Hair Type *
              </label>
              <div className="grid grid-cols-2 gap-3">
                {hairTypes.map(type => (
                  <button
                    key={type}
                    type="button"
                    onClick={() => setFormData({...formData, hairType: type})}
                    className={`p-3 rounded-lg border-2 transition-all ${
                      formData.hairType === type
                        ? 'border-purple-600 bg-purple-50 text-purple-700'
                        : 'border-gray-200 hover:border-purple-300'
                    }`}
                  >
                    {type}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                Color Preferences (Select Multiple)
              </label>
              <div className="grid grid-cols-2 gap-3">
                {colorPreferences.map(pref => (
                  <button
                    key={pref}
                    type="button"
                    onClick={() => togglePreference(pref)}
                    className={`p-3 rounded-lg border-2 transition-all flex items-center justify-between ${
                      formData.preferences.includes(pref)
                        ? 'border-purple-600 bg-purple-50 text-purple-700'
                        : 'border-gray-200 hover:border-purple-300'
                    }`}
                  >
                    <span>{pref}</span>
                    {formData.preferences.includes(pref) && (
                      <Check className="w-5 h-5" />
                    )}
                  </button>
                ))}
              </div>
            </div>

            <button
              onClick={handleSubmit}
              className="w-full bg-gradient-to-r from-purple-600 to-blue-600 text-white py-4 rounded-lg font-semibold hover:from-purple-700 hover:to-blue-700 transition-all shadow-lg flex items-center justify-center gap-2"
            >
              Save & Continue
              <ArrowRight className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FaceDetails;