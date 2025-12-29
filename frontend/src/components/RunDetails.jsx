import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import {
    ArrowLeft,
    Terminal,
    Calendar,
    User,
    Globe,
    Code2,
    Copy,
    Clock,
    Activity,
    CheckCircle2,
    AlertCircle,
    CopyCheck,
    PlayCircle,
    Maximize2,
    X
} from 'lucide-react';
import { highlight, languages } from 'prismjs/components/prism-core';
import 'prismjs/components/prism-sql';
import 'prismjs/themes/prism-tomorrow.css';

const API_BASE_URL = "http://localhost:8000/api/v1";

const RunDetails = ({ runId, onBack }) => {
    const [run, setRun] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [copied, setCopied] = useState(false);
    const [showDataModal, setShowDataModal] = useState(false);

    useEffect(() => {
        const fetchRunDetails = async () => {
            try {
                const response = await axios.get(`${API_BASE_URL}/run/${runId}`);
                setRun(response.data);
            } catch (err) {
                console.error("Error fetching run details:", err);
                setError(err.response?.data?.detail || "Failed to load run details.");
            } finally {
                setLoading(false);
            }
        };

        if (runId) {
            fetchRunDetails();
        }
    }, [runId]);

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
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    if (loading) return (
        <div className="loader-container">
            <div className="loader"></div>
            <p>Fetching run history...</p>
        </div>
    );

    if (error) return (
        <div className="error-view glass">
            <AlertCircle size={48} color="#ef4444" />
            <h2>Error</h2>
            <p>{error}</p>
            <button className="back-btn glass" onClick={onBack}>
                <ArrowLeft size={18} />
                <span>Back to Dashboard</span>
            </button>
        </div>
    );

    if (!run) return null;

    return (
        <div className="task-details-view run-details-view">
            <div className="view-header">
                <button className="back-btn glass" onClick={onBack}>
                    <ArrowLeft size={18} />
                    <span>Back to Dashboard</span>
                </button>
                <div className="detail-title-section">
                    <div className="detail-id-badge run-id">
                        <Activity size={24} />
                        <span>{run.run_task_id}</span>
                    </div>
                    <div className="title-with-status">
                        <h1>{run.task_description || 'Execution History'}</h1>
                        <span className={`status-pill large ${run.status?.toLowerCase()}`}>
                            {run.status?.toUpperCase()}
                        </span>
                    </div>
                    <div className="header-actions">
                        <button
                            className="run-now-btn header-btn bg-gradient"
                            onClick={onBack}
                        >
                            <PlayCircle size={18} />
                            <span>Return to Task</span>
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
                    {run.sql_query && (
                        <div className="detail-section mb-2">
                            <div className="section-header">
                                <Code2 size={18} />
                                <span>Executed SQL</span>
                                <button className="copy-btn" onClick={() => copyToClipboard(run.sql_query)}>
                                    {copied ? <CopyCheck size={16} color="#10b981" /> : <Copy size={16} />}
                                </button>
                            </div>
                            <div className="query-display-wrapper">
                                <pre className="sql-code-display">
                                    <code
                                        dangerouslySetInnerHTML={{
                                            __html: highlight(run.sql_query, languages.sql)
                                        }}
                                    />
                                </pre>
                            </div>
                        </div>
                    )}

                    <div className="detail-section mb-2">
                        <div className="section-header">
                            <Activity size={18} />
                            <span>Execution Result</span>
                        </div>
                        <div className="run-result-box">
                            <p className="run-msg">{run.message}</p>

                            {run.data && run.data.length > 0 && (
                                <div className="result-data-preview-wrapper glass" onClick={() => setShowDataModal(true)}>
                                    <div className="preview-header">
                                        <span>Table Preview ({Math.min(run.data.length, 5)} of {run.data.length} rows)</span>
                                        <Maximize2 size={14} />
                                    </div>
                                    <div className="result-data-table-wrapper mini">
                                        <table className="result-data-table">
                                            <thead>
                                                <tr>
                                                    {Object.keys(run.data[0]).map(key => (
                                                        <th key={key}>{key}</th>
                                                    ))}
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {run.data.slice(0, 5).map((row, i) => (
                                                    <tr key={i}>
                                                        {Object.values(row).map((val, j) => (
                                                            <td key={j}>{String(val)}</td>
                                                        ))}
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                    {run.data.length > 5 && (
                                        <div className="preview-footer">
                                            Click to view all {run.data.length} rows
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    </div>

                    {run.rollback_query && (
                        <div className="detail-section rollback-highlight-section">
                            <div className="section-header">
                                <AlertCircle size={18} />
                                <span>Rollback Query</span>
                                <button className="copy-btn mini" onClick={() => copyToClipboard(run.rollback_query)}>
                                    <Copy size={14} />
                                </button>
                            </div>
                            <div className="rollback-code-box">
                                <pre className="sql-code-display mini">
                                    <code
                                        dangerouslySetInnerHTML={{
                                            __html: highlight(run.rollback_query, languages.sql)
                                        }}
                                    />
                                </pre>
                            </div>
                        </div>
                    )}
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="details-sidebar"
                >
                    <div className="sidebar-card glass info-card">
                        <h3>Execution Metadata</h3>
                        <div className="info-list">
                            <div className="info-item">
                                <div className="info-label">
                                    <Terminal size={16} />
                                    <span>Task ID</span>
                                </div>
                                <div className="info-value">{run.task_id}</div>
                            </div>
                            <div className="info-item">
                                <div className="info-label">
                                    <Globe size={16} />
                                    <span>Environment</span>
                                </div>
                                <div className={`status-badge ${run.environment?.toLowerCase()}`}>
                                    {run.environment}
                                </div>
                            </div>
                            <div className="info-item">
                                <div className="info-label">
                                    <User size={16} />
                                    <span>Executed By</span>
                                </div>
                                <div className="info-value">{run.created_by}</div>
                            </div>
                            <div className="info-item">
                                <div className="info-label">
                                    <Calendar size={16} />
                                    <span>Execution Date</span>
                                </div>
                                <div className="info-value">{formatDate(run.created_date)}</div>
                            </div>
                            <div className="info-item">
                                <div className="info-label">
                                    <Clock size={16} />
                                    <span>Execution Time</span>
                                </div>
                                <div className="info-value">{(run.execution_time_ms || 0).toFixed(2)} ms</div>
                            </div>
                        </div>
                    </div>
                </motion.div>
            </div>

            <AnimatePresence>
                {showDataModal && run?.data && (
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
                                    <span className="row-count">{run.data.length} rows returned</span>
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
                                                {Object.keys(run.data[0]).map(key => (
                                                    <th key={key}>{key}</th>
                                                ))}
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {run.data.map((row, i) => (
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

export default RunDetails;
