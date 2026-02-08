import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, ShoppingBag, ArrowLeft } from 'lucide-react';

const Preferences = () => {
   const navigate = useNavigate();
  const [selectedOccasion, setSelectedOccasion] = useState('');
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);

  const occasions = [
    { id: 'casual', name: 'Casual', icon: '👕', desc: 'Everyday wear' },
    { id: 'formal', name: 'Formal', icon: '👔', desc: 'Business & meetings' },
    { id: 'party', name: 'Party', icon: '🎉', desc: 'Evening events' },
    { id: 'wedding', name: 'Wedding', icon: '💒', desc: 'Special ceremonies' },
    { id: 'sports', name: 'Sports', icon: '⚽', desc: 'Athletic activities' },
    { id: 'traditional', name: 'Traditional', icon: '🎨', desc: 'Cultural attire' }
  ];

  const generateRecommendations = (occasion) => {
    setLoading(true);
    setSelectedOccasion(occasion);

    const faceDetails = JSON.parse(localStorage.getItem('faceDetails') || '{}');
    const bodyDetails = JSON.parse(localStorage.getItem('bodyDetails') || '{}');

    setTimeout(() => {
      const recs = {
        casual: [
          { item: 'Cotton T-Shirt', color: 'Based on your skin tone', fit: bodyDetails.preferredFit || 'Regular' },
          { item: 'Denim Jeans', color: 'Dark wash recommended', fit: 'Straight fit' },
          { item: 'Casual Sneakers', color: 'White or neutral', fit: 'Comfortable' }
        ],
        formal: [
          { item: 'Formal Shirt', color: faceDetails.skinTone === 'Fair' ? 'Light blue' : 'White', fit: 'Slim fit' },
          { item: 'Dress Pants', color: 'Navy or charcoal', fit: bodyDetails.preferredFit || 'Regular' },
          { item: 'Leather Shoes', color: 'Brown or black', fit: 'Classic' }
        ],
        party: [
          { item: 'Blazer', color: 'Bold colors recommended', fit: 'Fitted' },
          { item: 'Dress Shirt', color: 'Complementary to blazer', fit: 'Slim' },
          { item: 'Chinos', color: 'Neutral tones', fit: 'Modern fit' }
        ],
        wedding: [
          { item: 'Suit', color: 'Navy, grey, or beige', fit: 'Tailored' },
          { item: 'Dress Shirt', color: 'White or pastels', fit: 'Classic' },
          { item: 'Tie & Pocket Square', color: 'Coordinated colors', fit: 'Elegant' }
        ],
        sports: [
          { item: 'Performance T-Shirt', color: 'Moisture-wicking fabric', fit: 'Athletic' },
          { item: 'Track Pants', color: 'Dark colors', fit: 'Comfortable' },
          { item: 'Running Shoes', color: 'Bright accents', fit: 'Supportive' }
        ],
        traditional: [
          { item: 'Kurta', color: 'Based on complexion', fit: 'Traditional' },
          { item: 'Pajama/Churidar', color: 'Matching or contrasting', fit: 'Comfortable' },
          { item: 'Traditional Footwear', color: 'Coordinated', fit: 'Classic' }
        ]
      };

      setRecommendations(recs[occasion] || []);
      setLoading(false);
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 to-orange-50 p-6">
      <div className="max-w-5xl mx-auto">
         <button
          onClick={() => navigate('/home')}
          className="mb-4 flex items-center gap-2 text-gray-600 hover:text-blue-600 transition-colors group"
        >
          <ArrowLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
          <span className="font-medium">Back to Home</span>
        </button>
        <div className="bg-white rounded-2xl shadow-lg p-8">
          <div className="flex items-center justify-between mb-8">
            <h1 className="text-3xl font-bold text-gray-800">Outfit Preferences</h1>
            <Sparkles className="w-8 h-8 text-orange-600" />
          </div>

          <div className="mb-8">
            <h2 className="text-lg font-semibold text-gray-700 mb-4">Select an Occasion</h2>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {occasions.map(occasion => (
                <button
                  key={occasion.id}
                  onClick={() => generateRecommendations(occasion.id)}
                  className={`p-6 rounded-xl border-2 transition-all hover:shadow-md ${
                    selectedOccasion === occasion.id
                      ? 'border-orange-600 bg-orange-50'
                      : 'border-gray-200 hover:border-orange-300'
                  }`}
                >
                  <div className="text-4xl mb-2">{occasion.icon}</div>
                  <div className="font-semibold text-gray-800">{occasion.name}</div>
                  <div className="text-sm text-gray-500 mt-1">{occasion.desc}</div>
                </button>
              ))}
            </div>
          </div>

          {loading && (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-orange-600 border-t-transparent"></div>
              <p className="mt-4 text-gray-600">Generating personalized recommendations...</p>
            </div>
          )}

          {!loading && recommendations.length > 0 && (
            <div className="bg-gradient-to-br from-orange-50 to-pink-50 rounded-xl p-6">
              <div className="flex items-center gap-2 mb-6">
                <ShoppingBag className="w-6 h-6 text-orange-600" />
                <h2 className="text-xl font-bold text-gray-800">Recommended for {occasions.find(o => o.id === selectedOccasion)?.name}</h2>
              </div>

              <div className="space-y-4">
                {recommendations.map((rec, idx) => (
                  <div key={idx} className="bg-white rounded-lg p-4 shadow-sm border-2 border-orange-100">
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="font-semibold text-gray-800 text-lg">{rec.item}</h3>
                        <p className="text-gray-600 mt-1">Color: {rec.color}</p>
                        <p className="text-gray-600">Fit: {rec.fit}</p>
                      </div>
                      <button className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors text-sm">
                        View More
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Preferences;