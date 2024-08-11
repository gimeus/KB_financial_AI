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

  // 마운트 시 데이터베이스 연결 상태 확인 및 주기적으로 메시지 가져오기
  useEffect(() => {
    checkDbConnection();
    fetchMessages(); // 초기 메시지 가져오기
    
    // 5초마다 메시지 갱신
    const interval = setInterval(fetchMessages, 3000);
    // 컴포넌트 언마운트 시 인터벌 정리
    return () => clearInterval(interval);
  }, []);

// 데이터베이스에서 메시지 가져오기
const fetchMessages = async () => {
  try {
    const response = await axios.get('http://localhost:8000/messages/');
    console.log('Messages fetched:', response.data);
    setMessageList(response.data);
  } catch (error) {
    console.error('Failed to fetch messages:', error.response || error.message);
  }
};

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

  // MicButton 클릭 시 test3.py 실행 및 메시지 가져오기 시작
  const handleMicButtonClick = async () => {
    try {
      const response = await axios.post('http://localhost:8000/start-recording');
      console.log('Recording started:', response.data.message);

      // 5초마다 메시지 갱신
      setListening(true);
      const interval = setInterval(fetchMessages, 5000);

      // 녹음 종료 시 인터벌 정리
      return () => clearInterval(interval);
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
