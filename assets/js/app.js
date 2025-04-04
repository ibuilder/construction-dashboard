import { initAuth, currentUser, signOut } from './auth.js';
import { supabase, hasPermission, PERMISSION_LEVELS, MODULES } from '../../supabase/init.js';

// Global app state
const appState = {
  currentModule: null,
  currentSection: null,
  isLoading: false,
  notifications: [],
  breadcrumbs: []
};

// Initialize app
async function initApp() {
  try {
    appState.isLoading = true;
    
    // Initialize auth
    const user = await initAuth();
    if (!user) {
      // Redirect to login if not on login page already
      if (!window.location.pathname.includes('login.html')) {
        window.location.href = '/pages/login.html';
        return;
      }
    }
    
    // Initialize UI components
    initNavigation();
    initSidebar();
    initBreadcrumbs();
    setupEventListeners();
    
    // Initialize notifications
    await loadNotifications();
    
    // If on dashboard page, initialize dashboard widgets
    if (window.location.pathname.includes('dashboard.html')) {
      initDashboard();
    }
    
    appState.isLoading = false;
  } catch (error) {
    console.error('Error initializing app:', error);
    appState.isLoading = false;
  }
}

// Initialize navigation
function initNavigation() {
  const navLinks = document.querySelectorAll('[data-module]');
  
  navLinks.forEach(link => {
    const moduleId = link.getAttribute('data-module');
    
    // Hide navigation items based on permissions
    if (currentUser && moduleId) {
      hasPermission(currentUser.id, moduleId, PERMISSION_LEVELS.READ).then(hasAccess => {
        link.style.display = hasAccess ? '' : 'none';
      });
    }
    
    // Set active module based on current URL
    if (window.location.pathname.includes(moduleId)) {
      link.classList.add('active');
      appState.currentModule = moduleId;
    }
  });
  
  // Setup signout button
  const signOutBtn = document.getElementById('sign-out-btn');
  if (signOutBtn) {
    signOutBtn.addEventListener('click', (e) => {
      e.preventDefault();
      signOut();
    });
  }
}

// Initialize sidebar
function initSidebar() {
  const sidebarToggle = document.getElementById('sidebar-toggle');
  const sidebar = document.querySelector('.sidebar');
  
  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', () => {
      sidebar.classList.toggle('collapsed');
      
      // Update layout classes
      const mainContent = document.querySelector('.main-content');
      if (mainContent) {
        mainContent.classList.toggle('expanded');
      }
    });
  }
}

// Initialize breadcrumbs
function initBreadcrumbs() {
  const breadcrumbContainer = document.querySelector('.breadcrumb');
  if (!breadcrumbContainer) return;
  
  const pathSegments = window.location.pathname.split('/').filter(segment => segment !== '' && !segment.includes('.html'));
  
  // Clear existing breadcrumbs
  breadcrumbContainer.innerHTML = '';
  
  // Add home breadcrumb
  const homeLi = document.createElement('li');
  homeLi.classList.add('breadcrumb-item');
  
  const homeLink = document.createElement('a');
  homeLink.href = '/pages/dashboard.html';
  homeLink.textContent = 'Dashboard';
  
  homeLi.appendChild(homeLink);
  breadcrumbContainer.appendChild(homeLi);
  
  // Add path segments as breadcrumbs
  let currentPath = '/pages';
  pathSegments.forEach((segment, index) => {
    currentPath += `/${segment}`;
    
    const li = document.createElement('li');
    li.classList.add('breadcrumb-item');
    
    if (index === pathSegments.length - 1) {
      li.classList.add('active');
      li.textContent = formatBreadcrumbText(segment);
    } else {
      const link = document.createElement('a');
      link.href = `${currentPath}.html`;
      link.textContent = formatBreadcrumbText(segment);
      li.appendChild(link);
    }
    
    breadcrumbContainer.appendChild(li);
  });
}

// Helper to format breadcrumb text
function formatBreadcrumbText(text) {
  return text
    .replace(/-/g, ' ')
    .replace(/\b\w/g, char => char.toUpperCase());
}

