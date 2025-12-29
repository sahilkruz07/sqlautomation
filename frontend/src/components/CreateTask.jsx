import React, { useState } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';
import { Database, ArrowLeft, Send, CheckCircle2, AlertCircle, Code2 } from 'lucide-react';
import Editor from 'react-simple-code-editor';
import { highlight, languages } from 'prismjs/components/prism-core';
import 'prismjs/components/prism-sql';
import 'prismjs/themes/prism-tomorrow.css'; // Dark theme for editor

const API_BASE_URL = "http://localhost:8000/api/v1";

const CreateTask = ({ user, onBack, onSuccess }) => {
    const [formData, setFormData] = useState({
        task_description: '',
        db_name: '',
        sql_query: '',
        query_type: 'SELECT'
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
            const payload = {
                ...formData,
                created_by: user.name || user.email
            };
            const response = await axios.post(`${API_BASE_URL}/tasks`, payload);
            setMessage({ type: 'success', text: 'Task created successfully!' });

            // Redirect to details after short delay
            setTimeout(() => {
                onSuccess(response.data);
            }, 1000);
        } catch (error) {
            console.error("Error creating task:", error);
            setMessage({
                type: 'error',
                text: error.response?.data?.detail || 'Failed to create task. Please try again.'
            });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="create-task-view">
            <div className="view-header">
                <button className="back-btn glass" onClick={onBack}>
                    <ArrowLeft size={18} />
                    <span>Back to Dashboard</span>
                </button>
                <div className="view-title">
                    <h1>Create New Task</h1>
                    <p>Register a new SQL execution task in the system</p>
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
                                    placeholder="SELECT * FROM table WHERE column = 'value'..."
                                />
                            </div>
                            <p className="form-hint">Note: SQL query must start with the selected Query Type.</p>
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
                                    <Send size={18} />
                                    <span>Create Task</span>
                                </>
                            )}
                        </button>
                    </div>
                </form>
            </motion.div>
        </div>
    );
};

export default CreateTask;
