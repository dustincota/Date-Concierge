// User types
export interface User {
  id: string;
  email: string;
  name?: string;
  created_at: string;
}

export interface UserLocation {
  id: string;
  user_id: string;
  label?: string;
  address?: string;
  latitude: number;
  longitude: number;
  neighborhood?: string;
  is_default: boolean;
}

// Venue types
export interface Venue {
  id: string;
  name: string;
  address?: string;
  neighborhood?: string;
  city: string;
  latitude?: number;
  longitude?: number;
  category?: string;
  cuisines: string[];
  price_level?: number;
  rating?: number;
  phone?: string;
  website?: string;
}

// Intelligence types
export interface SeatingRecommendation {
  spot: string;
  why: string;
  how_to_request: string;
  best_for: string[];
  source: string;
  mentions: number;
  confidence: number;
}

export interface DishRecommendation {
  item: string;
  category: string;
  must_try: boolean;
  pro_tips: string[];
  mentions: number;
  sentiment: number;
}

export interface VenueIntelligence {
  venue_id: string;
  venue_name: string;
  seating: SeatingRecommendation[];
  top_dishes: DishRecommendation[];
  trending_score: number;
  date_score: number;
  intelligence_score: number;
  warnings: string[];
}

// Session types
export interface PlanningSession {
  id: string;
  name: string;
  created_by: string;
  invite_code: string;
  target_date?: string;
  status: string;
  created_at: string;
}

export interface SessionParticipant {
  session_id: string;
  user_id: string;
  role: string;
  joined_at: string;
}

export interface VenueVote {
  session_id: string;
  venue_id: string;
  user_id: string;
  vote: number; // -1, 0, 1, 2
  comment?: string;
  voted_at: string;
}

export interface VenueWithVotes {
  venue_id: string;
  venue_name: string;
  votes: VenueVote[];
  vote_summary: {
    veto: number;
    neutral: number;
    like: number;
    love: number;
  };
  avg_score: number;
}

// WebSocket message types
export type WSMessageType =
  | 'user_joined'
  | 'user_left'
  | 'vote_update'
  | 'new_suggestion'
  | 'new_comment'
  | 'active_users';

export interface WSMessage {
  type: WSMessageType;
  user_id?: string;
  venue_id?: string;
  vote?: number;
  comment?: string;
  users?: string[];
  timestamp?: string;
}