// Initialize dashboard widgets
async function initDashboard() {
  try {
    // Load dashboard widgets
    await loadTaskSummary();
    await loadRecentActivity();
    await loadUpcomingDeadlines();
    await loadProjectStats();
    
    // Initialize dashboard charts
    initProjectProgressChart();
    initCostBreakdownChart();
  } catch (error) {
    console.error('Error initializing dashboard:', error);
  }
}

// Load task summary widget
async function loadTaskSummary() {
  try {
    const { data, error } = await supabase
      .rpc('get_task_summary', { user_id: currentUser.id });
    
    if (error) throw error;
    
    const taskSummaryEl = document.getElementById('task-summary');
    if (taskSummaryEl) {
      // Update task counts
      const taskCounts = {
        total: data.total_tasks || 0,
        completed: data.completed_tasks || 0,
        overdue: data.overdue_tasks || 0,
        upcoming: data.upcoming_tasks || 0
      };
      
      Object.keys(taskCounts).forEach(key => {
        const countEl = taskSummaryEl.querySelector(`.${key}-count`);
        if (countEl) {
          countEl.textContent = taskCounts[key];
        }
      });
      
      // Update progress bar
      const progressBar = taskSummaryEl.querySelector('.progress-bar');
      if (progressBar && taskCounts.total > 0) {
        const percentage = Math.round((taskCounts.completed / taskCounts.total) * 100);
        progressBar.style.width = `${percentage}%`;
        progressBar.setAttribute('aria-valuenow', percentage);
      }
    }
  } catch (error) {
    console.error('Error loading task summary:', error);
  }
}

// Load recent activity widget
async function loadRecentActivity() {
  try {
    const { data, error } = await supabase
      .from('activity_log')
      .select(`
        id,
        action,
        module,
        record_id,
        record_type,
        created_at,
        users(first_name, last_name)
      `)
      .order('created_at', { ascending: false })
      .limit(10);
    
    if (error) throw error;
    
    const activityContainer = document.getElementById('recent-activity');
    if (activityContainer && data) {
      const activityList = activityContainer.querySelector('.activity-list');
      if (activityList) {
        activityList.innerHTML = '';
        
        if (data.length === 0) {
          activityList.innerHTML = '<div class="no-activity">No recent activity</div>';
          return;
        }
        
        data.forEach(activity => {
          const activityItem = document.createElement('div');
          activityItem.className = 'activity-item';
          
          const formattedDate = new Date(activity.created_at).toLocaleString();
          const userName = `${activity.users.first_name} ${activity.users.last_name}`;
          
          activityItem.innerHTML = `
            <div class="activity-icon">
              <i class="bi ${getActivityIcon(activity.action)}"></i>
            </div>
            <div class="activity-details">
              <div class="activity-text">
                <strong>${userName}</strong> ${formatActivityAction(activity.action)} 
                <a href="${getRecordUrl(activity.module, activity.record_type, activity.record_id)}">
                  ${activity.record_type.replace(/_/g, ' ')}
                </a>
              </div>
              <div class="activity-time">${formattedDate}</div>
            </div>
          `;
          
          activityList.appendChild(activityItem);
        });
      }
    }
  } catch (error) {
    console.error('Error loading recent activity:', error);
  }
}

// Helper function to get icon for activity type
function getActivityIcon(action) {
  switch (action) {
    case 'create': return 'bi-plus-circle';
    case 'update': return 'bi-pencil';
    case 'delete': return 'bi-trash';
    case 'comment': return 'bi-chat';
    case 'upload': return 'bi-cloud-upload';
    case 'download': return 'bi-cloud-download';
    case 'approve': return 'bi-check-circle';
    case 'reject': return 'bi-x-circle';
    default: return 'bi-activity';
  }
}

// Helper function to format activity action for display
function formatActivityAction(action) {
  switch (action) {
    case 'create': return 'created a';
    case 'update': return 'updated a';
    case 'delete': return 'deleted a';
    case 'comment': return 'commented on a';
    case 'upload': return 'uploaded a';
    case 'download': return 'downloaded a';
    case 'approve': return 'approved a';
    case 'reject': return 'rejected a';
    default: return action;
  }
}

