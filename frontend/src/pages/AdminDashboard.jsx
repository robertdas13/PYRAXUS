import React, { useState, useEffect } from 'react';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { useToast } from '../hooks/use-toast';
import { Lock, Mail, Calendar, Trash2, Check, Eye, Filter, LogOut, Phone } from 'lucide-react';
import axios from 'axios';
import '../styles/admin.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AdminDashboard = () => {
  const { toast } = useToast();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [password, setPassword] = useState('');
  const [isLoggingIn, setIsLoggingIn] = useState(false);
  const [contacts, setContacts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filterStatus, setFilterStatus] = useState('all');
  const [adminPassword, setAdminPassword] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    setIsLoggingIn(true);

    try {
      const response = await axios.post(
        `${API}/admin/login`,
        {},
        {
          headers: {
            'X-Admin-Password': password
          }
        }
      );

      if (response.data.success) {
        setIsAuthenticated(true);
        setAdminPassword(password);
        toast({
          title: "Login Successful",
          description: "Welcome to PYRAXUS Admin Dashboard"
        });
        fetchContacts(password);
      }
    } catch (error) {
      toast({
        title: "Login Failed",
        description: "Invalid admin password",
        variant: "destructive"
      });
    } finally {
      setIsLoggingIn(false);
    }
  };

  const fetchContacts = async (pwd = adminPassword, status = null) => {
    setLoading(true);
    try {
      const url = status && status !== 'all' ? `${API}/admin/contacts?status=${status}` : `${API}/admin/contacts`;
      const response = await axios.get(url, {
        headers: {
          'X-Admin-Password': pwd
        }
      });

      if (response.data.success) {
        setContacts(response.data.data);
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to fetch contacts",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const updateStatus = async (contactId, newStatus) => {
    try {
      const response = await axios.patch(
        `${API}/admin/contacts/${contactId}/status`,
        { status: newStatus },
        {
          headers: {
            'X-Admin-Password': adminPassword
          }
        }
      );

      if (response.data.success) {
        toast({
          title: "Status Updated",
          description: response.data.message
        });
        fetchContacts();
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update status",
        variant: "destructive"
      });
    }
  };

  const deleteContact = async (contactId) => {
    if (!window.confirm('Are you sure you want to delete this contact message?')) {
      return;
    }

    try {
      const response = await axios.delete(
        `${API}/admin/contacts/${contactId}`,
        {
          headers: {
            'X-Admin-Password': adminPassword
          }
        }
      );

      if (response.data.success) {
        toast({
          title: "Contact Deleted",
          description: response.data.message
        });
        fetchContacts();
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete contact",
        variant: "destructive"
      });
    }
  };

  const handleFilterChange = (status) => {
    setFilterStatus(status);
    if (isAuthenticated) {
      fetchContacts(adminPassword, status);
    }
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setPassword('');
    setAdminPassword('');
    setContacts([]);
    toast({
      title: "Logged Out",
      description: "You have been logged out successfully"
    });
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'new': return 'status-new';
      case 'read': return 'status-read';
      case 'replied': return 'status-replied';
      default: return 'status-new';
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="admin-login-container">
        <Card className="admin-login-card">
          <div className="admin-login-header">
            <Lock size={48} className="admin-lock-icon" />
            <h1 className="admin-login-title">PYRAXUS Admin</h1>
            <p className="admin-login-subtitle">Dashboard Login</p>
          </div>

          <form onSubmit={handleLogin} className="admin-login-form">
            <div className="form-group">
              <label htmlFor="password" className="form-label">Admin Password</label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter admin password"
                required
                className="admin-input"
              />
            </div>
            <Button
              type="submit"
              disabled={isLoggingIn}
              className="admin-login-btn"
            >
              {isLoggingIn ? 'Logging in...' : 'Login'}
              <Lock className="ml-2" size={18} />
            </Button>
          </form>
        </Card>
      </div>
    );
  }

  return (
    <div className="admin-dashboard">
      <div className="admin-header">
        <div className="admin-header-content">
          <h1 className="admin-title">PYRAXUS Admin Dashboard</h1>
          <p className="admin-subtitle">Manage your contact messages</p>
        </div>
        <Button onClick={handleLogout} variant="outline" className="logout-btn">
          <LogOut size={18} className="mr-2" />
          Logout
        </Button>
      </div>

      <div className="admin-filters">
        <div className="filter-label">
          <Filter size={20} />
          <span>Filter by Status:</span>
        </div>
        <div className="filter-buttons">
          <Button
            onClick={() => handleFilterChange('all')}
            variant={filterStatus === 'all' ? 'default' : 'outline'}
            className="filter-btn"
          >
            All
          </Button>
          <Button
            onClick={() => handleFilterChange('new')}
            variant={filterStatus === 'new' ? 'default' : 'outline'}
            className="filter-btn"
          >
            New
          </Button>
          <Button
            onClick={() => handleFilterChange('read')}
            variant={filterStatus === 'read' ? 'default' : 'outline'}
            className="filter-btn"
          >
            Read
          </Button>
          <Button
            onClick={() => handleFilterChange('replied')}
            variant={filterStatus === 'replied' ? 'default' : 'outline'}
            className="filter-btn"
          >
            Replied
          </Button>
        </div>
      </div>

      <div className="admin-content">
        {loading ? (
          <div className="admin-loading">Loading contacts...</div>
        ) : contacts.length === 0 ? (
          <Card className="admin-empty">
            <Mail size={48} className="empty-icon" />
            <p className="empty-text">No contact messages yet</p>
          </Card>
        ) : (
          <div className="contacts-grid">
            {contacts.map((contact) => (
              <Card key={contact.id} className="contact-card">
                <div className="contact-card-header">
                  <div className="contact-info">
                    <h3 className="contact-name">{contact.name}</h3>
                    <a href={`tel:${contact.phone}`} className="contact-email">
                      <Phone size={14} />
                      {contact.phone}
                    </a>
                    <a href={`mailto:${contact.email}`} className="contact-email">
                      <Mail size={14} />
                      {contact.email}
                    </a>
                  </div>
                  <span className={`contact-status ${getStatusColor(contact.status)}`}>
                    {contact.status}
                  </span>
                </div>

                <div className="contact-message">
                  <p>{contact.message}</p>
                </div>

                <div className="contact-footer">
                  <div className="contact-date">
                    <Calendar size={14} />
                    <span>{formatDate(contact.createdAt)}</span>
                  </div>

                  <div className="contact-actions">
                    {contact.status === 'new' && (
                      <Button
                        size="sm"
                        onClick={() => updateStatus(contact.id, 'read')}
                        className="action-btn read-btn"
                      >
                        <Eye size={14} />
                        Mark Read
                      </Button>
                    )}
                    {contact.status === 'read' && (
                      <Button
                        size="sm"
                        onClick={() => updateStatus(contact.id, 'replied')}
                        className="action-btn replied-btn"
                      >
                        <Check size={14} />
                        Mark Replied
                      </Button>
                    )}
                    <Button
                      size="sm"
                      variant="destructive"
                      onClick={() => deleteContact(contact.id)}
                      className="action-btn delete-btn"
                    >
                      <Trash2 size={14} />
                      Delete
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminDashboard;
