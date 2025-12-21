import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { IncidentsProvider } from './context/IncidentsContext';
import Login from './components/Login';
import Dashboard from './pages/Dashboard';
import IncidentDetail from './components/IncidentDetail';
import ProtectedRoute from './components/ProtectedRoute';
import './index.css';

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <IncidentsProvider>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/incident/:id"
              element={
                <ProtectedRoute>
                  <IncidentDetail />
                </ProtectedRoute>
              }
            />
          </Routes>
        </IncidentsProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
