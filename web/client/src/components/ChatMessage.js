import React from 'react';
import './ChatMessage.css';
import BotLogo from '../assets/icons/KB.svg'; // SVG 파일 경로

const ChatMessage = ({ type, children, time }) => {
  return (
    <div className={`message-container ${type === 'user' ? 'user' : 'bot'}`}>
      {type === 'bot' && (
        <div className="message-time-container">
          <img src={BotLogo} alt="Bot Logo" className="message-bot-logo" />
          <div className="message-time-text">
            <span className="message-text-label">KB Bank</span>
            <span className="message-time">{time}</span>
          </div>
        </div>
      )}
      {type === 'user' && (
        <div className="message-time message-time-user">{time}</div>
      )}
      <div
        className={`message ${
          type === 'user' ? 'message-user' : 'message-bot'
        }`}
      >
        {children}
      </div>
    </div>
  );
};

export default ChatMessage;
