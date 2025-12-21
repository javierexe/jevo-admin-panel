import { useState } from 'react';
import { projects, categories, statuses } from '../data/mockData';

const IncidentFilters = ({ onFilterChange }) => {
  const [filters, setFilters] = useState({
    project: 'Todos',
    category: 'Todos',
    status: 'Todos',
    search: ''
  });

  const handleChange = (key, value) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    onFilterChange(newFilters);
  };

  return (
    <div className="bg-dark-card p-4 rounded-lg border border-dark-border mb-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div>
          <label className="block text-sm font-medium text-dark-text mb-2">
            Proyecto
          </label>
          <select
            value={filters.project}
            onChange={(e) => handleChange('project', e.target.value)}
            className="w-full px-3 py-2 bg-dark-bg border border-dark-border rounded-md text-dark-text focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {projects.map(project => (
              <option key={project} value={project}>{project}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-dark-text mb-2">
            Categoría
          </label>
          <select
            value={filters.category}
            onChange={(e) => handleChange('category', e.target.value)}
            className="w-full px-3 py-2 bg-dark-bg border border-dark-border rounded-md text-dark-text focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {categories.map(category => (
              <option key={category} value={category}>{category}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-dark-text mb-2">
            Estado
          </label>
          <select
            value={filters.status}
            onChange={(e) => handleChange('status', e.target.value)}
            className="w-full px-3 py-2 bg-dark-bg border border-dark-border rounded-md text-dark-text focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {statuses.map(status => (
              <option key={status} value={status}>
                {status === 'Todos' ? 'Todos' : 
                 status === 'pending' ? 'Pendiente' :
                 status === 'in-progress' ? 'En Progreso' :
                 'Resuelto'}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-dark-text mb-2">
            Búsqueda
          </label>
          <input
            type="text"
            value={filters.search}
            onChange={(e) => handleChange('search', e.target.value)}
            placeholder="Buscar incidente..."
            className="w-full px-3 py-2 bg-dark-bg border border-dark-border rounded-md text-dark-text placeholder-dark-text-secondary focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>
    </div>
  );
};

export default IncidentFilters;
