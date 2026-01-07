import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { sessionAPI, venueAPI } from '../utils/api';
import type { PlanningSession, VenueWithVotes } from '../types';
import { Heart, Copy, Check } from 'lucide-react';

export default function SessionPage() {
  const { id } = useParams<{ id: string }>();
  const [session, setSession] = useState<PlanningSession | null>(null);
  const [venues, setVenues] = useState<VenueWithVotes[]>([]);
  const [copied, setCopied] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadSession();
    loadVotes();
  }, [id]);

  const loadSession = async () => {
    if (!id) return;
    try {
      const data = await sessionAPI.getSession(id);
      setSession(data);
    } catch (error) {
      console.error('Failed to load session:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadVotes = async () => {
    if (!id) return;
    try {
      const data = await sessionAPI.getVotes(id);
      setVenues(data);
    } catch (error) {
      console.error('Failed to load votes:', error);
    }
  };

  const handleVote = async (venue_id: string, vote: number) => {
    if (!id) return;
    try {
      await sessionAPI.vote(id, venue_id, vote);
      await loadVotes(); // Reload votes
    } catch (error) {
      console.error('Failed to vote:', error);
    }
  };

  const copyInviteCode = () => {
    if (session?.invite_code) {
      navigator.clipboard.writeText(session.invite_code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const voteEmojis: Record<number, string> = {
    '-1': '🚫',
    '0': '😐',
    '1': '👍',
    '2': '❤️',
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading session...</p>
        </div>
      </div>
    );
  }

  if (!session) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-xl text-gray-600">Session not found</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-3">
              <Heart className="w-6 h-6 text-primary-600" fill="currentColor" />
              <h1 className="text-2xl font-bold">{session.name}</h1>
            </div>
            <button
              onClick={copyInviteCode}
              className="btn btn-outline flex items-center gap-2"
            >
              {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
              {copied ? 'Copied!' : `Code: ${session.invite_code}`}
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {venues.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-xl text-gray-600 mb-4">No venues suggested yet</p>
            <p className="text-gray-500">Search and suggest venues to get started!</p>
          </div>
        ) : (
          <div className="grid gap-6">
            {venues.map((venueData) => (
              <div key={venueData.venue_id} className="card">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-xl font-bold">{venueData.venue_name}</h3>
                    <div className="flex gap-2 mt-2">
                      {Object.entries(venueData.vote_summary).map(([type, count]) => (
                        count > 0 && (
                          <span key={type} className="text-sm bg-gray-100 px-2 py-1 rounded">
                            {voteEmojis[type as any] || type}: {count}
                          </span>
                        )
                      ))}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-primary-600">
                      {venueData.avg_score.toFixed(1)}
                    </div>
                    <div className="text-sm text-gray-500">Avg Score</div>
                  </div>
                </div>

                {/* Voting Buttons */}
                <div className="flex gap-2 border-t pt-4">
                  {[-1, 0, 1, 2].map((vote) => (
                    <button
                      key={vote}
                      onClick={() => handleVote(venueData.venue_id, vote)}
                      className="btn btn-outline flex-1 text-2xl hover:scale-110 transition-transform"
                      title={vote === -1 ? 'Veto' : vote === 0 ? 'Neutral' : vote === 1 ? 'Like' : 'Love'}
                    >
                      {voteEmojis[vote]}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
