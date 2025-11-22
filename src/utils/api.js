// Placeholder functions for future API integration

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000/api';

export const api = {
  // Authentication
  login: async (email, password) => {
    // TODO: Replace with actual API call
    // return fetch(`${API_BASE_URL}/auth/login`, {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify({ email, password })
    // }).then(res => res.json());
    
    // Mock implementation
    const adminEmail = import.meta.env.VITE_ADMIN_EMAIL;
    const adminPassword = import.meta.env.VITE_ADMIN_PASSWORD;
    
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        if (email === adminEmail && password === adminPassword) {
          resolve({ success: true, token: 'mock-token-123' });
        } else {
          reject(new Error('Credenciales inválidas'));
        }
      }, 500);
    });
  },

  // Incidents
  getIncidents: async (filters = {}) => {
    // TODO: Replace with actual API call
    // const params = new URLSearchParams(filters);
    // return fetch(`${API_BASE_URL}/incidents?${params}`).then(res => res.json());
    
    // Mock implementation - returns mock data
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({ success: true, data: [] });
      }, 300);
    });
  },

  getIncidentById: async (id) => {
    // TODO: Replace with actual API call
    // return fetch(`${API_BASE_URL}/incidents/${id}`).then(res => res.json());
    
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({ success: true, data: null });
      }, 300);
    });
  },

  updateIncident: async (id, data) => {
    // TODO: Replace with actual API call
    // return fetch(`${API_BASE_URL}/incidents/${id}`, {
    //   method: 'PUT',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify(data)
    // }).then(res => res.json());
    
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({ success: true, data });
      }, 300);
    });
  }
};
