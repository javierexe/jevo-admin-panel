import { createContext, useContext, useState, useEffect } from 'react';
import { getIncidents as fetchIncidents, getIncidentById as fetchIncidentById, updateIncident } from '../api/incidents';

const IncidentsContext = createContext(null);

export const IncidentsProvider = ({ children }) => {
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Cargar incidentes al montar el componente
  useEffect(() => {
    loadIncidents();
  }, []);

  const loadIncidents = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchIncidents();
      setIncidents(data);
    } catch (err) {
      setError(err.message);
      console.error('Error cargando incidentes:', err);
    } finally {
      setLoading(false);
    }
  };

  const updateIncidentStatus = async (id, newStatus) => {
    setLoading(true);
    setError(null);
    try {
      await updateIncident(id, { status: newStatus });
      
      // Recargar incidentes después de actualizar
      await loadIncidents();
    } catch (err) {
      setError(err.message);
      console.error('Error actualizando incidente:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const updateIncidentComments = async (id, comment) => {
    setLoading(true);
    setError(null);
    try {
      await updateIncident(id, { internalComment: comment });
      
      // Recargar incidentes después de actualizar
      await loadIncidents();
    } catch (err) {
      setError(err.message);
      console.error('Error actualizando comentarios:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const getIncidentById = async (id) => {
    setLoading(true);
    setError(null);
    try {
      const incident = await fetchIncidentById(id);
      return incident;
    } catch (err) {
      setError(err.message);
      console.error('Error obteniendo incidente:', err);
      // Fallback: buscar en el estado local
      return incidents.find(incident => incident.id === parseInt(id));
    } finally {
      setLoading(false);
    }
  };

  return (
    <IncidentsContext.Provider
      value={{
        incidents,
        updateIncidentStatus,
        updateIncidentComments,
        getIncidentById,
        loadIncidents,
        loading,
        error
      }}
    >
      {children}
    </IncidentsContext.Provider>
  );
};

export const useIncidents = () => {
  const context = useContext(IncidentsContext);
  if (!context) {
    throw new Error('useIncidents must be used within IncidentsProvider');
  }
  return context;
};
