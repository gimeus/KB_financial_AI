import React, { useState } from 'react';
import './App.css';
import StatusBar from './components/StatusBar';
import Header from './components/Header';
import ChatMessage from './components/ChatMessage';
import MicButton from './components/MicButton';

const App = () => {
  const [listening, setListening] = useState(false);

  const handleStart = () => {
    setListening(true);
  };

  const formatTime = (date) => {
    const options = { hour: 'numeric', minute: 'numeric', hour12: true };
    return new Intl.DateTimeFormat('en-US', options).format(date);
  };

  const currentTime = formatTime(new Date());

  return (
    <div className="app">
      <StatusBar />
      <Header />
      <div className="chat-window">
        <ChatMessage type="bot" time={currentTime}>
          KB Bank message
        </ChatMessage>
        <ChatMessage type="user" time={currentTime}>
          User message
        </ChatMessage>
      </div>
      <MicButton listening={listening} onClick={handleStart} />
    </div>
  );
};

export default App;
