import React from 'react';
import { motion } from 'framer-motion';
import { GoogleLogin } from '@react-oauth/google';
import { Database } from 'lucide-react';

const LoginPage = ({ onLoginSuccess }) => (
    <div className="login-page">
        <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="login-card glass"
        >
            <div className="login-header">
                <div className="logo-icon bg-gradient">
                    <Database size={32} color="white" />
                </div>
                <h2>Welcome Back</h2>
                <p>Login to access your SQL dashboard</p>
            </div>

            <div className="google-btn-wrapper">
                <GoogleLogin
                    onSuccess={credentialResponse => {
                        onLoginSuccess(credentialResponse.credential);
                    }}
                    onError={() => {
                        console.log('Login Failed');
                    }}
                    useOneTap
                    theme="filled_black"
                    shape="pill"
                />
            </div>

            <div className="login-footer">
                <p>By continuing, you agree to our Terms and Privacy Policy</p>
            </div>
        </motion.div>
    </div>
);

export default LoginPage;
