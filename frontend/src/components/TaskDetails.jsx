import React, { useState } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import {
    ArrowLeft,
    Terminal,
    Calendar,
    User,
    Database,
    Tag,
    Clock,
    Code2,
    Copy,
    PlayCircle,
    Edit2,
    Globe,
    AlertCircle,
    Maximize2,
    X
} from 'lucide-react';
import { highlight, languages } from 'prismjs/components/prism-core';
import 'prismjs/components/prism-sql';
import 'prismjs/themes/prism-tomorrow.css';

const API_BASE_URL = "http://localhost:8000/api/v1";

const TaskDetails = ({ task, onBack, onRunTask, onEditTask, user }) => {
    const [isRunning, setIsRunning] = useState(false);
    const [runResult, setRunResult] = useState(null);
    const [error, setError] = useState(null);
    const [showEnvModal, setShowEnvModal] = useState(false);
    const [showDataModal, setShowDataModal] = useState(false);

    if (!task) return null;

    const formatDate = (dateString) => {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleString('en-IN', {
            timeZone: 'Asia/Kolkata',
            month: 'long',
            day: 'numeric',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            hour12: true
        });
    };

    const copyToClipboard = (text) => {
        navigator.clipboard.writeText(text);
    };

    const handleRunTask = async (env) => {
        setIsRunning(true);
        setRunResult(null);
        setError(null);
        setShowEnvModal(false);

        try {
            const payload = {
                task_id: task.task_id,
                environment: env,
                created_by: user?.name || user?.email || 'System'
            };
            const response = await axios.post(`${API_BASE_URL}/run`, payload);
            setRunResult(response.data);
            if (onRunTask) onRunTask(response.data);
        } catch (err) {
            console.error("Error executing task:", err);
            setError(err.response?.data?.detail || "An error occurred during execution.");
        } finally {
            setIsRunning(false);
        }
    };

    return (
        <div className="task-details-view">
            <div className="view-header">
                <button className="back-btn glass" onClick={onBack}>
                    <ArrowLeft size={18} />
                    <span>Back to Dashboard</span>
                </button>
                <div className="detail-title-section">
                    <div className="detail-id-badge">
                        <Terminal size={24} />
                        <span>{task.task_id}</span>
                    </div>
                    <h1>{task.task_description}</h1>
                    <div className="header-actions">
                        <button className="edit-task-btn glass" onClick={() => onEditTask(task)}>
                            <Edit2 size={18} />
                            <span>Edit Task</span>
                        </button>
                        <button
                            className="run-now-btn header-btn bg-gradient"
                            onClick={() => setShowEnvModal(true)}
                            disabled={isRunning}
                        >
                            {isRunning ? (
                                <div className="loader-small"></div>
                            ) : (
                                <>
                                    <PlayCircle size={18} />
                                    <span>Run Task Now</span>
                                </>
                            )}
                        </button>
                    </div>
                </div>
            </div>

            <div className="details-grid">
                <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="details-main glass"
                >
                    <div className="detail-section">
                        <div className="section-header">
                            <Code2 size={18} />
                            <span>SQL Query</span>
                            <button className="copy-btn" onClick={() => copyToClipboard(task.sql_query)}>
                                <Copy size={16} />
                            </button>
                        </div>
                        <div className="query-display-wrapper">
                            <pre className="sql-code-display">
                                <code
                                    dangerouslySetInnerHTML={{
                                        __html: highlight(task.sql_query, languages.sql)
                                    }}
                                />
                            </pre>
                        </div>
                    </div>

                    <AnimatePresence>
                        {(runResult || error) && (
                            <motion.div
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -20 }}
                                className="run-result-section"
                            >
                                <div className="section-header">
                                    <Terminal size={18} />
                                    <span>Execution Results</span>
                                    <button className="close-result-btn" onClick={() => { setRunResult(null); setError(null); }}>×</button>
                                </div>
                                {error ? (
                                    <div className="run-error glass">
                                        <AlertCircle size={20} />
                                        <p>{error}</p>
                                    </div>
                                ) : (
                                    <div className="run-success glass">
                                        <div className="success-header">
                                            <div className={`status-badge ${runResult.status.toLowerCase()}`}>
                                                {runResult.status}
                                            </div>
                                            <div className="run-id-text">Run ID: {runResult.run_task_id}</div>
                                            <div className="exec-time">{runResult.execution_time_ms}ms</div>
                                        </div>
                                        <p className="run-msg">{runResult.message}</p>

                                        {runResult.data && runResult.data.length > 0 && (
                                            <div className="result-data-preview-wrapper glass" onClick={() => setShowDataModal(true)}>
                                                <div className="preview-header">
                                                    <span>Table Preview ({Math.min(runResult.data.length, 5)} of {runResult.data.length} rows)</span>
                                                    <Maximize2 size={14} />
                                                </div>
                                                <div className="result-data-table-wrapper mini">
                                                    <table className="result-data-table">
                                                        <thead>
                                                            <tr>
                                                                {Object.keys(runResult.data[0]).map(key => (
                                                                    <th key={key}>{key}</th>
                                                                ))}
                                                            </tr>
                                                        </thead>
                                                        <tbody>
                                                            {runResult.data.slice(0, 5).map((row, i) => (
                                                                <tr key={i}>
                                                                    {Object.values(row).map((val, j) => (
                                                                        <td key={j}>{String(val)}</td>
                                                                    ))}
                                                                </tr>
                                                            ))}
                                                        </tbody>
                                                    </table>
                                                </div>
                                                {runResult.data.length > 5 && (
                                                    <div className="preview-footer">
                                                        Click to view all {runResult.data.length} rows
                                                    </div>
                                                )}
                                            </div>
                                        )}

                                        {runResult.rollback_query && (
                                            <div className="rollback-section">
                                                <div className="rollback-label">Generated Rollback Query:</div>
                                                <div className="rollback-code glass">
                                                    <pre className="sql-code-display mini">
                                                        <code
                                                            dangerouslySetInnerHTML={{
                                                                __html: highlight(runResult.rollback_query, languages.sql)
                                                            }}
                                                        />
                                                    </pre>
                                                    <button className="copy-btn mini" onClick={() => copyToClipboard(runResult.rollback_query)}>
                                                        <Copy size={14} />
                                                    </button>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                )}
                            </motion.div>
                        )}
                    </AnimatePresence>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="details-sidebar"
                >
                    <div className="sidebar-card glass info-card">
                        <h3>Task Information</h3>
                        <div className="info-list">
                            <div className="info-item">
                                <div className="info-label">
                                    <Tag size={16} />
                                    <span>Query Type</span>
                                </div>
                                <div className={`type-badge ${task.query_type?.toLowerCase()}`}>
                                    {task.query_type}
                                </div>
                            </div>
                            <div className="info-item">
                                <div className="info-label">
                                    <Database size={16} />
                                    <span>Database</span>
                                </div>
                                <div className="info-value">{task.db_name}</div>
                            </div>
                            <div className="info-item">
                                <div className="info-label">
                                    <User size={16} />
                                    <span>Created By</span>
                                </div>
                                <div className="info-value">{task.created_by}</div>
                            </div>
                            <div className="info-item">
                                <div className="info-label">
                                    <Calendar size={16} />
                                    <span>Created On</span>
                                </div>
                                <div className="info-value">{formatDate(task.created_date)}</div>
                            </div>
                            {task.updated_date && (
                                <div className="info-item">
                                    <div className="info-label">
                                        <Clock size={16} />
                                        <span>Last Updated</span>
                                    </div>
                                    <div className="info-value">{formatDate(task.updated_date)}</div>
                                </div>
                            )}

                        </div>
                    </div>
                </motion.div>
            </div>

            <AnimatePresence>
                {showEnvModal && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="modal-overlay"
                        onClick={() => setShowEnvModal(false)}
                    >
                        <motion.div
                            initial={{ scale: 0.9, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.9, opacity: 0 }}
                            className="env-modal glass"
                            onClick={e => e.stopPropagation()}
                        >
                            <h3>Select Environment</h3>
                            <p>Choose the target environment to execute this query:</p>
                            <div className="env-options">
                                {['QA', 'PREPROD', 'PROD'].map(env => (
                                    <button
                                        key={env}
                                        className="env-btn glass"
                                        onClick={() => handleRunTask(env)}
                                    >
                                        <Globe size={18} />
                                        <span>{env}</span>
                                    </button>
                                ))}
                            </div>
                            <button className="cancel-btn" onClick={() => setShowEnvModal(false)}>Cancel</button>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>

            <AnimatePresence>
                {showDataModal && runResult?.data && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="modal-overlay"
                        style={{ zIndex: 1100 }}
                        onClick={() => setShowDataModal(false)}
                    >
                        <motion.div
                            initial={{ scale: 0.9, opacity: 0, y: 20 }}
                            animate={{ scale: 1, opacity: 1, y: 0 }}
                            exit={{ scale: 0.9, opacity: 0, y: 20 }}
                            className="full-data-modal glass"
                            onClick={e => e.stopPropagation()}
                        >
                            <div className="modal-header">
                                <div className="header-info">
                                    <h3>Execution Results</h3>
                                    <span className="row-count">{runResult.data.length} rows returned</span>
                                </div>
                                <button className="close-modal-btn" onClick={() => setShowDataModal(false)}>
                                    <X size={20} />
                                </button>
                            </div>
                            <div className="modal-content">
                                <div className="result-data-table-wrapper large">
                                    <table className="result-data-table">
                                        <thead>
                                            <tr>
                                                {Object.keys(runResult.data[0]).map(key => (
                                                    <th key={key}>{key}</th>
                                                ))}
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {runResult.data.map((row, i) => (
                                                <tr key={i}>
                                                    {Object.values(row).map((val, j) => (
                                                        <td key={j}>{String(val)}</td>
                                                    ))}
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

export default TaskDetails;
