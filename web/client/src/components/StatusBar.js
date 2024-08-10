import React from 'react';
import './StatusBar.css';
import StatusIcon from '../assets/icons/Status Bar.png';

const StatusBar = () => {
  return (
    <div className="status-bar">
      <img src={StatusIcon} alt="Status Icon" className="status-bar" />
    </div>
  );
};

export default StatusBar;
