import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';
import {
    Database,
    History,
    ChevronLeft,
    ChevronRight,
    Search,
    RefreshCw,
    Terminal,
    Clock,
    User,
    Globe,
    Tag,
    Code
} from 'lucide-react';

const API_BASE_URL = "http://localhost:8000/api/v1";

const Dashboard = ({ onTaskClick, onRunClick }) => {
    const [activeTab, setActiveTab] = useState(() => {
        return localStorage.getItem('sql_auto_active_tab') || 'tasks';
    });
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [page, setPage] = useState(0);
    const [limit] = useState(10);
    const [searchQuery, setSearchQuery] = useState('');

    // Column width states
    const [taskWidths, setTaskWidths] = useState([150, 340, 150, 220, 180]);
    const [historyWidths, setHistoryWidths] = useState([150, 150, 150, 120, 250, 230]);
    const [resizing, setResizing] = useState(null);

    const fetchData = async () => {
        setLoading(true);
        try {
            const endpoint = activeTab === 'tasks' ? '/tasks' : '/run';
            const response = await axios.get(`${API_BASE_URL}${endpoint}`, {
                params: {
                    skip: (page || 0) * limit,
                    limit: limit,
                    search: searchQuery || undefined
                }
            });
            setData(response.data);
        } catch (error) {
            console.error(`Error fetching ${activeTab}:`, error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, [activeTab, page, searchQuery]);

    const handleTabChange = (tab) => {
        setData([]); // Clear previous data to prevent template/data mismatch
        setActiveTab(tab);
        localStorage.setItem('sql_auto_active_tab', tab);
        setPage(0);
        setSearchQuery('');
    };

    const handleResizeStart = (index, event) => {
        setResizing({
            index,
            startX: event.clientX,
            startWidth: activeTab === 'tasks' ? taskWidths[index] : historyWidths[index]
        });
    };

    useEffect(() => {
        const handleMouseMove = (e) => {
            if (resizing !== null) {
                const diff = e.clientX - resizing.startX;
                const newWidth = Math.max(50, resizing.startWidth + diff);

                if (activeTab === 'tasks') {
                    const newWidths = [...taskWidths];
                    newWidths[resizing.index] = newWidth;
                    setTaskWidths(newWidths);
                } else {
                    const newWidths = [...historyWidths];
                    newWidths[resizing.index] = newWidth;
                    setHistoryWidths(newWidths);
                }
            }
        };

        const handleMouseUp = () => {
            setResizing(null);
        };

        if (resizing !== null) {
            window.addEventListener('mousemove', handleMouseMove);
            window.addEventListener('mouseup', handleMouseUp);
        }

        return () => {
            window.removeEventListener('mousemove', handleMouseMove);
            window.removeEventListener('mouseup', handleMouseUp);
        };
    }, [resizing, activeTab, taskWidths, historyWidths]);

    // Data is now filtered server-side
    const displayData = data;

    const formatDate = (dateString) => {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleString('en-IN', {
            timeZone: 'Asia/Kolkata',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            hour12: true
        });
    };

    const renderHeaders = () => {
        const headers = activeTab === 'tasks'
            ? ['Task ID', 'Description', 'Query Type', 'Created By', 'Created At']
            : ['Run ID', 'Task ID', 'Environment', 'Status', 'Executed By', 'Created At'];

        const currentWidths = activeTab === 'tasks' ? taskWidths : historyWidths;

        return (
            <thead>
                <tr>
                    {headers.map((header, idx) => (
                        <th key={idx} style={{ width: currentWidths[idx] }}>
                            {header}
                            <div
                                className={`resizer ${resizing?.index === idx ? 'resizing' : ''}`}
                                onMouseDown={(e) => handleResizeStart(idx, e)}
                            />
                        </th>
                    ))}
                </tr>
            </thead>
        );
    };

    return (
        <div className="dashboard-container">
            <div className="dashboard-header glass">
                <div className="tab-group">
                    <button
                        className={`tab-btn ${activeTab === 'tasks' ? 'active' : ''}`}
                        onClick={() => handleTabChange('tasks')}
                    >
                        <Database size={18} />
                        <span>Tasks</span>
                    </button>
                    <button
                        className={`tab-btn ${activeTab === 'history' ? 'active' : ''}`}
                        onClick={() => handleTabChange('history')}
                    >
                        <History size={18} />
                        <span>Run History</span>
                    </button>
                </div>

                <div className="search-wrapper glass">
                    <Search size={18} className="search-icon" />
                    <input
                        type="text"
                        placeholder={`Search ${activeTab}...`}
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                    />
                </div>

                <div className="dashboard-actions">
                    <button className="refresh-btn glass" onClick={fetchData}>
                        <RefreshCw size={18} className={loading ? 'spin' : ''} />
                    </button>
                </div>
            </div>

            <div className="dashboard-content">
                <motion.div
                    key={activeTab}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="data-table-wrapper glass"
                >
                    {loading ? (
                        <div className="table-loader">
                            <div className="loader"></div>
                            <span>Fetching {activeTab}...</span>
                        </div>
                    ) : displayData.length === 0 ? (
                        <div className="empty-state">
                            <Search size={48} className="text-secondary" />
                            <p>{searchQuery ? 'No results found for your search' : `No ${activeTab} found`}</p>
                        </div>
                    ) : (
                        <table className="data-table">
                            {renderHeaders()}
                            <tbody>
                                {displayData.map((item, idx) => (
                                    <tr
                                        key={idx}
                                        onClick={() => activeTab === 'tasks' ? onTaskClick(item) : onRunClick(item)}
                                        style={{ cursor: 'pointer' }}
                                    >
                                        {activeTab === 'tasks' ? (
                                            <>
                                                <td>
                                                    <div className="id-cell">
                                                        <Terminal size={14} />
                                                        <span>{item.task_id}</span>
                                                    </div>
                                                </td>
                                                <td>
                                                    <div className="desc-cell-wrapper">
                                                        <Code size={14} />
                                                        <span className="desc-text">{item.task_description}</span>
                                                    </div>
                                                </td>
                                                <td>
                                                    <div className="type-badge-wrapper">
                                                        <span className={`type-badge ${item.query_type?.toLowerCase() || ''}`}>
                                                            <Tag size={14} />
                                                            {item.query_type}
                                                        </span>
                                                    </div>
                                                </td>

                                                <td>
                                                    <div className="user-cell">
                                                        <User size={14} />
                                                        <span>{item.created_by || 'Unknown'}</span>
                                                    </div>
                                                </td>
                                                <td>
                                                    <div className="date-cell">
                                                        <Clock size={14} />
                                                        <span>{formatDate(item.created_date)}</span>
                                                    </div>
                                                </td>
                                            </>
                                        ) : (
                                            <>
                                                <td>
                                                    <div className="id-cell">
                                                        <Clock size={14} />
                                                        <span>{item.run_task_id || 'N/A'}</span>
                                                    </div>
                                                </td>
                                                <td>
                                                    <div className="task-id-cell">
                                                        <Terminal size={14} />
                                                        <span>{item.task_id}</span>
                                                    </div>
                                                </td>
                                                <td>
                                                    <div className="env-cell">
                                                        <Globe size={14} />
                                                        <span>{item.environment}</span>
                                                    </div>
                                                </td>
                                                <td>
                                                    <div className="status-pill-wrapper">
                                                        <span className={`status-pill ${item.status?.toLowerCase() || ''}`}>
                                                            {item.status}
                                                        </span>
                                                    </div>
                                                </td>
                                                <td>
                                                    <div className="user-cell">
                                                        <User size={14} />
                                                        <span>{item.created_by || 'Unknown'}</span>
                                                    </div>
                                                </td>
                                                <td>
                                                    <div className="date-cell">
                                                        <Clock size={14} />
                                                        <span>{formatDate(item.created_date)}</span>
                                                    </div>
                                                </td>
                                            </>
                                        )}
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </motion.div>

                <div className="pagination">
                    <button
                        className="pag-btn glass"
                        disabled={page === 0}
                        onClick={() => setPage(p => p - 1)}
                    >
                        <ChevronLeft size={20} />
                    </button>
                    <span className="page-info">Page {page + 1}</span>
                    <button
                        className="pag-btn glass"
                        disabled={data.length < limit}
                        onClick={() => setPage(p => p + 1)}
                    >
                        <ChevronRight size={20} />
                    </button>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