// Helper function to get URL for a record
function getRecordUrl(module, recordType, recordId) {
  return `/pages/${module}/${recordType.replace(/_/g, '-')}.html?id=${recordId}`;
}

// Load upcoming deadlines widget
async function loadUpcomingDeadlines() {
  try {
    const today = new Date();
    const twoWeeksLater = new Date(today);
    twoWeeksLater.setDate(today.getDate() + 14);
    
    const { data, error } = await supabase
      .from('deadlines')
      .select(`
        id,
        title,
        due_date,
        priority,
        module,
        record_type,
        record_id,
        assigned_to,
        users(first_name, last_name)
      `)
      .gte('due_date', today.toISOString())
      .lte('due_date', twoWeeksLater.toISOString())
      .order('due_date', { ascending: true })
      .limit(5);
    
    if (error) throw error;
    
    const deadlinesContainer = document.getElementById('upcoming-deadlines');
    if (deadlinesContainer && data) {
      const deadlinesList = deadlinesContainer.querySelector('.deadlines-list');
      if (deadlinesList) {
        deadlinesList.innerHTML = '';
        
        if (data.length === 0) {
          deadlinesList.innerHTML = '<div class="no-deadlines">No upcoming deadlines</div>';
          return;
        }
        
        data.forEach(deadline => {
          const deadlineItem = document.createElement('div');
          deadlineItem.className = `deadline-item priority-${deadline.priority}`;
          
          const dueDate = new Date(deadline.due_date);
          const formattedDate = dueDate.toLocaleDateString();
          const daysLeft = Math.ceil((dueDate - today) / (1000 * 60 * 60 * 24));
          
          deadlineItem.innerHTML = `
            <div class="deadline-title">
              <a href="${getRecordUrl(deadline.module, deadline.record_type, deadline.record_id)}">
                ${deadline.title}
              </a>
            </div>
            <div class="deadline-info">
              <div class="deadline-date">Due: ${formattedDate}</div>
              <div class="deadline-days ${daysLeft <= 3 ? 'urgent' : ''}">
                ${daysLeft} day${daysLeft !== 1 ? 's' : ''} left
              </div>
              <div class="deadline-assignee">
                <i class="bi bi-person"></i> ${deadline.users.first_name} ${deadline.users.last_name}
              </div>
            </div>
          `;
          
          deadlinesList.appendChild(deadlineItem);
        });
      }
    }
  } catch (error) {
    console.error('Error loading upcoming deadlines:', error);
  }
}

// Load project stats widget
async function loadProjectStats() {
  try {
    // Get current project ID from URL or localStorage
    const projectId = getProjectId();
    
    const { data, error } = await supabase
      .rpc('get_project_stats', { project_id: projectId });
    
    if (error) throw error;
    
    const statsContainer = document.getElementById('project-stats');
    if (statsContainer && data) {
      // Update project info
      const projectNameEl = document.getElementById('project-name');
      if (projectNameEl) {
        projectNameEl.textContent = data.project_name || 'Project Dashboard';
      }
      
      // Update stats cards
      updateStatCard('budget-stat', formatCurrency(data.total_budget), formatCurrency(data.used_budget));
      updateStatCard('schedule-stat', formatDate(data.start_date), formatDate(data.end_date));
      updateStatCard('rfi-stat', data.total_rfis, data.open_rfis);
      updateStatCard('submittals-stat', data.total_submittals, data.open_submittals);
      updateStatCard('change-orders-stat', data.total_change_orders, formatCurrency(data.change_order_amount));
    }
  } catch (error) {
    console.error('Error loading project stats:', error);
  }
}

// Helper function to update stat card
function updateStatCard(id, totalValue, currentValue) {
  const card = document.getElementById(id);
  if (card) {
    const totalEl = card.querySelector('.stat-total');
    const currentEl = card.querySelector('.stat-current');
    
    if (totalEl) totalEl.textContent = totalValue;
    if (currentEl) currentEl.textContent = currentValue;
  }
}

// Helper function to format currency
function formatCurrency(value) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(value || 0);
}

// Helper function to format date
function formatDate(dateString) {
  if (!dateString) return 'N/A';
  return new Date(dateString).toLocaleDateString();
}

