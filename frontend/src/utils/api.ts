import axios from 'axios';
import type { User, Venue, VenueIntelligence, PlanningSession, VenueWithVotes } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080/api';

const api = axios.create({
  baseURL: API_BASE_URL,
});

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth API
export const authAPI = {
  register: async (email: string, password: string, name?: string) => {
    const { data } = await api.post('/users/register', { email, password, name });
    return data;
  },

  login: async (email: string, password: string) => {
    const { data } = await api.post('/users/login', { email, password });
    return data;
  },

  getCurrentUser: async (): Promise<User> => {
    const { data } = await api.get('/users/me');
    return data;
  },
};

// Venue API
export const venueAPI = {
  searchVenues: async (params?: {
    neighborhood?: string;
    cuisine?: string;
    price_level?: number;
  }): Promise<Venue[]> => {
    const { data } = await api.get('/venues', { params });
    return data;
  },

  getVenue: async (id: string): Promise<Venue> => {
    const { data } = await api.get(`/venues/${id}`);
    return data;
  },

  getVenueIntelligence: async (id: string): Promise<VenueIntelligence> => {
    const { data } = await api.get(`/venues/${id}/intelligence`);
    return data;
  },

  refreshIntelligence: async (id: string) => {
    const { data } = await api.post(`/venues/${id}/intelligence/refresh`);
    return data;
  },
};

// Session API
export const sessionAPI = {
  createSession: async (name: string, target_date?: string): Promise<PlanningSession> => {
    const { data } = await api.post('/sessions', { name, target_date });
    return data;
  },

  getSession: async (id: string): Promise<PlanningSession> => {
    const { data } = await api.get(`/sessions/${id}`);
    return data;
  },

  joinSession: async (invite_code: string) => {
    const { data } = await api.post('/sessions/join', { invite_code });
    return data;
  },

  suggestVenue: async (session_id: string, venue_id: string) => {
    const { data } = await api.post(`/sessions/${session_id}/venues`, { venue_id });
    return data;
  },

  vote: async (session_id: string, venue_id: string, vote: number, comment?: string) => {
    const { data } = await api.post(`/sessions/${session_id}/votes`, {
      venue_id,
      vote,
      comment,
    });
    return data;
  },

  getVotes: async (session_id: string): Promise<VenueWithVotes[]> => {
    const { data } = await api.get(`/sessions/${session_id}/votes`);
    return data;
  },

  getOptimalLocation: async (session_id: string) => {
    const { data } = await api.get(`/sessions/${session_id}/optimal-location`);
    return data;
  },
};

export default api;
