import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import StatusBar from './components/StatusBar';
import Header from './components/Header';
import ChatMessage from './components/ChatMessage';
import MicButton from './components/MicButton';

const App = () => {
  const [messageList, setMessageList] = useState([]);
  const [listening, setListening] = useState(false);
  const [dbStatus, setDbStatus] = useState("Checking database connection...");

  // 데이터베이스 연결 상태 확인 함수
  const checkDbConnection = async () => {
    try {
      const response = await axios.get('http://localhost:8000/test-db/');
      setDbStatus(response.data.message);
    } catch (error) {
      console.error('Failed to connect to database:', error);
      setDbStatus("Database connection failed");
    }
  };

  // 마운트 시 데이터베이스 연결 상태 확인
  useEffect(() => {
    checkDbConnection();
  }, []);

  // // 샘플 메시지 저장 함수
  // const saveSampleMessageToDB = async () => {
  //   const sampleMessage = {
  //     type: 'user',
  //     text: 'This is a sample message',
  //     time: new Date().toLocaleTimeString(),
  //   };

  //   try {
  //     await axios.post('http://localhost:8000/messages/', sampleMessage);
  //     console.log('Sample message saved to DB:', sampleMessage);

  //     // 메시지 리스트 업데이트
  //     setMessageList((prevMessages) => [...prevMessages, sampleMessage]);
  //   } catch (error) {
  //     console.error('Failed to save sample message to DB:', error);
  //   }
  // };

  // MicButton 클릭 시 샘플 메시지 저장
  const handleMicButtonClick = async () => {
    try {
      const response = await axios.post('http://localhost:8000/start-recording');
      console.log('Recording started:', response.data.message);
    } catch (error) {
      console.error('Failed to start recording:', error);
    }
  };

  return (
    <div className="app">
      <StatusBar />
      <Header />
      <p>{dbStatus}</p>
      <div className="chat-window">
        {messageList.map((message, index) => (
          <ChatMessage key={index} type={message.type} time={message.time}>
            {message.text}
          </ChatMessage>
        ))}
      </div>
      <MicButton listening={listening} onClick={handleMicButtonClick} />
    </div>
  );
};

export default App;
