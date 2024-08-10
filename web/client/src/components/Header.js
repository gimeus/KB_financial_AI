import React from 'react';
import chevronLeft from '../assets/icons/chevron-left.svg';
import languageIcon from '../assets/icons/language.svg';
import './Header.css';

const Header = () => {
  return (
    <div>
      <header className="header header-top">
        <img src={chevronLeft} alt="Chevron Left" className="chevron-icon" />
        <h1>Voice Assistant</h1>
        <button className="language-setting">
          <img src={languageIcon} alt="Language Settings" />
        </button>
      </header>
      <header className="header header-bottom">
        <h2>KB Bank</h2>
        <button className="end-chat">End Chat</button>
      </header>
      <header className="header header-notification">
        <h2>Do not share personal information.</h2>
      </header>
    </div>
  );
};

export default Header;
