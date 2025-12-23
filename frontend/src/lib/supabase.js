import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
  console.warn('Supabase credentials not found. Auth will be disabled.');
}

export const supabase = supabaseUrl && supabaseAnonKey 
  ? createClient(supabaseUrl, supabaseAnonKey)
  : null;

// Auth helpers
export const signUp = async (email, password) => {
  if (!supabase) throw new Error('Supabase not configured');
  const { data, error } = await supabase.auth.signUp({
    email,
    password,
  });
  if (error) throw error;
  return data;
};

export const signIn = async (email, password) => {
  if (!supabase) throw new Error('Supabase not configured');
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password,
  });
  if (error) throw error;
  return data;
};

export const signOut = async () => {
  if (!supabase) return;
  const { error } = await supabase.auth.signOut();
  if (error) throw error;
};

export const getCurrentUser = async () => {
  if (!supabase) return null;
  const { data: { user } } = await supabase.auth.getUser();
  return user;
};

export const onAuthStateChange = (callback) => {
  if (!supabase) return { data: { subscription: { unsubscribe: () => {} } } };
  return supabase.auth.onAuthStateChange(callback);
};

// Profile helpers
export const getUserProfile = async (userId) => {
  if (!supabase) {
    console.warn('getUserProfile: Supabase not configured');
    return null;
  }
  console.log('getUserProfile: Fetching profile for user:', userId);
  const { data, error } = await supabase
    .from('profiles')
    .select('*')
    .eq('id', userId)
    .single();
  if (error) {
    console.error('getUserProfile: Error fetching profile:', error);
    return null;
  }
  console.log('getUserProfile: Got profile:', data);
  return data;
};

// Record a generation (increments usage)
export const recordGeneration = async (userId, metadata = {}) => {
  if (!supabase) return null;
  
  console.log('recordGeneration: Starting for user:', userId);
  
  // 1. Insert generation record
  const { data, error } = await supabase
    .from('generations')
    .insert({
      user_id: userId,
      status: 'completed',
      ...metadata
    })
    .select()
    .single();
  
  if (error) {
    console.error('Error inserting generation:', error);
    throw error;
  }
  console.log('recordGeneration: Inserted generation record:', data);
  
  // 2. Increment generations_used in profiles
  // Fetch current value and increment (Supabase JS doesn't support raw SQL increment)
  const { data: profile, error: fetchError } = await supabase
    .from('profiles')
    .select('generations_used')
    .eq('id', userId)
    .single();
  
  if (fetchError) {
    console.error('Error fetching profile for increment:', fetchError);
  } else if (profile) {
    const newCount = (profile.generations_used || 0) + 1;
    console.log('recordGeneration: Updating generations_used from', profile.generations_used, 'to', newCount);
    
    const { error: updateError } = await supabase
      .from('profiles')
      .update({ 
        generations_used: newCount,
        updated_at: new Date().toISOString()
      })
      .eq('id', userId);
    
    if (updateError) {
      console.error('Error updating generations_used:', updateError);
    } else {
      console.log('recordGeneration: Successfully updated generations_used');
    }
  }
  
  return data;
};

// Get user's generation history
export const getUserGenerations = async (userId, limit = 10) => {
  if (!supabase) return [];
  const { data, error } = await supabase
    .from('generations')
    .select('*')
    .eq('user_id', userId)
    .order('created_at', { ascending: false })
    .limit(limit);
  if (error) {
    console.error('Error fetching generations:', error);
    return [];
  }
  return data || [];
};
