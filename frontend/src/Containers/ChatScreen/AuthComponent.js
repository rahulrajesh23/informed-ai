import React, { useState } from 'react';
import styles from './LoginModal.module.css';

const LoginModal = ({ onClose, onLogin }) => {
  const [username, setUsername] = useState('');

  const handleLogin = () => {
    onLogin(username);
    setUsername('');
    onClose();
  };

  return (
    <div className={styles.modal}>
      <div className={styles.modalContent}>
            
        <div className={styles.loginModalHeading}>
            <p>Enter User Details</p>
            <div className={styles.closeButtonContainer} onClick={onClose}>
                x
            </div>
        </div>
        
        <div className={styles.loginActionsContainer}>
            <div className={styles.userNameInputContainer}>
                <input
                type="text"
                placeholder="Enter your username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className={styles.userNameInput}
                />
            </div>
            <div className={styles.usernameSubmitContainer}>
                <button className={styles.usernameSubmit} onClick={handleLogin}>Login</button>
            </div>
            
        </div>
        
      </div>
    </div>
  );
};

const AuthComponent = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [username, setUsername] = useState('');

  const handleLogin = (username) => {
    setUsername(username);
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    setUsername('');
    setIsLoggedIn(false);
  };

  return (
    <div className={styles.AuthComponent}>
        <div className={styles.loginlogoutContainer}>
            {isLoggedIn ? (
            <button className={styles.close} onClick={handleLogout}>Logout</button>
            ) : (
                <button onClick={() => setShowModal(true)}>Login</button>
            )}
        </div>
    
        {
        isLoggedIn &&
            <div className={styles.loggedInMsg}>Welcome, {username}!</div>
        }

        {showModal && (
        <LoginModal
            onClose={() => setShowModal(false)}
            onLogin={handleLogin}
        />
        )}
    </div>
  );
};

export default AuthComponent;
