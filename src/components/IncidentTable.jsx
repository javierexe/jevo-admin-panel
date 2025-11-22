import { useNavigate } from 'react-router-dom';
import { statusLabels, statusColors } from '../data/mockData';

const IncidentTable = ({ incidents }) => {
  const navigate = useNavigate();

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

  return (
    <div className="bg-dark-card rounded-lg border border-dark-border overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-dark-border bg-dark-bg">
              <th className="px-6 py-3 text-left text-xs font-medium text-dark-text-secondary uppercase tracking-wider">
                Proyecto
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-dark-text-secondary uppercase tracking-wider">
                Categoría
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-dark-text-secondary uppercase tracking-wider">
                Descripción
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-dark-text-secondary uppercase tracking-wider">
                Estado
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-dark-text-secondary uppercase tracking-wider">
                Fecha
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-dark-text-secondary uppercase tracking-wider">
                Acciones
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-dark-border">
            {incidents.length === 0 ? (
              <tr>
                <td colSpan="6" className="px-6 py-8 text-center text-dark-text-secondary">
                  No se encontraron incidentes
                </td>
              </tr>
            ) : (
              incidents.map((incident) => (
                <tr key={incident.id} className="hover:bg-dark-bg transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-dark-text">
                    {incident.project}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-dark-text">
                    {incident.category}
                  </td>
                  <td className="px-6 py-4 text-sm text-dark-text max-w-xs truncate">
                    {incident.description}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${statusColors[incident.status]} text-white`}>
                      {statusLabels[incident.status]}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-dark-text-secondary">
                    {formatDate(incident.date)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <button
                      onClick={() => navigate(`/incident/${incident.id}`)}
                      className="text-blue-400 hover:text-blue-300 font-medium"
                    >
                      Ver
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default IncidentTable;
