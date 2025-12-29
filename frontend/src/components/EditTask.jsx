import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';
import { Database, ArrowLeft, Send, CheckCircle2, AlertCircle, Code2, Save } from 'lucide-react';
import Editor from 'react-simple-code-editor';
import { highlight, languages } from 'prismjs/components/prism-core';
import 'prismjs/components/prism-sql';
import 'prismjs/themes/prism-tomorrow.css';

const API_BASE_URL = "http://localhost:8000/api/v1";

const EditTask = ({ task, onBack, onSuccess }) => {
    const [formData, setFormData] = useState({
        task_description: task?.task_description || '',
        db_name: task?.db_name || '',
        sql_query: task?.sql_query || '',
        query_type: task?.query_type || 'SELECT'
    });
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState(null);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setMessage(null);

        try {
            const response = await axios.put(`${API_BASE_URL}/tasks/${task.task_id}`, formData);
            setMessage({ type: 'success', text: 'Task updated successfully!' });

            setTimeout(() => {
                onSuccess(response.data);
            }, 1000);
        } catch (error) {
            console.error("Error updating task:", error);
            setMessage({
                type: 'error',
                text: error.response?.data?.detail || 'Failed to update task. Please try again.'
            });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="create-task-view edit-task-view">
            <div className="view-header">
                <button className="back-btn glass" onClick={onBack}>
                    <ArrowLeft size={18} />
                    <span>Back to Details</span>
                </button>
                <div className="view-title">
                    <div className="detail-id-badge" style={{ marginBottom: '1rem' }}>
                        <span>{task.task_id}</span>
                    </div>
                    <h1>Edit Task</h1>
                    <p>Modify the existing SQL task configuration</p>
                </div>
            </div>

            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="form-card glass"
            >
                <form onSubmit={handleSubmit}>
                    <div className="form-grid">
                        <div className="form-group full-width">
                            <label>Task Description</label>
                            <input
                                type="text"
                                name="task_description"
                                value={formData.task_description}
                                onChange={handleChange}
                                placeholder="What does this task do?"
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label>Database Name</label>
                            <input
                                type="text"
                                name="db_name"
                                value={formData.db_name}
                                onChange={handleChange}
                                placeholder="e.g. sales_prod"
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label>Query Type</label>
                            <div className="query-type-selector">
                                {['SELECT', 'INSERT', 'UPDATE', 'DELETE'].map((type) => (
                                    <div
                                        key={type}
                                        className={`type-option ${formData.query_type === type ? `active ${type.toLowerCase()}` : ''}`}
                                        onClick={() => setFormData(prev => ({ ...prev, query_type: type }))}
                                    >
                                        {type}
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="form-group full-width">
                            <label>SQL Query</label>
                            <div className="code-editor-wrapper">
                                <div className="editor-toolbar">
                                    <Code2 size={14} />
                                    <span>SQL Editor</span>
                                </div>
                                <Editor
                                    value={formData.sql_query}
                                    onValueChange={code => setFormData(prev => ({ ...prev, sql_query: code }))}
                                    highlight={code => highlight(code, languages.sql)}
                                    padding={20}
                                    className="sql-code-editor"
                                    style={{
                                        fontFamily: '"JetBrains Mono", "Fira Code", monospace',
                                        fontSize: 14,
                                        minHeight: '250px',
                                    }}
                                />
                            </div>
                        </div>
                    </div>

                    {message && (
                        <div className={`form-message ${message.type}`}>
                            {message.type === 'success' ? <CheckCircle2 size={18} /> : <AlertCircle size={18} />}
                            <span>{message.text}</span>
                        </div>
                    )}

                    <div className="form-actions">
                        <button
                            type="submit"
                            className="submit-btn bg-gradient"
                            disabled={loading}
                        >
                            {loading ? (
                                <div className="loader-small"></div>
                            ) : (
                                <>
                                    <Save size={18} />
                                    <span>Save Changes</span>
                                </>
                            )}
                        </button>
                    </div>
                </form>
            </motion.div>
        </div>
    );
};

export default EditTask;
