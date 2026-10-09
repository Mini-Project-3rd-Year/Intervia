/**
 * frontend/src/components/layout/Navbar.tsx
 * Landing page navigation bar — redesigned.
 */

import { Link } from "react-router-dom";

const Navbar = () => {
  return (
    <nav className="navbar" role="navigation" aria-label="Main navigation">
      {/* Logo */}
      <Link to="/" className="navbar-logo">
        <div className="navbar-logo-mark" aria-hidden="true">I</div>
        <span className="navbar-logo-name">Intervia</span>
      </Link>

      {/* Center links */}
      <ul className="navbar-links" role="list">
        <li>
          <a href="#features" className="navbar-link">Features</a>
        </li>
        <li>
          <a href="#how-it-works" className="navbar-link">How It Works</a>
        </li>
      </ul>

      {/* Actions */}
      <div className="navbar-actions">
        <Link to="/login">
          <button
            className="btn btn-secondary btn-sm"
            aria-label="Sign in to your account"
          >
            Sign In
          </button>
        </Link>
        <Link to="/register">
          <button
            className="btn btn-primary btn-sm"
            aria-label="Create a free account"
          >
            Start Free
          </button>
        </Link>
      </div>
    </nav>
  );
};

export default Navbar;
