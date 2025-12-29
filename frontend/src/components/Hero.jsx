import React from 'react';
import { motion } from 'framer-motion';
import {
    Sparkles,
    ChevronRight,
    Terminal,
    Layers,
    ShieldCheck,
    Zap
} from 'lucide-react';

const Hero = ({ onGetStarted }) => (
    <section className="hero-section">
        <div className="hero-glow" style={{ top: '-10%', left: '10%' }}></div>
        <div className="hero-glow" style={{ bottom: '-10%', right: '10%', background: 'radial-gradient(circle, rgba(236, 72, 153, 0.1) 0%, transparent 70%)' }}></div>

        <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="hero-content"
        >
            <div className="badge glass">
                <Sparkles size={14} className="text-gradient" />
                <span>Next Gen SQL Management</span>
            </div>

            <h1 className="hero-title">
                Streamline your <span className="text-gradient">SQL Operations</span> <br />
                with Ultimate Ease
            </h1>

            <p className="hero-subtitle">
                Your unified platform for Easy SQL Operations and Secured Logins.
                Experience the safety of Easy Rollbacks and the clarity of Standardized Reports
                designed for modern engineering excellence.
            </p>

            <div className="hero-btns">
                <button
                    className="btn-primary bg-gradient shadow-glow"
                    onClick={onGetStarted}
                >
                    Get Started <ChevronRight size={18} />
                </button>
                <button className="btn-secondary glass">
                    <Terminal size={18} /> View Docs
                </button>
            </div>
        </motion.div>

        <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 1, delay: 0.2 }}
            className="hero-assets"
        >
            <div className="asset-card glass floating" style={{ animationDelay: '0s' }}>
                <Layers className="text-gradient" size={32} />
                <h3>Data Analysis</h3>
                <p>Real-time insights</p>
            </div>
            <div className="asset-card glass floating" style={{ animationDelay: '1s', top: '200px', right: '-40px' }}>
                <ShieldCheck className="text-gradient" size={32} />
                <h3>Secure Login</h3>
                <p>Google SSL Auth</p>
            </div>
            <div className="asset-card glass floating" style={{ animationDelay: '2s', bottom: '50px', left: '-30px' }}>
                <Zap className="text-gradient" size={32} />
                <h3>Fast Exec</h3>
                <p>Optimized queries</p>
            </div>
        </motion.div>
    </section>
);

export default Hero;
