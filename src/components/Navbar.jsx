import { useAuth } from '../context/AuthContext';

const Navbar = () => {
  const { logout } = useAuth();

  return (
    <nav className="bg-dark-card border-b border-dark-border px-6 py-4">
      <div className="flex justify-between items-center max-w-7xl mx-auto">
        <div>
          <h1 className="text-2xl font-bold text-dark-text">Panel Administrativo</h1>
          <p className="text-sm text-dark-text-secondary">Gestión de Incidentes</p>
        </div>
        <button
          onClick={logout}
          className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-md transition-colors"
        >
          Cerrar Sesión
        </button>
      </div>
    </nav>
  );
};

export default Navbar;
