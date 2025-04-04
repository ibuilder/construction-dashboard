import { supabase, USER_ROLES } from '../../supabase/init.js';

// Auth state management
let currentUser = null;

// Initialize auth and check session
async function initAuth() {
  // Check for existing session
  const { data: { session }, error } = await supabase.auth.getSession();
  
  if (error) {
    console.error('Error getting session:', error.message);
    return null;
  }
  
  if (session) {
    await fetchUserProfile(session.user.id);
    setupAuthUI(true);
    return currentUser;
  } else {
    setupAuthUI(false);
    return null;
  }
}

// Fetch extended user profile
async function fetchUserProfile(userId) {
  try {
    const { data, error } = await supabase
      .from('users')
      .select(`
        id,
        email,
        first_name,
        last_name,
        role,
        company_id,
        companies(name, type),
        profile_image_url,
        last_login,
        created_at
      `)
      .eq('id', userId)
      .single();
    
    if (error) throw error;
    
    currentUser = data;
    return data;
  } catch (error) {
    console.error('Error fetching user profile:', error.message);
    return null;
  }
}

// Sign in with email and password
async function signIn(email, password) {
  try {
    const { data: { user, session }, error } = await supabase.auth.signInWithPassword({
      email,
      password
    });
    
    if (error) throw error;
    
    await fetchUserProfile(user.id);
    
    // Update last login time
    await supabase
      .from('users')
      .update({ last_login: new Date().toISOString() })
      .eq('id', user.id);
    
    setupAuthUI(true);
    
    // Redirect to dashboard or reload
    window.location.href = '/pages/dashboard.html';
    
    return { user: currentUser, session };
  } catch (error) {
    console.error('Error signing in:', error.message);
    showAuthError(error.message);
    return { error };
  }
}

// Sign up a new user
async function signUp(email, password, firstName, lastName, company, role) {
  try {
    // Check if role is valid
    if (!Object.values(USER_ROLES).includes(role)) {
      throw new Error('Invalid user role');
    }
    
    // First create the auth user
    const { data: { user }, error } = await supabase.auth.signUp({
      email,
      password,
    });
    
    if (error) throw error;
    
    // Then create or get company ID
    let companyId;
    
    if (company.id) {
      companyId = company.id;
    } else {
      // Create new company
      const { data: newCompany, error: companyError } = await supabase
        .from('companies')
        .insert({
          name: company.name,
          type: company.type
        })
        .select('id')
        .single();
      
      if (companyError) throw companyError;
      companyId = newCompany.id;
    }
    
    // Create user profile
    const { error: profileError } = await supabase
      .from('users')
      .insert({
        id: user.id,
        email,
        first_name: firstName,
        last_name: lastName,
        role,
        company_id: companyId,
        created_at: new Date().toISOString(),
        last_login: new Date().toISOString()
      });
    
    if (profileError) throw profileError;
    
    showSuccessMessage('Account created! Please check your email for verification.');
    return { user };
  } catch (error) {
    console.error('Error signing up:', error.message);
    showAuthError(error.message);
    return { error };
  }
}

// Sign out
async function signOut() {
  try {
    const { error } = await supabase.auth.signOut();
    if (error) throw error;
    
    currentUser = null;
    setupAuthUI(false);
    
    // Redirect to login page
    window.location.href = '/pages/login.html';
    
    return { success: true };
  } catch (error) {
    console.error('Error signing out:', error.message);
    return { error };
  }
}

// Reset password
async function resetPassword(email) {
  try {
    const { error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${window.location.origin}/pages/reset-password.html`,
    });
    
    if (error) throw error;
    
    showSuccessMessage('Password reset instructions sent to your email');
    return { success: true };
  } catch (error) {
    console.error('Error resetting password:', error.message);
    showAuthError(error.message);
    return { error };
  }
}

// Update password
async function updatePassword(password) {
  try {
    const { error } = await supabase.auth.updateUser({
      password
    });
    
    if (error) throw error;
    
    showSuccessMessage('Password updated successfully');
    return { success: true };
  } catch (error) {
    console.error('Error updating password:', error.message);
    showAuthError(error.message);
    return { error };
  }
}

// UI Helpers
function setupAuthUI(isLoggedIn) {
  const loginElements = document.querySelectorAll('.login-only');
  const loggedInElements = document.querySelectorAll('.logged-in-only');
  
  loginElements.forEach(el => {
    el.style.display = isLoggedIn ? 'none' : '';
  });
  
  loggedInElements.forEach(el => {
    el.style.display = isLoggedIn ? '' : 'none';
  });
  
  // Update user info display if logged in
  if (isLoggedIn && currentUser) {
    const userNameElements = document.querySelectorAll('.user-name');
    const userRoleElements = document.querySelectorAll('.user-role');
    const userImageElements = document.querySelectorAll('.user-image');
    
    userNameElements.forEach(el => {
      el.textContent = `${currentUser.first_name} ${currentUser.last_name}`;
    });
    
    userRoleElements.forEach(el => {
      el.textContent = currentUser.role.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
    });
    
    userImageElements.forEach(el => {
      if (currentUser.profile_image_url) {
        el.src = currentUser.profile_image_url;
      }
    });
  }
}

function showAuthError(message) {
  const errorElement = document.getElementById('auth-error');
  if (errorElement) {
    errorElement.textContent = message;
    errorElement.style.display = 'block';
  }
}

function showSuccessMessage(message) {
  const successElement = document.getElementById('auth-success');
  if (successElement) {
    successElement.textContent = message;
    successElement.style.display = 'block';
  }
}

// Auth state change listener
supabase.auth.onAuthStateChange(async (event, session) => {
  if (event === 'SIGNED_IN' && session) {
    await fetchUserProfile(session.user.id);
    setupAuthUI(true);
  } else if (event === 'SIGNED_OUT') {
    currentUser = null;
    setupAuthUI(false);
  }
});

// Export auth functions
export {
  initAuth,
  signIn,
  signUp,
  signOut,
  resetPassword,
  updatePassword,
  currentUser
};