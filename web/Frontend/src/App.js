import React, { useState } from 'react';
import './App.css';
import StatusBar from './components/StatusBar';
import Header from './components/Header';
import ChatMessage from './components/ChatMessage';
import MicButton from './components/MicButton';

const App = () => {
  const [messageList, setMessageList] = useState([]);
  const [listening, setListening] = useState(false);

  // Web Speech API를 사용한 음성 인식 함수
  const handleStart = () => {
    // 브라우저 호환성 체크
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      alert(
        'Your browser does not support Speech Recognition. Please try using Chrome or Edge.'
      );
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = 'en-US'; // 인식할 언어 설정
    recognition.interimResults = false; // 중간 결과 반환 여부
    recognition.maxAlternatives = 1; // 최대 대안 개수

    recognition.onstart = () => {
      console.log('Voice recognition started.');
      setListening(true);
    };

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript; // 인식된 텍스트
      console.log('Transcription:', transcript);

      // 인식된 텍스트를 메시지 리스트에 추가
      setMessageList((prevMessages) => {
        const newMessages = [
          ...prevMessages,
          {
            type: 'user',
            text: transcript,
            time: new Date().toLocaleTimeString(),
          },
        ];
        console.log('Updated message list:', newMessages); // 상태 업데이트 확인
        return newMessages;
      });

      setListening(false); // 인식 종료 시 listening 상태 해제
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
