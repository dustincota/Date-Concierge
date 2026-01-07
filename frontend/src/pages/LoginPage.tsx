import { useState } from 'react';
import { useAuthStore } from '../stores/authStore';
import { Heart } from 'lucide-react';

export default function LoginPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');

  const { login, register, error, isLoading, clearError } = useAuthStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();

    if (isLogin) {
      await login(email, password);
    } else {
      await register(email, password, name);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 via-white to-purple-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        {/* Logo/Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-600 rounded-full mb-4">
            <Heart className="w-8 h-8 text-white" fill="white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900">Date Concierge</h1>
          <p className="text-gray-600 mt-2">Collaborative date planning made perfect</p>
        </div>

        {/* Form Card */}
        <div className="card">
          <h2 className="text-2xl font-bold mb-6 text-center">
            {isLogin ? 'Welcome Back' : 'Get Started'}
          </h2>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {!isLogin && (
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
                  Name
                </label>
                <input
                  type="text"
                  id="name"
                  className="input"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Your name"
                />
              </div>
            )}

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                Email
              </label>
              <input
                type="email"
                id="email"
                className="input"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="you@example.com"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                Password
              </label>
              <input
                type="password"
                id="password"
                className="input"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                placeholder="••••••••"
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="btn btn-primary w-full"
            >
              {isLoading ? 'Please wait...' : isLogin ? 'Sign In' : 'Create Account'}
            </button>
          </form>

          <div className="mt-6 text-center">
            <button
              onClick={() => {
                setIsLogin(!isLogin);
                clearError();
              }}
              className="text-primary-600 hover:text-primary-700 text-sm font-medium"
            >
              {isLogin ? "Don't have an account? Sign up" : 'Already have an account? Sign in'}
            </button>
          </div>
        </div>

        {/* Features */}
        <div className="mt-8 text-center text-sm text-gray-600">
          <p>✨ Collaborative planning • 🧠 AI venue intelligence • 📍 Smart location matching</p>
        </div>
      </div>
    </div>
  );
}
