import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import React, { useState, useEffect } from 'react';

import './Login.css'; 
import { login } from '../../apis/user';
import { BackgroundVideo1, FullContainer, GoBackBtn } from '../../components/CommonStyles';
import { enterKey } from '../../utils/keyboard';

const Login = () => {
  const [id, setId] = useState('');
  const [password, setPassword] = useState('');

  const navigate = useNavigate();

  useEffect(() => {
    // csrf token 가져오기
    axios.get('http://localhost:8000/account/signup/')
  }, [])

  return (
    <FullContainer>
      <GoBackBtn />
      <BackgroundVideo1 />
      <div className="login-container">
        <div className="container">
          <div className="image-section">
            <img src="/images/1.jpg" alt="Logo" />
          </div>
          <div className="login-section">
            <div className="login-header">
              <img src="/images/mainlogo.png" alt="Login Icon" />
              <span>로그인</span>
            </div>
            <form>
              <input
                  value={id}
                  onChange={(e) => setId(e.target.value)}
                  placeholder="ID"
                  />
              <input
                  type="password"
                  value={password}
                  placeholder="PW"
                  onKeyDown={(e) => enterKey(e, () => login(id, password))}
                  onChange={(e) => setPassword(e.target.value)}
                  />
              <button type="button" onClick={() => login(id, password)}>로그인</button>
            </form>
            <div className="links">
              <button className="link-button" onClick={() => navigate('/signup')}>회원가입</button>
              <button className="link-button" onClick={() => navigate('/findid')}>ID 찾기</button>
              <button className="link-button" onClick={() => navigate('/changepw')}>PW 변경</button>
            </div>
          </div>
        </div>
      </div>
    </FullContainer>
  );
};

export default Login;
