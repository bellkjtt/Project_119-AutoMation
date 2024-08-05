import axios from 'axios';
import React, { useState, useEffect } from "react";

import './Home.css';
import styled from "styled-components";
import Draggable from 'react-draggable';
import { faUser } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { BackgroundVideo1 } from "../../components/CommonStyles";

const Navbar = styled.div`
  position: absolute;
  top: 0;
  width: 100%;
  display: flex;
  justify-content: space-between;
  padding: 20px;
  z-index: 1;
`;

const Logo = styled.img`
  width: 150px;
  height: auto;
  cursor: pointer;
`;

const NavItems = styled.div`
  display: flex;
  align-items: top;
  gap: 20px;
`;

const NavItem = styled.div`
  font-size: 18px;
  font-weight: 600;
  color: white;
  cursor: pointer;
  transition: transform 0.2s;
  &:hover {
    transform: scale(1.1);
  }
`;

const PopupWrapper = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 2;
  display: flex;
  justify-content: center;
  align-items: center;
  pointer-events: none; /* This allows clicks to pass through the wrapper */
`;

const PopupContent = styled.div`
  width: 600px; /* Fixed width */
  height: 650px; /* Fixed height */
  cursor: grab;
  padding: 20px;
  background: white;
  border-radius: 10px;
  box-shadow: rgba(0, 0, 0, 0.35) 0px 5px 15px;
  pointer-events: all; /* This allows clicks to interact with the popup content */

  &.dragging {
    cursor: grabbing;
  }
`;

const ImageContainer = styled.div`
  width: 100%;
  height: calc(100% - 40px); /* Adjust height to leave space for the checkbox and close button */
  display: flex;
  align-items: center;
  justify-content: center;
`;

const StyledImage = styled.img`
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
`;

const CloseButton = styled.button`
  border: none;
  background: none;
  font-size: 20px;
  cursor: pointer;
`;

const CheckboxContainer = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 10px;
`;

const CentralTextContainer = styled.div`
  position: absolute;
  top: 50%;
  left: 30%;
  transform: translate(-50%, -50%);
  text-align: center;
  color: white;
`;

const Subheading = styled.h2`
  font-size: 48px;
  margin-bottom: 10px;
  white-space: pre-line; /* 줄 바꿈 허용 */
`;

const Description = styled.p`
  font-size: 24px;
  white-space: pre-line; /* 줄 바꿈 허용 */
  text-align: left; /* 왼쪽 정렬 */
`;

const Home = () => {
  const [isPopupOpen, setIsPopupOpen] = useState(false);
  const [showPopupToday, setShowPopupToday] = useState(true);
  const [isDragging, setIsDragging] = useState(false);

  useEffect(() => {
    const lastVisit = localStorage.getItem('lastVisit');
    const today = new Date().toISOString().split('T')[0];

    if (lastVisit !== today) {
      setIsPopupOpen(true);
    }
  }, []);

  const closePopup = () => {
    if (!showPopupToday) {
      const today = new Date().toISOString().split('T')[0];
      localStorage.setItem('lastVisit', today);
    }
    setIsPopupOpen(false);
  };

  const handleStart = () => {
    setIsDragging(true);
  };

  const handleStop = () => {
    setIsDragging(false);
  };

  useEffect(() => {
    // csrf token 가져오기
    axios.get(process.env.REACT_APP_USER_SERVER_URL + 'signup/')
  }, [])

  return (
    <div className="home-container">
      <BackgroundVideo1 />
      <Navbar>
        <Logo src="/images/logoEX.png" alt="Logo" />
        <NavItems>
          <NavItem onClick={() => window.location.href = "/main"}>
            <FontAwesomeIcon icon={faUser} /> 관리자 페이지
          </NavItem>
          <NavItem onClick={() => window.location.href = "/report"}>
            신고하기
          </NavItem>
        </NavItems>
      </Navbar>
      <CentralTextContainer>
        <Subheading>긴급 신고 자동화 시스템</Subheading>
        <Description>AI 기술을 이용한 신고 자동화로 <br />신속하고 효율적인 신고 접수를 지원합니다</Description>
      </CentralTextContainer>

      {isPopupOpen && (
        <PopupWrapper>
          <Draggable onStart={handleStart} onStop={handleStop} bounds="parent">
            <PopupContent className={isDragging ? 'dragging' : ''}>
              <ImageContainer>
                <a href="https://www.nfa.go.kr/nfa/publicrelations/emergencyservice/119emergencydeclaration/" target="_blank" rel="noopener noreferrer">
                  <StyledImage
                    src="/images/emergency_report.jpg"
                    alt="Popup"
                  />
                </a>
              </ImageContainer>
              <CheckboxContainer>
                <label>
                  <input
                    type="checkbox"
                    checked={!showPopupToday}
                    onChange={() => setShowPopupToday(!showPopupToday)}
                  /> 오늘 하루 이 창 띄우지 않기
                </label>
                <CloseButton onClick={closePopup}>X</CloseButton>
              </CheckboxContainer>
            </PopupContent>
          </Draggable>
        </PopupWrapper>
      )}
    </div>
  );
};

export default Home;