// Initialize project progress chart
function initProjectProgressChart() {
  const chartCanvas = document.getElementById('project-progress-chart');
  if (!chartCanvas) return;
  
  const ctx = chartCanvas.getContext('2d');
  
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Preconstruction', 'Engineering', 'Field', 'Contracts', 'Cost', 'BIM', 'Closeout'],
      datasets: [{
        label: 'Complete',
        data: [90, 75, 45, 80, 60, 40, 10],
        backgroundColor: '#4CAF50'
      }, {
        label: 'In Progress',
        data: [10, 20, 35, 15, 30, 50, 15],
        backgroundColor: '#FFC107'
      }, {
        label: 'Not Started',
        data: [0, 5, 20, 5, 10, 10, 75],
        backgroundColor: '#F44336'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          stacked: true,
        },
        y: {
          stacked: true,
          max: 100
        }
      }
    }
  });
}

// Initialize cost breakdown chart
function initCostBreakdownChart() {
  const chartCanvas = document.getElementById('cost-breakdown-chart');
  if (!chartCanvas) return;
  
  const ctx = chartCanvas.getContext('2d');
  
  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Labor', 'Materials', 'Equipment', 'Subcontractors', 'General Conditions', 'Overhead & Profit'],
      datasets: [{
        data: [25, 30, 15, 20, 5, 5],
        backgroundColor: [
          '#3498db',
          '#2ecc71',
          '#f1c40f',
          '#e67e22',
          '#9b59b6',
          '#34495e'
        ]
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'right'
        }
      }
    }
  });
}

// Load notifications
async function loadNotifications() {
  try {
    const { data, error } = await supabase
      .from('notifications')
      .select('*')
      .eq('user_id', currentUser.id)
      .eq('read', false)
      .order('created_at', { ascending: false });
    
    if (error) throw error;
    
    appState.notifications = data || [];
    
    // Update notification badge
    const notificationBadge = document.getElementById('notification-badge');
    if (notificationBadge) {
      notificationBadge.textContent = appState.notifications.length;
      notificationBadge.style.display = appState.notifications.length > 0 ? 'block' : 'none';
    }
    
    // Update notification dropdown
    updateNotificationsDropdown();
    
  } catch (error) {
    console.error('Error loading notifications:', error);
  }
}

// Update notifications dropdown
function updateNotificationsDropdown() {
  const dropdown = document.getElementById('notification-dropdown');
  if (!dropdown) return;
  
  const notificationList = dropdown.querySelector('.notification-list');
  if (notificationList) {
    notificationList.innerHTML = '';
    
    if (appState.notifications.length === 0) {
      notificationList.innerHTML = '<div class="no-notifications">No new notifications</div>';
      return;
    }
    
    appState.notifications.forEach(notification => {
      const notificationItem = document.createElement('a');
      notificationItem.className = 'dropdown-item notification-item';
      notificationItem.href = notification.link || '#';
      notificationItem.dataset.id = notification.id;
      
      const formattedDate = new Date(notification.created_at).toLocaleString();
      
      notificationItem.innerHTML = `
        <div class="notification-icon">
          <i class="bi ${getNotificationIcon(notification.type)}"></i>
        </div>
        <div class="notification-content">
          <div class="notification-title">${notification.title}</div>
          <div class="notification-text">${notification.message}</div>
          <div class="notification-time">${formattedDate}</div>
        </div>
        <button class="notification-mark-read" data-id="${notification.id}">
          <i class="bi bi-check"></i>
        </button>
      `;
      
      notificationList.appendChild(notificationItem);
    });
    
    // Add event listeners to mark notifications as read
    const markReadButtons = notificationList.querySelectorAll('.notification-mark-read');
    markReadButtons.forEach(button => {
      button.addEventListener('click', async (e) => {
        e.preventDefault();
        e.stopPropagation();
        
        const notificationId = button.dataset.id;
        await markNotificationAsRead(notificationId);
      });
    });
  }
}

