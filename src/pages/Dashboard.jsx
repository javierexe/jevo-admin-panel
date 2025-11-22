import { useState, useEffect } from 'react';
import Layout from '../components/Layout';
import IncidentFilters from '../components/IncidentFilters';
import IncidentTable from '../components/IncidentTable';
import { useIncidents } from '../context/IncidentsContext';

const Dashboard = () => {
  const { incidents, loading, error } = useIncidents();
  const [filteredIncidents, setFilteredIncidents] = useState([]);

  // Actualizar incidentes filtrados cuando cambian los incidentes
  useEffect(() => {
    setFilteredIncidents(incidents);
  }, [incidents]);

  const handleFilterChange = (filters) => {
    let filtered = incidents;

    // Filter by project
    if (filters.project !== 'Todos') {
      filtered = filtered.filter(inc => inc.project === filters.project);
    }

    // Filter by category
    if (filters.category !== 'Todos') {
      filtered = filtered.filter(inc => inc.category === filters.category);
    }

    // Filter by status
    if (filters.status !== 'Todos') {
      filtered = filtered.filter(inc => inc.status === filters.status);
    }

    // Filter by search
    if (filters.search.trim() !== '') {
      const searchLower = filters.search.toLowerCase();
      filtered = filtered.filter(inc =>
        inc.description.toLowerCase().includes(searchLower) ||
        inc.fullDescription.toLowerCase().includes(searchLower) ||
        inc.project.toLowerCase().includes(searchLower) ||
        inc.category.toLowerCase().includes(searchLower)
      );
    }

    setFilteredIncidents(filtered);
  };

  return (
    <Layout>
      <div>
        <div className="mb-6">
          <h2 className="text-3xl font-bold text-dark-text mb-2">Incidentes Reportados</h2>
          <p className="text-dark-text-secondary">
            Total: {filteredIncidents.length} incidente{filteredIncidents.length !== 1 ? 's' : ''}
          </p>
        </div>

        {error && (
          <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
            Error: {error}
          </div>
        )}

        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
          </div>
        ) : (
          <>
            <IncidentFilters onFilterChange={handleFilterChange} />
            <IncidentTable incidents={filteredIncidents} />
          </>
        )}
      </div>
    </Layout>
  );
};

export default Dashboard;
