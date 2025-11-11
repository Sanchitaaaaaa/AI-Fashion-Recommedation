import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { User, ArrowRight, ArrowLeft } from 'lucide-react';

const BodyDetails = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    height: '',
    weight: '',
    bodyShape: '',
    shoulderWidth: '',
    waistSize: '',
    hipSize: '',
    preferredFit: ''
  });

  const bodyShapes = ['Rectangle', 'Triangle', 'Inverted Triangle', 'Hourglass', 'Round'];
  const shoulderWidths = ['Narrow', 'Average', 'Broad'];
  const fitPreferences = ['Tight Fit', 'Regular Fit', 'Loose Fit', 'Oversized'];

  const handleSubmit = () => {
    if (!formData.height || !formData.weight || !formData.bodyShape) {
      alert('Please fill in all required fields');
      return;
    }
    localStorage.setItem('bodyDetails', JSON.stringify(formData));
    alert('Body details saved successfully!');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 p-6">
      <div className="max-w-3xl mx-auto">
        {/* Back Button */}
        <button
          onClick={() => navigate('/home')}
          className="mb-4 flex items-center gap-2 text-gray-600 hover:text-blue-600 transition-colors group"
        >
          <ArrowLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
          <span className="font-medium">Back to Home</span>
        </button>

        <div className="bg-white rounded-2xl shadow-lg p-8">
          <div className="flex items-center justify-between mb-8">
            <h1 className="text-3xl font-bold text-gray-800">Body Details</h1>
            <User className="w-8 h-8 text-blue-600" />
          </div>

          <div className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Height (cm) *
                </label>
                <input
                  type="number"
                  value={formData.height}
                  onChange={(e) => setFormData({...formData, height: e.target.value})}
                  placeholder="e.g., 170"
                  className="w-full p-3 border-2 border-gray-200 rounded-lg focus:border-blue-600 focus:outline-none transition-colors"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Weight (kg) *
                </label>
                <input
                  type="number"
                  value={formData.weight}
                  onChange={(e) => setFormData({...formData, weight: e.target.value})}
                  placeholder="e.g., 65"
                  className="w-full p-3 border-2 border-gray-200 rounded-lg focus:border-blue-600 focus:outline-none transition-colors"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                Body Shape *
              </label>
              <div className="grid grid-cols-3 gap-3">
                {bodyShapes.map(shape => (
                  <button
                    key={shape}
                    onClick={() => setFormData({...formData, bodyShape: shape})}
                    className={`p-3 rounded-lg border-2 transition-all ${
                      formData.bodyShape === shape
                        ? 'border-blue-600 bg-blue-50 text-blue-700'
                        : 'border-gray-200 hover:border-blue-300'
                    }`}
                  >
                    {shape}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                Shoulder Width
              </label>
              <div className="grid grid-cols-3 gap-3">
                {shoulderWidths.map(width => (
                  <button
                    key={width}
                    onClick={() => setFormData({...formData, shoulderWidth: width})}
                    className={`p-3 rounded-lg border-2 transition-all ${
                      formData.shoulderWidth === width
                        ? 'border-blue-600 bg-blue-50 text-blue-700'
                        : 'border-gray-200 hover:border-blue-300'
                    }`}
                  >
                    {width}
                  </button>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Waist Size (inches)
                </label>
                <input
                  type="number"
                  value={formData.waistSize}
                  onChange={(e) => setFormData({...formData, waistSize: e.target.value})}
                  placeholder="e.g., 32"
                  className="w-full p-3 border-2 border-gray-200 rounded-lg focus:border-blue-600 focus:outline-none transition-colors"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Hip Size (inches)
                </label>
                <input
                  type="number"
                  value={formData.hipSize}
                  onChange={(e) => setFormData({...formData, hipSize: e.target.value})}
                  placeholder="e.g., 36"
                  className="w-full p-3 border-2 border-gray-200 rounded-lg focus:border-blue-600 focus:outline-none transition-colors"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                Preferred Fit
              </label>
              <div className="grid grid-cols-2 gap-3">
                {fitPreferences.map(fit => (
                  <button
                    key={fit}
                    onClick={() => setFormData({...formData, preferredFit: fit})}
                    className={`p-3 rounded-lg border-2 transition-all ${
                      formData.preferredFit === fit
                        ? 'border-blue-600 bg-blue-50 text-blue-700'
                        : 'border-gray-200 hover:border-blue-300'
                    }`}
                  >
                    {fit}
                  </button>
                ))}
              </div>
            </div>

            <button
              onClick={handleSubmit}
              className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-4 rounded-lg font-semibold hover:from-blue-700 hover:to-indigo-700 transition-all shadow-lg flex items-center justify-center gap-2"
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

export default BodyDetails;