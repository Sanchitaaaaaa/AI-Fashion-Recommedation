import { useState } from 'react';
import { HelpCircle, Mail, MessageCircle, Book, Send } from 'lucide-react';

const Support = () => {
  const [activeTab, setActiveTab] = useState('faq');
  const [message, setMessage] = useState('');
  const [email, setEmail] = useState('');

  const faqs = [
    {
      q: "How does the AI recommendation system work?",
      a: "Our AI analyzes your body measurements, skin tone, face shape, and personal preferences to suggest clothing that complements your unique features and style."
    },
    {
      q: "How accurate are the clothing recommendations?",
      a: "The system uses machine learning algorithms trained on fashion data and styling principles to provide personalized recommendations with high accuracy."
    },
    {
      q: "Can I update my body measurements later?",
      a: "Yes! You can update your measurements anytime in the Settings page under 'Profile Details'."
    },
    {
      q: "What occasions are supported?",
      a: "We provide recommendations for Casual, Formal, Party, Wedding, Sports, and Traditional occasions."
    },
    {
      q: "Is my data secure?",
      a: "Yes, all your personal data is stored locally on your device and is never shared with third parties."
    },
    {
      q: "How do I reset my preferences?",
      a: "Go to Settings > Data Management > Clear All Data to reset your preferences and start fresh."
    }
  ];

  const handleSubmit = () => {
    if (!email || !message) {
      alert('Please fill in all fields');
      return;
    }
    alert('Message sent successfully! We will get back to you soon.');
    setEmail('');
    setMessage('');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-purple-50 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-2xl shadow-lg p-8">
          <div className="flex items-center justify-between mb-8">
            <h1 className="text-3xl font-bold text-gray-800">Support & Help</h1>
            <HelpCircle className="w-8 h-8 text-indigo-600" />
          </div>

          <div className="flex gap-4 mb-8 border-b-2 border-gray-200">
            <button
              onClick={() => setActiveTab('faq')}
              className={`pb-4 px-4 font-semibold transition-colors ${
                activeTab === 'faq'
                  ? 'text-indigo-600 border-b-2 border-indigo-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <div className="flex items-center gap-2">
                <Book className="w-5 h-5" />
                FAQs
              </div>
            </button>

            <button
              onClick={() => setActiveTab('contact')}
              className={`pb-4 px-4 font-semibold transition-colors ${
                activeTab === 'contact'
                  ? 'text-indigo-600 border-b-2 border-indigo-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <div className="flex items-center gap-2">
                <MessageCircle className="w-5 h-5" />
                Contact Us
              </div>
            </button>
          </div>

          {activeTab === 'faq' && (
            <div className="space-y-4">
              {faqs.map((faq, idx) => (
                <details key={idx} className="group border-2 border-gray-200 rounded-lg p-4 hover:border-indigo-300 transition-colors">
                  <summary className="font-semibold text-gray-800 cursor-pointer list-none flex items-center justify-between">
                    <span>{faq.q}</span>
                    <span className="text-indigo-600 group-open:rotate-180 transition-transform">▼</span>
                  </summary>
                  <p className="mt-4 text-gray-600 leading-relaxed">{faq.a}</p>
                </details>
              ))}
            </div>
          )}

          {activeTab === 'contact' && (
            <div className="space-y-6">
              <div className="bg-indigo-50 rounded-xl p-6 border-2 border-indigo-100">
                <div className="flex items-start gap-4">
                  <Mail className="w-6 h-6 text-indigo-600 mt-1" />
                  <div>
                    <h3 className="font-semibold text-gray-800 mb-2">Get in Touch</h3>
                    <p className="text-gray-600">
                      Have questions or feedback? Send us a message and we'll respond within 24 hours.
                    </p>
                  </div>
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Your Email
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="your.email@example.com"
                  className="w-full p-3 border-2 border-gray-200 rounded-lg focus:border-indigo-600 focus:outline-none transition-colors"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Message
                </label>
                <textarea
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="Tell us how we can help..."
                  rows="6"
                  className="w-full p-3 border-2 border-gray-200 rounded-lg focus:border-indigo-600 focus:outline-none transition-colors resize-none"
                />
              </div>

              <button
                onClick={handleSubmit}
                className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-4 rounded-lg font-semibold hover:from-indigo-700 hover:to-purple-700 transition-all shadow-lg flex items-center justify-center gap-2"
              >
                <Send className="w-5 h-5" />
                Send Message
              </button>

              <div className="grid grid-cols-2 gap-4 mt-8">
                <div className="p-4 bg-gray-50 rounded-lg text-center">
                  <Mail className="w-8 h-8 text-indigo-600 mx-auto mb-2" />
                  <p className="text-sm font-semibold text-gray-700">Email Support</p>
                  <p className="text-xs text-gray-500 mt-1">support@fashionai.com</p>
                </div>

                <div className="p-4 bg-gray-50 rounded-lg text-center">
                  <MessageCircle className="w-8 h-8 text-indigo-600 mx-auto mb-2" />
                  <p className="text-sm font-semibold text-gray-700">Live Chat</p>
                  <p className="text-xs text-gray-500 mt-1">Mon-Fri, 9AM-6PM</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Support;