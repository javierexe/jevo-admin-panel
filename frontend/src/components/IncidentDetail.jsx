import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useIncidents } from '../context/IncidentsContext';
import { statusLabels } from '../data/mockData';

const IncidentDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { getIncidentById, updateIncidentStatus, updateIncidentComments, loading } = useIncidents();
  
  const [incident, setIncident] = useState(null);
  const [status, setStatus] = useState('pending');
  const [comments, setComments] = useState('');
  const [loadingIncident, setLoadingIncident] = useState(true);

  useEffect(() => {
    const loadIncident = async () => {
      setLoadingIncident(true);
      try {
        const data = await getIncidentById(id);
        if (data) {
          setIncident(data);
          setStatus(data.status);
          setComments(data.comments || '');
        }
      } catch (error) {
        console.error('Error cargando incidente:', error);
      } finally {
        setLoadingIncident(false);
      }
    };

    loadIncident();
  }, [id, getIncidentById]);

  if (loadingIncident) {
    return (
      <div className="min-h-screen bg-dark-bg flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!incident) {
    return (
      <div className="min-h-screen bg-dark-bg flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-dark-text mb-4">Incidente no encontrado</h2>
          <button
            onClick={() => navigate('/')}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md"
          >
            Volver al inicio
          </button>
        </div>
      </div>
    );
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const handleStatusChange = async (e) => {
    const newStatus = e.target.value;
    setStatus(newStatus);
    
    try {
      await updateIncidentStatus(incident.id, newStatus);
    } catch (error) {
      console.error('Error actualizando estado:', error);
      alert('Error al actualizar el estado');
      // Revertir el cambio en caso de error
      setStatus(incident.status);
    }
  };

  const handleCommentsChange = async (e) => {
    const newComments = e.target.value;
    setComments(newComments);
  };

  const handleSaveComments = async () => {
    try {
      await updateIncidentComments(incident.id, comments);
      alert('Comentario guardado exitosamente');
    } catch (error) {
      console.error('Error guardando comentarios:', error);
      alert('Error al guardar el comentario');
    }
  };

  const handleMarkAsResolved = async () => {
    try {
      await updateIncidentStatus(incident.id, 'resolved');
      setStatus('resolved');
      alert('Incidente marcado como resuelto');
    } catch (error) {
      console.error('Error marcando como resuelto:', error);
      alert('Error al marcar como resuelto');
    }
  };

  return (
    <div className="min-h-screen bg-dark-bg py-8 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="mb-6">
          <button
            onClick={() => navigate('/')}
            className="text-blue-400 hover:text-blue-300 flex items-center gap-2"
          >
            ← Volver a la lista
          </button>
        </div>

        <div className="bg-dark-card rounded-lg border border-dark-border overflow-hidden">
          <div className="px-6 py-4 border-b border-dark-border">
            <h1 className="text-2xl font-bold text-dark-text">Detalle del Incidente #{incident.id}</h1>
          </div>

          <div className="grid md:grid-cols-2 gap-6 p-6">
            {/* Left Column: Image and basic info */}
            <div className="space-y-4">
              <div className="aspect-video bg-dark-bg rounded-lg overflow-hidden border border-dark-border">
                <img
                  src={incident.image}
                  alt="Incidente"
                  className="w-full h-full object-cover"
                />
              </div>

              <div className="space-y-3">
                <div className="bg-dark-bg p-4 rounded-lg border border-dark-border">
                  <p className="text-sm text-dark-text-secondary mb-1">Proyecto</p>
                  <p className="text-lg font-semibold text-dark-text">{incident.project}</p>
                </div>

                <div className="bg-dark-bg p-4 rounded-lg border border-dark-border">
                  <p className="text-sm text-dark-text-secondary mb-1">Fecha de reporte</p>
                  <p className="text-lg font-semibold text-dark-text">{formatDate(incident.date)}</p>
                </div>
              </div>
            </div>

            {/* Right Column: Details and actions */}
            <div className="space-y-4">
              <div className="bg-dark-bg p-4 rounded-lg border border-dark-border">
                <p className="text-sm text-dark-text-secondary mb-1">Categoría</p>
                <p className="text-lg font-semibold text-dark-text">{incident.category}</p>
              </div>

              <div className="bg-dark-bg p-4 rounded-lg border border-dark-border">
                <p className="text-sm text-dark-text-secondary mb-2">Descripción completa</p>
                <p className="text-dark-text leading-relaxed">{incident.fullDescription}</p>
              </div>

              <div className="bg-dark-bg p-4 rounded-lg border border-dark-border">
                <label className="block text-sm text-dark-text-secondary mb-2">
                  Estado
                </label>
                <select
                  value={status}
                  onChange={handleStatusChange}
                  className="w-full px-3 py-2 bg-dark-card border border-dark-border rounded-md text-dark-text focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="pending">{statusLabels.pending}</option>
                  <option value="in-progress">{statusLabels['in-progress']}</option>
                  <option value="resolved">{statusLabels.resolved}</option>
                </select>
              </div>

              <div className="bg-dark-bg p-4 rounded-lg border border-dark-border">
                <label className="block text-sm text-dark-text-secondary mb-2">
                  Comentario interno
                </label>
                <textarea
                  value={comments}
                  onChange={handleCommentsChange}
                  rows="4"
                  placeholder="Agregar notas o comentarios sobre este incidente..."
                  className="w-full px-3 py-2 bg-dark-card border border-dark-border rounded-md text-dark-text placeholder-dark-text-secondary focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                  onClick={handleSaveComments}
                  disabled={loading}
                  className="mt-2 w-full py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white rounded-md font-medium transition-colors"
                >
                  {loading ? 'Guardando...' : 'Guardar Comentario'}
                </button>
              </div>

              {status !== 'resolved' && (
                <button
                  onClick={handleMarkAsResolved}
                  disabled={loading}
                  className="w-full py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white rounded-md font-medium transition-colors"
                >
                  {loading ? 'Procesando...' : 'Marcar como Resuelto'}
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default IncidentDetail;
