import React from 'react';
import './MicButton.css';
import microphoneIcon from '../assets/icons/microphone.svg';

const MicButton = ({ listening, onClick }) => {
  return (
    <button onClick={onClick} disabled={listening} className="mic-button">
      <img src={microphoneIcon} alt="Microphone" className="mic-icon" />
    </button>
  );
};

export default MicButton;
