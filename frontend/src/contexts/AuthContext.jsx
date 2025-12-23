import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { supabase, signIn, signUp, signOut, getCurrentUser, onAuthStateChange, getUserProfile, recordGeneration } from '../lib/supabase';

const AuthContext = createContext({});

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  // Fetch user profile
  const fetchProfile = useCallback(async (userId) => {
    if (!userId) {
      setProfile(null);
      return;
    }
    try {
      const profileData = await getUserProfile(userId);
      console.log('AuthContext: Profile fetched:', profileData);
      setProfile(profileData);
    } catch (error) {
      console.error('AuthContext: Failed to fetch profile:', error);
      setProfile(null);
    }
  }, []);

  // Refresh profile (call after generation)
  const refreshProfile = useCallback(async () => {
    if (user?.id) {
      await fetchProfile(user.id);
    }
  }, [user?.id, fetchProfile]);

  useEffect(() => {
    // Check current session
    const checkUser = async () => {
      try {
        const currentUser = await getCurrentUser();
        console.log('AuthContext: Current user:', currentUser?.id);
        setUser(currentUser);
        if (currentUser) {
          // Don't block on profile fetch
          fetchProfile(currentUser.id);
        }
      } catch (error) {
        console.error('Error checking user:', error);
      } finally {
        setLoading(false);
      }
    };

    checkUser();

    // Listen for auth changes
    const { data: { subscription } } = onAuthStateChange(async (event, session) => {
      console.log('AuthContext: Auth state changed:', event);
      const newUser = session?.user ?? null;
      setUser(newUser);
      setLoading(false);
      if (newUser) {
        // Don't block on profile fetch
        fetchProfile(newUser.id);
      } else {
        setProfile(null);
      }
    });

    return () => {
      subscription?.unsubscribe();
    };
  }, [fetchProfile]);

  const login = async (email, password) => {
    const data = await signIn(email, password);
    setUser(data.user);
    return data;
  };

  const register = async (email, password) => {
    const data = await signUp(email, password);
    return data;
  };

  const logout = async () => {
    await signOut();
    setUser(null);
    setProfile(null);
  };

  // Check if user can generate (has quota remaining)
  const canGenerate = profile ? (profile.generations_used < profile.generation_quota) : true;
  const quotaRemaining = profile ? (profile.generation_quota - profile.generations_used) : null;

  // Record a generation and refresh profile
  const trackGeneration = async (metadata = {}) => {
    if (!user?.id) return;
    try {
      await recordGeneration(user.id, metadata);
      await refreshProfile();
    } catch (error) {
      console.error('Error tracking generation:', error);
    }
  };

  const value = {
    user,
    profile,
    loading,
    login,
    register,
    logout,
    refreshProfile,
    trackGeneration,
    canGenerate,
    quotaRemaining,
    isAuthenticated: !!user,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
