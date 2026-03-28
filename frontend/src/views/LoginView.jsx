import { useState } from 'react';
import { Mail, Lock } from 'lucide-react';
import { loginUser, registerUser } from '../lib/api';

export default function LoginView({ onLoginSuccess }) {
  const [mode, setMode] = useState('login');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setIsSubmitting(true);

    if (mode === 'register' && password !== confirmPassword) {
      setError('Passwords do not match.');
      setIsSubmitting(false);
      return;
    }

    try {
      const payload = { username: username.trim(), password };
      const response = mode === 'register'
        ? await registerUser(payload)
        : await loginUser(payload);

      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('token_type', response.token_type);
      localStorage.setItem('current_user', JSON.stringify(response.user));
      onLoginSuccess(response.user);
    } catch (requestError) {
      setError(requestError.message || 'Unable to authenticate. Please try again.');
      setIsSubmitting(false);
    }
  };

  const switchMode = (nextMode) => {
    setMode(nextMode);
    setError('');
    setConfirmPassword('');
  };

  return (
    <div className="login-shell">
      <div className="login-watermark" aria-hidden="true">KHARCHA</div>

      <main className="login-main">
        <div className="login-branding">
          <h1 className="login-brand">Obsidian</h1>
          <p className="login-tagline">Architectural Wealth Intelligence</p>
        </div>

        <section className="login-card" aria-label="Sign in panel">
          <header className="login-card-header">
            <h2>{mode === 'login' ? 'Welcome Back' : 'Create Account'}</h2>
            <p>
              {mode === 'login'
                ? 'Enter your credentials to access the vault.'
                : 'Register a new account to begin managing your finances.'}
            </p>
          </header>

          <form className="login-form" onSubmit={handleSubmit}>
            <div className="login-field">
              <label htmlFor="username">Username</label>
              <div className="login-input-wrap">
                <Mail size={16} />
                <input
                  id="username"
                  name="username"
                  type="text"
                  placeholder="Enter username"
                  value={username}
                  onChange={(event) => setUsername(event.target.value)}
                  required
                  minLength={3}
                  maxLength={50}
                  autoComplete="username"
                />
              </div>
            </div>

            <div className="login-field">
              <div className="login-field-row">
                <label htmlFor="password">Password</label>
                <a href="#" onClick={(event) => event.preventDefault()}>Forgot Password?</a>
              </div>
              <div className="login-input-wrap">
                <Lock size={16} />
                <input
                  id="password"
                  name="password"
                  type="password"
                  placeholder="Enter password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  required
                  minLength={8}
                  autoComplete="current-password"
                />
              </div>
            </div>

            {mode === 'register' ? (
              <div className="login-field">
                <label htmlFor="confirm-password">Confirm Password</label>
                <div className="login-input-wrap">
                  <Lock size={16} />
                  <input
                    id="confirm-password"
                    name="confirm-password"
                    type="password"
                    placeholder="Confirm password"
                    value={confirmPassword}
                    onChange={(event) => setConfirmPassword(event.target.value)}
                    required
                    minLength={8}
                    autoComplete="new-password"
                  />
                </div>
              </div>
            ) : null}

            <p className="login-hint">
              {mode === 'login'
                ? 'Use your registered username and password to sign in.'
                : 'Username must be 3-50 chars. Password must be at least 8 chars.'}
            </p>

            {error ? <p className="login-error">{error}</p> : null}

            <button type="submit" className="login-submit" disabled={isSubmitting}>
              {isSubmitting ? (mode === 'login' ? 'Signing In...' : 'Creating Account...') : (mode === 'login' ? 'Sign In' : 'Create Account')}
            </button>
          </form>

          <footer className="login-card-footer">
            <p>
              {mode === 'login' ? 'New to the system?' : 'Already have an account?'}
              <a
                href="#"
                onClick={(event) => {
                  event.preventDefault();
                  switchMode(mode === 'login' ? 'register' : 'login');
                }}
              >
                {mode === 'login' ? 'Create Account' : 'Sign In'}
              </a>
            </p>
          </footer>
        </section>

        <footer className="login-footer-links">
          <a href="#" onClick={(event) => event.preventDefault()}>Privacy Policy</a>
          <a href="#" onClick={(event) => event.preventDefault()}>Security</a>
          <a href="#" onClick={(event) => event.preventDefault()}>Support</a>
        </footer>
      </main>

      <div className="login-top-accent" aria-hidden="true" />
      <div className="login-bottom-accent" aria-hidden="true" />
      <div className="login-blob login-blob-right" aria-hidden="true" />
      <div className="login-blob login-blob-left" aria-hidden="true" />
    </div>
  );
}
