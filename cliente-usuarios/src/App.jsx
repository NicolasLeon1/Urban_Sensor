import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation, useNavigate } from 'react-router-dom';
import { 
  Layout, Menu, Card, Avatar, Typography, Table, Button, 
  Tag, Space, Modal, Form, Input, Select, message, Popconfirm, Breadcrumb, Descriptions, Divider
} from 'antd';
import { 
  TeamOutlined, DashboardOutlined, BellOutlined, 
  PlusOutlined, EditOutlined, DeleteOutlined, 
  EyeOutlined, StopOutlined, CheckCircleOutlined, 
  CloseCircleOutlined, ClockCircleOutlined, UserOutlined
} from '@ant-design/icons';
import api from './api';

// Importamos los estilos CSS
import './dashboard.css';

const { Header, Sider, Content } = Layout;
const { Title, Text } = Typography;
const { Option } = Select;

// --- 1. DASHBOARD HOME (Limpio) ---
const DashboardHome = () => {
  const [stats, setStats] = useState({ 
    total_usuarios: 0, total_abiertas: 0, total_derivadas: 0, 
    total_rechazadas: 0, total_finalizadas: 0 
  });
  
  const navigate = useNavigate();

  useEffect(() => {
    api.get('dashboard-stats/').then(res => setStats(res.data)).catch(() => {});
  }, []);

  return (
    <div className="dashboard-content-wrapper">
      <div className="page-header">
        <h1 className="page-title">Panel de Administración (SECPLA)</h1>
        <p className="page-subtitle">Resumen general del sistema.</p>
      </div>

      {/* GRID DE TARJETAS */}
      <div className="dashboard-stats">
        <div className="stat-card user-card">
            <div className="stat-icon"><TeamOutlined /></div>
            <div className="stat-info">
                <h4>Usuarios Activos</h4>
                <span className="stat-value">{stats.total_usuarios || 0}</span>
            </div>
        </div>
        <div className="stat-card border-cyan">
            <h4>Incidencias Abiertas</h4>
            <span className="stat-value">{stats.total_abiertas || 0}</span>
        </div>
        <div className="stat-card border-yellow">
            <h4>En Gestión</h4>
            <span className="stat-value">{stats.total_derivadas || 0}</span>
        </div>
        <div className="stat-card border-red">
            <h4>Rechazadas</h4>
            <span className="stat-value">{stats.total_rechazadas || 0}</span>
        </div>
        <div className="stat-card border-green">
            <h4>Finalizadas</h4>
            <span className="stat-value">{stats.total_finalizadas || 0}</span>
        </div>
      </div>

      {/* ACCESOS RÁPIDOS (Solo Usuarios) */}
      <div className="custom-card">
        <div className="custom-card-header">
           <h2>Accesos Rápidos</h2>
        </div>
        <div className="custom-card-body">
           <div className="quick-links-grid">
              <div className="quick-link-item" onClick={() => navigate('/usuarios')}>
                 <TeamOutlined className="quick-link-icon" />
                 <span>Gestión de Usuarios</span>
              </div>
              {/* Se eliminaron los otros módulos */}
           </div>
        </div>
      </div>
    </div>
  );
};