// Helper function to get notification icon
function getNotificationIcon(type) {
  switch (type) {
    case 'rfi': return 'bi-question-circle';
    case 'submittal': return 'bi-file-earmark-check';
    case 'comment': return 'bi-chat';
    case 'mention': return 'bi-at';
    case 'approval': return 'bi-check-circle';
    case 'rejection': return 'bi-x-circle';
    case 'deadline': return 'bi-calendar-event';
    case 'change': return 'bi-arrow-clockwise';
    default: return 'bi-bell';
  }
}

// Mark notification as read
async function markNotificationAsRead(notificationId) {
  try {
    const { error } = await supabase
      .from('notifications')
      .update({ read: true })
      .eq('id', notificationId);
    
    if (error) throw error;
    
    // Update local state
    appState.notifications = appState.notifications.filter(n => n.id !== notificationId);
    
    // Update UI
    updateNotificationsDropdown();
    
    // Update badge
    const notificationBadge = document.getElementById('notification-badge');
    if (notificationBadge) {
      notificationBadge.textContent = appState.notifications.length;
      notificationBadge.style.display = appState.notifications.length > 0 ? 'block' : 'none';
    }
    
    return true;
  } catch (error) {
    console.error('Error marking notification as read:', error);
    return false;
  }
}

// Mark all notifications as read
async function markAllNotificationsAsRead() {
  try {
    const { error } = await supabase
      .from('notifications')
      .update({ read: true })
      .eq('user_id', currentUser.id)
      .eq('read', false);
    
    if (error) throw error;
    
    // Update local state
    appState.notifications = [];
    
    // Update UI
    updateNotificationsDropdown();
    
    // Update badge
    const notificationBadge = document.getElementById('notification-badge');
    if (notificationBadge) {
      notificationBadge.textContent = '0';
      notificationBadge.style.display = 'none';
    }
    
    return true;
  } catch (error) {
    console.error('Error marking all notifications as read:', error);
    return false;
  }
}

// Set up event listeners
function setupEventListeners() {
  // Mobile navigation toggle
  const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
  const navbarNav = document.querySelector('.navbar-collapse');
  
  if (mobileMenuToggle && navbarNav) {
    mobileMenuToggle.addEventListener('click', () => {
      navbarNav.classList.toggle('show');
    });
  }
  
  // Notification dropdown toggle
  const notificationToggle = document.getElementById('notification-toggle');
  const notificationDropdown = document.getElementById('notification-dropdown');
  
  if (notificationToggle && notificationDropdown) {
    notificationToggle.addEventListener('click', (e) => {
      e.preventDefault();
      notificationDropdown.classList.toggle('show');
    });
    
    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
      if (!notificationToggle.contains(e.target) && !notificationDropdown.contains(e.target)) {
        notificationDropdown.classList.remove('show');
      }
    });
    
    // Mark all as read button
    const markAllReadBtn = document.getElementById('mark-all-read');
    if (markAllReadBtn) {
      markAllReadBtn.addEventListener('click', (e) => {
        e.preventDefault();
        markAllNotificationsAsRead();
      });
    }
  }
  
  // User dropdown toggle
  const userDropdownToggle = document.getElementById('user-dropdown-toggle');
  const userDropdown = document.getElementById('user-dropdown');
  
  if (userDropdownToggle && userDropdown) {
    userDropdownToggle.addEventListener('click', (e) => {
      e.preventDefault();
      userDropdown.classList.toggle('show');
    });
    
    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
      if (!userDropdownToggle.contains(e.target) && !userDropdown.contains(e.target)) {
        userDropdown.classList.remove('show');
      }
    });
  }
  
  // Global search
  const globalSearchInput = document.getElementById('global-search');
  const searchResults = document.getElementById('search-results');
  
  if (globalSearchInput && searchResults) {
    let searchTimeout;
    
    globalSearchInput.addEventListener('input', (e) => {
      clearTimeout(searchTimeout);
      
      const query = e.target.value.trim();
      if (query.length < 2) {
        searchResults.innerHTML = '';
        searchResults.style.display = 'none';
        return;
      }
      
      searchTimeout = setTimeout(() => {
        performGlobalSearch(query);
      }, 300);
    });
    
    // Hide search results when clicking outside
    document.addEventListener('click', (e) => {
      if (!globalSearchInput.contains(e.target) && !searchResults.contains(e.target)) {
        searchResults.style.display = 'none';
      }
    });
  }
  
  // Modal close buttons
  const modalCloseButtons = document.querySelectorAll('[data-dismiss="modal"]');
  modalCloseButtons.forEach(button => {
    button.addEventListener('click', () => {
      const modal = button.closest('.modal');
      if (modal) {
        modal.style.display = 'none';
        document.body.classList.remove('modal-open');
        const modalBackdrop = document.querySelector('.modal-backdrop');
        if (modalBackdrop) {
          modalBackdrop.remove();
        }
      }
    });
  });
}

