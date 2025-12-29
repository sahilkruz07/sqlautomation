import React, { useState } from 'react';
import { GoogleOAuthProvider } from '@react-oauth/google';
import { jwtDecode } from 'jwt-decode';
import { motion, AnimatePresence } from 'framer-motion';

// Components
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import LoginPage from './components/LoginPage';
import Dashboard from './components/Dashboard';
import CreateTask from './components/CreateTask';
import EditTask from './components/EditTask';
import TaskDetails from './components/TaskDetails';
import RunDetails from './components/RunDetails';

import './App.css';

const GOOGLE_CLIENT_ID = "27073838006-qi8aeodmv5adnq5it0eajkomhtimb74n.apps.googleusercontent.com";

function App() {
  const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem('sql_auto_user');
    return savedUser ? JSON.parse(savedUser) : null;
  });
  const [loading, setLoading] = useState(false);
  const [showDashboard, setShowDashboard] = useState(() => {
    return localStorage.getItem('sql_auto_show_dashboard') === 'true';
  });
  const [currentView, setCurrentView] = useState('home'); // 'home', 'dashboard', 'create-task', 'task-details', 'edit-task', 'run-details'
  const [selectedTask, setSelectedTask] = useState(null);
  const [selectedRunId, setSelectedRunId] = useState(null);

  const handleLogin = (credential) => {
    setLoading(true);
    try {
      const decoded = jwtDecode(credential);
      setTimeout(() => {
        const userData = {
          name: decoded.name,
          email: decoded.email,
          picture: decoded.picture
        };
        setUser(userData);
        localStorage.setItem('sql_auto_user', JSON.stringify(userData));
        setLoading(false);
      }, 1000);
    } catch (error) {
      console.error("Login Error:", error);
      setLoading(false);
    }
  };

  const handleLogout = () => {
    setUser(null);
    setShowDashboard(false);
    localStorage.removeItem('sql_auto_user');
    localStorage.removeItem('sql_auto_show_dashboard');
  };

  const handleGetStarted = () => {
    setShowDashboard(true);
    localStorage.setItem('sql_auto_show_dashboard', 'true');
  };

  return (
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
      <div className="app-container">
        <AnimatePresence mode="wait">
          {!user ? (
            <motion.div
              key="login"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <LoginPage onLoginSuccess={handleLogin} />
            </motion.div>
          ) : (
            <motion.div
              key="home"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="main-view"
            >
              <Navbar
                user={user}
                onLogout={handleLogout}
                onCreateTask={() => setCurrentView('create-task')}
                onHome={() => setCurrentView(showDashboard ? 'dashboard' : 'home')}
              />
              <div className="container">
                {currentView === 'home' && !showDashboard && (
                  <Hero onGetStarted={() => {
                    handleGetStarted();
                    setCurrentView('dashboard');
                  }} />
                )}
                {(currentView === 'dashboard' || (currentView === 'home' && showDashboard)) && (
                  <Dashboard
                    onTaskClick={(task) => {
                      setSelectedTask(task);
                      setCurrentView('task-details');
                    }}
                    onRunClick={(run) => {
                      setSelectedRunId(run.run_task_id);
                      setCurrentView('run-details');
                    }}
                  />
                )}
                {currentView === 'create-task' && (
                  <CreateTask
                    user={user}
                    onBack={() => setCurrentView(showDashboard ? 'dashboard' : 'home')}
                    onSuccess={(newestTask) => {
                      setSelectedTask(newestTask);
                      setCurrentView('task-details');
                    }}
                  />
                )}
                {currentView === 'task-details' && (
                  <TaskDetails
                    task={selectedTask}
                    user={user}
                    onBack={() => setCurrentView('dashboard')}
                    onEditTask={(task) => {
                      setSelectedTask(task);
                      setCurrentView('edit-task');
                    }}
                    onRunTask={(task) => {
                      // Logic for running task from details can be added later
                      console.log("Running task:", task.task_id);
                    }}
                  />
                )}
                {currentView === 'edit-task' && (
                  <EditTask
                    task={selectedTask}
                    onBack={() => setCurrentView('task-details')}
                    onSuccess={(updatedTask) => {
                      setSelectedTask(updatedTask);
                      setCurrentView('task-details');
                    }}
                  />
                )}
                {currentView === 'run-details' && (
                  <RunDetails
                    runId={selectedRunId}
                    onBack={() => setCurrentView('dashboard')}
                  />
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {loading && (
          <div className="loader-overlay">
            <div className="loader"></div>
          </div>
        )}
      </div>
    </GoogleOAuthProvider>
  );
}

export default App;
