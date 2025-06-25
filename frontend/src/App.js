import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL;

function App() {
  const [apiStatus, setApiStatus] = useState('checking');
  const [showChat, setShowChat] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [chatMessage, setChatMessage] = useState('');
  const [chatResponse, setChatResponse] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    checkApiConnection();
    // Check if user is logged in
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');
    if (token && userData) {
      setIsAuthenticated(true);
      setUser(JSON.parse(userData));
    }
  }, []);

  const checkApiConnection = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/`);
      if (response.status === 200) {
        setApiStatus('connected');
      }
    } catch (error) {
      console.error('API connection failed:', error);
      setApiStatus('failed');
    }
  };

  const handleGetStarted = () => {
    if (isAuthenticated) {
      setShowChat(true);
    } else {
      // For demo purposes, let's create a demo user
      createDemoUser();
    }
  };

  const createDemoUser = async () => {
    try {
      setIsLoading(true);
      const demoUser = {
        email: `demo${Date.now()}@nutracia.com`,
        password: 'demo123',
        name: 'Demo User',
        age: 30,
        health_goals: ['Weight Management', 'Better Nutrition', 'Fitness Improvement']
      };

      const response = await axios.post(`${API_BASE_URL}/api/signup`, demoUser);
      
      if (response.data.access_token) {
        localStorage.setItem('token', response.data.access_token);
        localStorage.setItem('user', JSON.stringify({
          id: response.data.user_id,
          ...demoUser
        }));
        setIsAuthenticated(true);
        setUser({ id: response.data.user_id, ...demoUser });
        setShowChat(true);
      }
    } catch (error) {
      console.error('Demo user creation failed:', error);
      alert('Failed to create demo user. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleChatSubmit = async (e) => {
    e.preventDefault();
    if (!chatMessage.trim() || !user) return;

    try {
      setIsLoading(true);
      const token = localStorage.getItem('token');
      
      const response = await axios.post(
        `${API_BASE_URL}/api/chat/ai`,
        {
          message: chatMessage,
          user_id: user.id
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      setChatResponse(response.data.response);
      setChatMessage('');
    } catch (error) {
      console.error('Chat failed:', error);
      setChatResponse('Sorry, I encountered an error. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-soft-white">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-medical-blue rounded-full flex items-center justify-center">
                <span className="text-white font-bold text-lg">N</span>
              </div>
              <h1 className="text-2xl font-poppins font-bold text-medical-blue">Nutracía</h1>
            </div>
            <div className="flex items-center space-x-4">
              <div className={`px-3 py-1 rounded-full text-sm ${
                apiStatus === 'connected' 
                  ? 'bg-medical-green text-white' 
                  : apiStatus === 'failed' 
                  ? 'bg-red-500 text-white' 
                  : 'bg-gray-300 text-gray-700'
              }`}>
                {apiStatus === 'connected' ? '● Online' : apiStatus === 'failed' ? '● Offline' : '● Checking...'}
              </div>
              {isAuthenticated && (
                <span className="text-medical-blue font-medium">Welcome, {user?.name}</span>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      {!showChat ? (
        // Hero Section
        <main className="medical-gradient">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="py-20 lg:py-32">
              <div className="grid lg:grid-cols-2 gap-12 items-center">
                {/* Left Column - Content */}
                <div className="space-y-8 animate-fade-in">
                  <div className="space-y-4">
                    <h1 className="text-5xl lg:text-6xl font-poppins font-bold text-medical-blue leading-tight">
                      Nutracía
                      <span className="block text-medical-accent">Your Intelligent</span>
                      <span className="block text-medical-green">Wellness Companion</span>
                    </h1>
                    <p className="text-xl lg:text-2xl text-gray-600 font-inter max-w-lg">
                      Nutrition, Skincare & Fitness — Tailored by AI, Backed by Science
                    </p>
                  </div>

                  <div className="space-y-6">
                    <div className="flex items-center space-x-4">
                      <div className="w-6 h-6 bg-medical-green rounded-full flex items-center justify-center">
                        <span className="text-white text-sm">✓</span>
                      </div>
                      <span className="text-lg text-medical-blue">Medical-grade AI guidance</span>
                    </div>
                    <div className="flex items-center space-x-4">
                      <div className="w-6 h-6 bg-medical-green rounded-full flex items-center justify-center">
                        <span className="text-white text-sm">✓</span>
                      </div>
                      <span className="text-lg text-medical-blue">Personalized wellness plans</span>
                    </div>
                    <div className="flex items-center space-x-4">
                      <div className="w-6 h-6 bg-medical-green rounded-full flex items-center justify-center">
                        <span className="text-white text-sm">✓</span>
                      </div>
                      <span className="text-lg text-medical-blue">Evidence-based recommendations</span>
                    </div>
                  </div>

                  <div className="pt-8">
                    <button 
                      onClick={handleGetStarted}
                      disabled={isLoading || apiStatus !== 'connected'}
                      className="btn-glow bg-medical-green hover:bg-green-600 text-white px-8 py-4 rounded-lg text-lg font-semibold shadow-lg transform transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {isLoading ? 'Loading...' : 'Get Started'}
                    </button>
                    <p className="text-sm text-gray-500 mt-2">Start your wellness journey today</p>
                  </div>
                </div>

                {/* Right Column - Hero Image */}
                <div className="relative animate-slide-up">
                  <div className="relative rounded-2xl overflow-hidden shadow-2xl">
                    <img 
                      src="https://images.unsplash.com/photo-1576091160399-112ba8d25d1d" 
                      alt="Healthcare Professional with Technology"
                      className="w-full h-96 lg:h-[500px] object-cover"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-medical-blue/20 to-transparent"></div>
                    
                    {/* Floating Cards */}
                    <div className="absolute top-4 right-4 bg-white/90 backdrop-blur-sm rounded-lg p-4 shadow-lg floating-element">
                      <div className="flex items-center space-x-2">
                        <div className="w-3 h-3 bg-medical-green rounded-full animate-pulse"></div>
                        <span className="text-sm font-medium text-medical-blue">AI Active</span>
                      </div>
                    </div>
                    
                    <div className="absolute bottom-4 left-4 bg-white/90 backdrop-blur-sm rounded-lg p-4 shadow-lg floating-element" style={{animationDelay: '2s'}}>
                      <div className="text-sm text-medical-blue">
                        <div className="font-semibold">Health Score</div>
                        <div className="text-medical-green font-bold">95/100</div>
                      </div>
                    </div>
                  </div>

                  {/* Background Decorative Elements */}
                  <div className="absolute -top-4 -right-4 w-24 h-24 bg-medical-green/10 rounded-full blur-xl"></div>
                  <div className="absolute -bottom-4 -left-4 w-32 h-32 bg-medical-blue/10 rounded-full blur-xl"></div>
                </div>
              </div>
            </div>
          </div>

          {/* Features Section */}
          <div className="bg-white py-20">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="text-center mb-16">
                <h2 className="text-4xl font-poppins font-bold text-medical-blue mb-4">
                  Powered by Advanced AI
                </h2>
                <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                  Our intelligent system provides personalized recommendations across nutrition, skincare, and fitness
                </p>
              </div>

              <div className="grid md:grid-cols-3 gap-8">
                <div className="text-center p-8 rounded-xl bg-medical-gray/30 hover:shadow-lg transition-all duration-300">
                  <div className="w-16 h-16 bg-medical-green rounded-full flex items-center justify-center mx-auto mb-6">
                    <span className="text-white text-2xl">🥗</span>
                  </div>
                  <h3 className="text-xl font-semibold text-medical-blue mb-4">Smart Nutrition</h3>
                  <p className="text-gray-600">Personalized meal plans and nutritional guidance based on your health goals and dietary preferences.</p>
                </div>

                <div className="text-center p-8 rounded-xl bg-medical-gray/30 hover:shadow-lg transition-all duration-300">
                  <div className="w-16 h-16 bg-medical-blue rounded-full flex items-center justify-center mx-auto mb-6">
                    <span className="text-white text-2xl">💪</span>
                  </div>
                  <h3 className="text-xl font-semibold text-medical-blue mb-4">Fitness Coaching</h3>
                  <p className="text-gray-600">AI-powered workout recommendations tailored to your fitness level and available time.</p>
                </div>

                <div className="text-center p-8 rounded-xl bg-medical-gray/30 hover:shadow-lg transition-all duration-300">
                  <div className="w-16 h-16 bg-medical-accent rounded-full flex items-center justify-center mx-auto mb-6">
                    <span className="text-white text-2xl">✨</span>
                  </div>
                  <h3 className="text-xl font-semibold text-medical-blue mb-4">Skincare Analysis</h3>
                  <p className="text-gray-600">Evidence-based skincare routines and product recommendations for your skin type.</p>
                </div>
              </div>
            </div>
          </div>
        </main>
      ) : (
        // Chat Interface
        <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="bg-white rounded-2xl shadow-lg p-8">
            <div className="mb-8">
              <h2 className="text-3xl font-poppins font-bold text-medical-blue mb-2">
                Chat with Nutracía AI
              </h2>
              <p className="text-gray-600">Ask me anything about nutrition, fitness, or skincare!</p>
            </div>

            <form onSubmit={handleChatSubmit} className="space-y-6">
              <div>
                <label htmlFor="chat-message" className="block text-sm font-medium text-medical-blue mb-2">
                  Your Question
                </label>
                <textarea
                  id="chat-message"
                  value={chatMessage}
                  onChange={(e) => setChatMessage(e.target.value)}
                  rows={4}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-medical-green focus:border-transparent resize-none"
                  placeholder="e.g., What should I eat for breakfast to boost my energy?"
                  disabled={isLoading}
                />
              </div>

              <button
                type="submit"
                disabled={isLoading || !chatMessage.trim()}
                className="btn-glow bg-medical-green hover:bg-green-600 text-white px-6 py-3 rounded-lg font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? 'Thinking...' : 'Ask Nutracía'}
              </button>
            </form>

            {chatResponse && (
              <div className="mt-8 p-6 bg-medical-gray/30 rounded-lg">
                <h3 className="font-semibold text-medical-blue mb-3">Nutracía's Response:</h3>
                <div className="text-gray-700 whitespace-pre-wrap leading-relaxed">
                  {chatResponse}
                </div>
              </div>
            )}

            <button
              onClick={() => setShowChat(false)}
              className="mt-6 text-medical-blue hover:text-medical-accent underline"
            >
              ← Back to Home
            </button>
          </div>
        </main>
      )}

      {/* Footer */}
      <footer className="bg-medical-blue text-white py-12 mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="flex items-center justify-center space-x-3 mb-4">
              <div className="w-8 h-8 bg-medical-green rounded-full flex items-center justify-center">
                <span className="text-white font-bold">N</span>
              </div>
              <h3 className="text-2xl font-poppins font-bold">Nutracía</h3>
            </div>
            <p className="text-blue-200 mb-6">Your Intelligent Wellness Companion</p>
            <p className="text-sm text-blue-300">
              © 2025 Nutracía. Powered by AI, backed by science.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;