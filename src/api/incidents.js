const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000/api';

/**
 * Obtiene todos los incidentes
 * @returns {Promise<Array>} Lista de incidentes
 */
export async function getIncidents() {
  const response = await fetch(`${API_BASE_URL}/incidents`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`Error al obtener incidentes: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Obtiene un incidente por ID
 * @param {string} id - ID del incidente
 * @returns {Promise<Object>} Detalle del incidente
 */
export async function getIncidentById(id) {
  const response = await fetch(`${API_BASE_URL}/incidents/${id}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`Error al obtener incidente: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Actualiza un incidente
 * @param {string} id - ID del incidente
 * @param {Object} payload - Datos a actualizar (estado, comentario interno, etc)
 * @returns {Promise<Object>} Incidente actualizado
 */
export async function updateIncident(id, payload) {
  const response = await fetch(`${API_BASE_URL}/incidents/${id}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`Error al actualizar incidente: ${response.statusText}`);
  }

  return response.json();
}