// --- 2. GESTIÓN DE USUARIOS (Con Ver y Bloquear) ---
const UserManagement = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // Estado para Modal de Creación/Edición
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [form] = Form.useForm();
  const [editingUser, setEditingUser] = useState(null);
  
  // Estado para Modal de VER USUARIO
  const [isViewModalOpen, setIsViewModalOpen] = useState(false);
  const [viewingUser, setViewingUser] = useState(null);

  const [options, setOptions] = useState({ perfiles: [], departamentos: [], direcciones: [] });
  const [selectedProfile, setSelectedProfile] = useState(null);

  useEffect(() => { fetchUsers(); fetchOptions(); }, []);

  const fetchUsers = async () => {
    setLoading(true);
    try { const res = await api.get('users/'); setUsers(res.data); } catch { message.error('Error cargando usuarios'); }
    setLoading(false);
  };
  const fetchOptions = async () => {
    try { const res = await api.get('options/'); setOptions(res.data); } catch {}
  };

  // --- Acciones de Guardado ---
  const handleOk = async () => {
    try {
      const values = await form.validateFields();
      if (editingUser) await api.put(`users/${editingUser.id}/`, values);
      else await api.post('users/', values);
      message.success('Guardado correctamente');
      setIsModalOpen(false); form.resetFields(); fetchUsers();
    } catch {}
  };

  // --- Abrir Modales ---
  const openModal = (user = null) => {
    setEditingUser(user);
    form.setFieldsValue(user ? {...user, perfil: user.perfil} : {});
    setSelectedProfile(user?.perfil || null);
    setIsModalOpen(true);
  };

  const openViewModal = (user) => {
    setViewingUser(user);
    setIsViewModalOpen(true);
  };

  // --- Acciones de Estado ---
  const toggleStatus = async (user) => { 
     try { 
         await api.post(`users/${user.id}/toggle_status/`); 
         fetchUsers(); 
         message.success(user.activo ? 'Usuario bloqueado' : 'Usuario activado'); 
     } catch { message.error('Error al cambiar estado'); }
  };

  const deleteUser = async (id) => {
     try { await api.delete(`users/${id}/`); fetchUsers(); message.success('Usuario eliminado'); } catch {}
  };

  // --- Columnas de la Tabla ---
  const columns = [
    { title: 'Usuario', dataIndex: 'username', render: t => <b>{t}</b> },
    { title: 'Nombre', render: (_, r) => `${r.nombre} ${r.apellido}` },
    { title: 'Perfil', dataIndex: 'perfil_nombre', render: t => <Tag color="blue">{t}</Tag> },
    { title: 'Estado', dataIndex: 'activo', render: a => <Tag color={a ? 'green' : 'red'}>{a ? 'Activo' : 'Bloqueado'}</Tag> },
    { title: 'Acciones', width: 200, render: (_, r) => (
        <Space>
          {/* Botón VER */}
          <Button icon={<EyeOutlined />} onClick={() => openViewModal(r)} title="Ver detalle" />
          
          {/* Botón EDITAR */}
          <Button icon={<EditOutlined />} onClick={() => openModal(r)} title="Editar" />
          
          {/* Botón BLOQUEAR/DESBLOQUEAR */}
          <Popconfirm 
            title={r.activo ? "¿Bloquear acceso?" : "¿Activar acceso?"} 
            onConfirm={() => toggleStatus(r)}
            okText="Sí" cancelText="No"
          >
            <Button 
                type="default" 
                danger={r.activo} 
                style={!r.activo ? { borderColor: '#52c41a', color: '#52c41a' } : {}}
                icon={r.activo ? <StopOutlined /> : <CheckCircleOutlined />} 
                title={r.activo ? "Bloquear" : "Activar"} 
            />
          </Popconfirm>

          {/* Botón BORRAR (Solo si está bloqueado para evitar errores) */}
          {!r.activo && (
              <Popconfirm title="¿Eliminar permanentemente?" onConfirm={() => deleteUser(r.id)}>
                <Button danger icon={<DeleteOutlined />} title="Eliminar" />
              </Popconfirm>
          )}
        </Space>
    )}
  ];

  return (
    <div className="dashboard-content-wrapper">
       <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:'1.5rem' }}>
          <h1 className="page-title">Gestión de Usuarios</h1>
          <Button type="primary" icon={<PlusOutlined />} style={{ background: 'var(--color-principal)' }} onClick={() => openModal()}>
            Nuevo Usuario
          </Button>
       </div>
       
       <Card bordered={false} style={{ borderRadius: '0.5rem', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
          <Table columns={columns} dataSource={users} rowKey="id" loading={loading} pagination={{ pageSize: 8 }} />
       </Card>

       {/* MODAL DE CREAR/EDITAR */}
       <Modal title={editingUser ? "Editar Usuario" : "Nuevo Usuario"} open={isModalOpen} onOk={handleOk} onCancel={() => setIsModalOpen(false)} width={700}>
        <Form form={form} layout="vertical" style={{ marginTop: 20 }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
             <Form.Item name="username" label="Username" rules={[{ required: true }]}><Input /></Form.Item>
             <Form.Item name="perfil" label="Perfil" rules={[{ required: true }]}><Select onChange={setSelectedProfile}>{options.perfiles?.map(p => <Option key={p.id} value={p.id}>{p.nombre_perfil}</Option>)}</Select></Form.Item>
             <Form.Item name="nombre" label="Nombre" rules={[{ required: true }]}><Input /></Form.Item>
             <Form.Item name="apellido" label="Apellido" rules={[{ required: true }]}><Input /></Form.Item>
             <Form.Item name="email" label="Email" rules={[{ required: true, type: 'email' }]}><Input /></Form.Item>
             <Form.Item name="telefono" label="Teléfono" rules={[{ required: true }]}><Input prefix="+56 9" /></Form.Item>
          </div>
          {(selectedProfile === 3 || selectedProfile === 5) && <Form.Item name="departamento" label="Departamento" rules={[{ required: true }]}><Select>{options.departamentos?.map(d => <Option key={d.id} value={d.id}>{d.nombre_departamento}</Option>)}</Select></Form.Item>}
          {selectedProfile === 2 && <Form.Item name="direccion" label="Dirección" rules={[{ required: true }]}><Select>{options.direcciones?.map(d => <Option key={d.id_direccion} value={d.id_direccion}>{d.nombre_direccion}</Option>)}</Select></Form.Item>}
        </Form>
      </Modal>

      {/* MODAL DE VER DETALLE */}
      <Modal 
        title="Detalle del Funcionario" 
        open={isViewModalOpen} 
        onCancel={() => setIsViewModalOpen(false)} 
        footer={[<Button key="close" onClick={() => setIsViewModalOpen(false)}>Cerrar</Button>]}
        width={600}
      >
        {viewingUser && (
            <Descriptions bordered column={1} style={{ marginTop: 20 }}>
                <Descriptions.Item label="Nombre Completo">{viewingUser.nombre} {viewingUser.apellido}</Descriptions.Item>
                <Descriptions.Item label="Nombre de Usuario">{viewingUser.username}</Descriptions.Item>
                <Descriptions.Item label="Correo Electrónico">{viewingUser.email}</Descriptions.Item>
                <Descriptions.Item label="Teléfono">{viewingUser.telefono || 'No registrado'}</Descriptions.Item>
                <Descriptions.Item label="Perfil de Acceso"><Tag color="blue">{viewingUser.perfil_nombre}</Tag></Descriptions.Item>
                
                {viewingUser.departamento_nombre && (
                    <Descriptions.Item label="Departamento">{viewingUser.departamento_nombre}</Descriptions.Item>
                )}
                {viewingUser.direccion_nombre && (
                    <Descriptions.Item label="Dirección">{viewingUser.direccion_nombre}</Descriptions.Item>
                )}
                
                <Descriptions.Item label="Estado Actual">
                    <Tag color={viewingUser.activo ? 'green' : 'red'}>
                        {viewingUser.activo ? 'ACTIVO (Habilitado)' : 'BLOQUEADO (Deshabilitado)'}
                    </Tag>
                </Descriptions.Item>
            </Descriptions>
        )}
      </Modal>
    </div>
  );
};

// --- LAYOUT PRINCIPAL (Menú Limpio) ---
const AppLayout = () => {
  const location = useLocation();
  return (
    <Layout style={{ minHeight: '100vh' }} hasSider>
      <Sider 
        width={250} 
        style={{ 
            overflow: 'auto', height: '100vh', position: 'fixed', left: 0, top: 0, bottom: 0, 
            background: 'var(--color-secundario)', zIndex: 100 
        }}
      >
        <div style={{ height: 60, display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(255,255,255,0.1)', color: 'white', fontWeight: '900', fontSize: '1.2rem' }}>
            URBAN SENSOR
        </div>
        {/* Menú con solo Dashboard y Usuarios */}
        <Menu 
            theme="dark" 
            mode="inline" 
            selectedKeys={[location.pathname]} 
            style={{ background: 'var(--color-secundario)', border: 'none' }}
        >
          <Menu.Item key="/" icon={<DashboardOutlined />}><Link to="/">Dashboard</Link></Menu.Item>
          <Menu.Item key="/usuarios" icon={<TeamOutlined />}><Link to="/usuarios">Gestión de Usuarios</Link></Menu.Item>
          
          {/* Se eliminaron las opciones de Encuesta, Dirección, etc. y el botón Salir */}
        </Menu>
      </Sider>
      
      <Layout style={{ marginLeft: 250, background: 'var(--fondo-general)' }}>
        <Header style={{ 
            background: 'var(--fondo-general)', 
            padding: '0 2rem', 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'flex-end', 
            borderBottom: '1px solid var(--borde-suave)',
            height: '60px'
        }}>
           <Space>
              <Avatar style={{ backgroundColor: 'var(--color-principal)' }} icon={<UserOutlined />} />
              <Text strong style={{ color: 'var(--color-secundario)' }}>Administrador</Text>
           </Space>
        </Header>
        
        <Content style={{ margin: 0, overflow: 'initial' }}>
           <Routes>
             <Route path="/" element={<DashboardHome />} />
             <Route path="/usuarios" element={<UserManagement />} />
           </Routes>
        </Content>
      </Layout>
    </Layout>
  );
};

const App = () => <Router><AppLayout /></Router>;
export default App;