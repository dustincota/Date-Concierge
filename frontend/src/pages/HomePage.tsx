import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { sessionAPI } from '../utils/api';
import { Heart, Plus, LogOut, Users } from 'lucide-react';

export default function HomePage() {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showJoinModal, setShowJoinModal] = useState(false);
  const [sessionName, setSessionName] = useState('');
  const [inviteCode, setInviteCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleCreateSession = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const session = await sessionAPI.createSession(sessionName);
      navigate(`/session/${session.id}`);
    } catch (error) {
      console.error('Failed to create session:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleJoinSession = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const session = await sessionAPI.joinSession(inviteCode);
      navigate(`/session/${session.id}`);
    } catch (error) {
      console.error('Failed to join session:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <Heart className="w-8 h-8 text-primary-600" fill="currentColor" />
            <h1 className="text-2xl font-bold text-gray-900">Date Concierge</h1>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-gray-600">Hi, {user?.name || user?.email}</span>
            <button onClick={logout} className="btn btn-outline flex items-center gap-2">
              <LogOut className="w-4 h-4" />
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Plan the Perfect Date Together
          </h2>
          <p className="text-xl text-gray-600">
            Collaborate with your partner to discover amazing venues with deep intelligence
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {/* Create Session Card */}
          <div className="card hover:shadow-lg transition-shadow cursor-pointer" onClick={() => setShowCreateModal(true)}>
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-100 rounded-full mb-4">
                <Plus className="w-8 h-8 text-primary-600" />
              </div>
              <h3 className="text-xl font-bold mb-2">Create New Session</h3>
              <p className="text-gray-600">
                Start planning and invite your partner
              </p>
            </div>
          </div>

          {/* Join Session Card */}
          <div className="card hover:shadow-lg transition-shadow cursor-pointer" onClick={() => setShowJoinModal(true)}>
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-purple-100 rounded-full mb-4">
                <Users className="w-8 h-8 text-purple-600" />
              </div>
              <h3 className="text-xl font-bold mb-2">Join Session</h3>
              <p className="text-gray-600">
                Enter an invite code to join
              </p>
            </div>
          </div>
        </div>

        {/* Features */}
        <div className="mt-16 grid md:grid-cols-3 gap-8">
          <div className="text-center">
            <div className="text-4xl mb-3">🤝</div>
            <h4 className="font-bold mb-2">Collaborative</h4>
            <p className="text-sm text-gray-600">Vote together on venues in real-time</p>
          </div>
          <div className="text-center">
            <div className="text-4xl mb-3">🧠</div>
            <h4 className="font-bold mb-2">Intelligent</h4>
            <p className="text-sm text-gray-600">Deep insights from Reddit, reviews, TikTok</p>
          </div>
          <div className="text-center">
            <div className="text-4xl mb-3">📍</div>
            <h4 className="font-bold mb-2">Location-Smart</h4>
            <p className="text-sm text-gray-600">Find venues fair to everyone</p>
          </div>
        </div>
      </main>

      {/* Create Session Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <h3 className="text-xl font-bold mb-4">Create Planning Session</h3>
            <form onSubmit={handleCreateSession}>
              <input
                type="text"
                className="input mb-4"
                placeholder="Session name (e.g., Saturday Night Date)"
                value={sessionName}
                onChange={(e) => setSessionName(e.target.value)}
                required
              />
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="btn btn-outline flex-1"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isLoading}
                  className="btn btn-primary flex-1"
                >
                  Create
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Join Session Modal */}
      {showJoinModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <h3 className="text-xl font-bold mb-4">Join Planning Session</h3>
            <form onSubmit={handleJoinSession}>
              <input
                type="text"
                className="input mb-4"
                placeholder="Enter invite code"
                value={inviteCode}
                onChange={(e) => setInviteCode(e.target.value.toUpperCase())}
                required
              />
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => setShowJoinModal(false)}
                  className="btn btn-outline flex-1"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isLoading}
                  className="btn btn-primary flex-1"
                >
                  Join
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
