// Mock data for incidents
export const mockIncidents = [
  {
    id: 1,
    project: 'POS Botillería',
    category: 'Error de Sistema',
    description: 'El sistema no procesa pagos con tarjeta de crédito',
    fullDescription: 'Al intentar procesar un pago con tarjeta de crédito Visa, el sistema arroja error 500 y no completa la transacción. El cliente debe reintentar múltiples veces.',
    status: 'pending',
    date: '2025-11-20T14:30:00',
    image: 'https://via.placeholder.com/400x300?text=POS+Error+Screenshot',
    comments: ''
  },
  {
    id: 2,
    project: 'Agenda Lava Autos',
    category: 'Bug Interface',
    description: 'Calendario no muestra citas del día actual',
    fullDescription: 'El calendario de la agenda no carga las citas agendadas para el día actual. Al cambiar de fecha y volver, el problema persiste.',
    status: 'in-progress',
    date: '2025-11-21T09:15:00',
    image: 'https://via.placeholder.com/400x300?text=Calendar+Bug',
    comments: 'Revisando base de datos'
  },
  {
    id: 3,
    project: 'POS Botillería',
    category: 'Solicitud de Mejora',
    description: 'Agregar impresión automática de boletas',
    fullDescription: 'Los usuarios solicitan que después de cada venta se imprima automáticamente la boleta sin necesidad de presionar el botón de imprimir manualmente.',
    status: 'pending',
    date: '2025-11-19T16:45:00',
    image: 'https://via.placeholder.com/400x300?text=Feature+Request',
    comments: ''
  },
  {
    id: 4,
    project: 'Agenda Lava Autos',
    category: 'Error de Sistema',
    description: 'No se pueden cancelar citas',
    fullDescription: 'Al intentar cancelar una cita desde el panel de administración, aparece un mensaje de error y la cita permanece activa.',
    status: 'resolved',
    date: '2025-11-18T11:20:00',
    image: 'https://via.placeholder.com/400x300?text=Cancel+Error',
    comments: 'Solucionado en versión 1.2.3'
  },
  {
    id: 5,
    project: 'POS Botillería',
    category: 'Bug Interface',
    description: 'Botón de descuento no visible en móvil',
    fullDescription: 'En dispositivos móviles con pantallas pequeñas, el botón para aplicar descuentos no es visible y los usuarios no pueden aplicar promociones.',
    status: 'in-progress',
    date: '2025-11-21T13:00:00',
    image: 'https://via.placeholder.com/400x300?text=Mobile+UI+Bug',
    comments: 'Trabajando en diseño responsive'
  },
  {
    id: 6,
    project: 'Agenda Lava Autos',
    category: 'Solicitud de Mejora',
    description: 'Notificaciones por WhatsApp',
    fullDescription: 'Los clientes solicitan recibir recordatorios de sus citas a través de WhatsApp además del correo electrónico actual.',
    status: 'pending',
    date: '2025-11-17T10:30:00',
    image: 'https://via.placeholder.com/400x300?text=WhatsApp+Integration',
    comments: ''
  }
];

export const projects = ['Todos', 'POS Botillería', 'Agenda Lava Autos'];
export const categories = ['Todos', 'Error de Sistema', 'Bug Interface', 'Solicitud de Mejora'];
export const statuses = ['Todos', 'pending', 'in-progress', 'resolved'];

export const statusLabels = {
  pending: 'Pendiente',
  'in-progress': 'En Progreso',
  resolved: 'Resuelto'
};

export const statusColors = {
  pending: 'bg-yellow-600',
  'in-progress': 'bg-blue-600',
  resolved: 'bg-green-600'
};
