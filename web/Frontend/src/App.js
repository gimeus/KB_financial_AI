import React, { useState } from 'react';
import axios from 'axios';
import './App.css';
import StatusBar from './components/StatusBar';
import Header from './components/Header';
import ChatMessage from './components/ChatMessage';
import MicButton from './components/MicButton';

const App = () => {
  const [messageList, setMessageList] = useState([]);
  const [listening, setListening] = useState(false);

  // 메시지 저장 함수
  const saveMessageToDB = async (message) => {
    try {
      await axios.post('http://localhost:8001/messages/', message);
      console.log('Message saved to DB');
    } catch (error) {
      console.error('Failed to save message to DB:', error);
    }
  };

  // Web Speech API를 사용한 음성 인식 함수
  const handleStart = () => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      alert(
        'Your browser does not support Speech Recognition. Please try using Chrome or Edge.'
      );
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
      console.log('Voice recognition started.');
      setListening(true);
    };

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      console.log('Transcription:', transcript);

      const newMessage = {
        type: 'user',
        text: transcript,
        time: new Date().toLocaleTimeString(),
      };

      // 메시지 리스트 업데이트
      setMessageList((prevMessages) => [...prevMessages, newMessage]);

      // 데이터베이스에 저장
      saveMessageToDB(newMessage);

      setListening(false);
    };

    recognition.onerror = (event) => {
      console.error('Recognition error:', event.error);
      setListening(false);
    };

    recognition.onend = () => {
      console.log('Voice recognition ended.');
      setListening(false);
    };

    recognition.start();
  };

  return (
    <div className="app">
      <StatusBar />
      <Header />
      <div className="chat-window">
        {messageList.map((message, index) => (
          <ChatMessage key={index} type={message.type} time={message.time}>
            {message.text}
          </ChatMessage>
        ))}
      </div>
      <MicButton listening={listening} onClick={handleStart} />
    </div>
  );
};

export default App;