// Perform global search
async function performGlobalSearch(query) {
  try {
    const searchResults = document.getElementById('search-results');
    if (!searchResults) return;
    
    searchResults.innerHTML = '<div class="search-loading">Searching...</div>';
    searchResults.style.display = 'block';
    
    const { data, error } = await supabase
      .rpc('global_search', { search_query: query });
    
    if (error) throw error;
    
    searchResults.innerHTML = '';
    
    if (!data || data.length === 0) {
      searchResults.innerHTML = '<div class="no-results">No results found</div>';
      return;
    }
    
    // Group results by module
    const groupedResults = data.reduce((acc, result) => {
      if (!acc[result.module]) {
        acc[result.module] = [];
      }
      acc[result.module].push(result);
      return acc;
    }, {});
    
    // Create result sections by module
    Object.keys(groupedResults).forEach(module => {
      const moduleResults = groupedResults[module];
      
      const moduleSection = document.createElement('div');
      moduleSection.className = 'search-module';
      
      const moduleTitle = document.createElement('div');
      moduleTitle.className = 'module-title';
      moduleTitle.textContent = formatBreadcrumbText(module);
      
      moduleSection.appendChild(moduleTitle);
      
      const resultsList = document.createElement('div');
      resultsList.className = 'results-list';
      
      moduleResults.forEach(result => {
        const resultItem = document.createElement('a');
        resultItem.className = 'result-item';
        resultItem.href = result.url;
        
        resultItem.innerHTML = `
          <div class="result-icon">
            <i class="bi ${getModuleIcon(result.module)}"></i>
          </div>
          <div class="result-content">
            <div class="result-title">${result.title}</div>
            <div class="result-subtitle">${result.subtitle || ''}</div>
          </div>
        `;
        
        resultsList.appendChild(resultItem);
      });
      
      moduleSection.appendChild(resultsList);
      searchResults.appendChild(moduleSection);
    });
    
  } catch (error) {
    console.error('Error performing search:', error);
    
    const searchResults = document.getElementById('search-results');
    if (searchResults) {
      searchResults.innerHTML = '<div class="search-error">Error performing search</div>';
    }
  }
}

// Helper function to get module icon
function getModuleIcon(module) {
  switch (module) {
    case 'preconstruction': return 'bi-building';
    case 'engineering': return 'bi-gear';
    case 'field': return 'bi-clipboard';
    case 'safety': return 'bi-shield';
    case 'contracts': return 'bi-file-earmark-text';
    case 'cost': return 'bi-cash';
    case 'bim': return 'bi-box';
    case 'closeout': return 'bi-check-square';
    case 'settings': return 'bi-gear-fill';
    case 'reports': return 'bi-bar-chart';
    default: return 'bi-file';
  }
}

// Helper function to get current project ID
function getProjectId() {
  // Try to get from URL query parameter
  const urlParams = new URLSearchParams(window.location.search);
  const projectId = urlParams.get('project_id');
  
  if (projectId) {
    // Save to localStorage for future use
    localStorage.setItem('currentProjectId', projectId);
    return projectId;
  }
  
  // Try to get from localStorage
  const savedProjectId = localStorage.getItem('currentProjectId');
  if (savedProjectId) {
    return savedProjectId;
  }
  
  // Default project ID (should be set during initial login)
  return 1; // Default project ID
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', initApp);

// Export functions for use in other modules
export {
  appState,
  initApp,
  getProjectId,
  formatCurrency,
  formatDate
};