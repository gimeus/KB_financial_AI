import React from 'react';
import './ChatMessage.css';
import BotLogo from '../assets/icons/KB.svg';

const formatTime = (time) => {
  const period = time.includes('오후') || time.includes('PM') ? 'PM' : 'AM';

  let [hour, minute] = time.match(/\d{1,2}:\d{2}/)[0].split(':');

  hour = parseInt(hour, 10);

  if (period === 'PM' && hour < 12) {
    hour += 12;
  } else if (period === 'AM' && hour === 12) {
    hour = 0;
  }

  hour = hour % 12 || 12;

  return `${hour}:${minute} ${period}`;
};

const ChatMessage = ({ type, children, time }) => {
  return (
    <div className={`message-container ${type === 'user' ? 'user' : 'bot'}`}>
      {type === 'bot' && (
        <div className="message-time-container">
          <img src={BotLogo} alt="Bot Logo" className="message-bot-logo" />
          <div className="message-time-text">
            <span className="message-text-label">KB Bank</span>
            <span className="message-time">{formatTime(time)}</span>
          </div>
        </div>
      )}
      {type === 'user' && (
        <div className="message-time message-time-user">{formatTime(time)}</div>
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
