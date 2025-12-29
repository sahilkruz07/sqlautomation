import React from 'react';
import { Database, LogOut, Plus } from 'lucide-react';

const Navbar = ({ user, onLogout, onCreateTask, onHome }) => (
    <nav className="navbar glass">
        <div className="nav-container">
            <div className="logo-section" onClick={onHome} style={{ cursor: 'pointer' }}>
                <div className="logo-icon bg-gradient">
                    <Database size={24} color="white" />
                </div>
                <span className="logo-text">SQL<span className="text-gradient">Automate</span></span>
            </div>

            <div className="nav-actions">
                {user ? (
                    <>
                        <button className="create-task-btn bg-gradient" onClick={onCreateTask}>
                            <Plus size={18} />
                            <span>Create Task</span>
                        </button>
                        <div className="user-profile">
                            <span className="user-name">{user.name}</span>
                            <button onClick={onLogout} className="logout-btn">
                                <LogOut size={18} />
                            </button>
                        </div>
                    </>
                ) : (
                    <button className="login-trigger-btn glass">Sign In</button>
                )}
            </div>
        </div>
    </nav>
);

export default Navbar;
