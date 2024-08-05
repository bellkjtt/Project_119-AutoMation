import React, { useState, useEffect, useRef } from 'react';

import io from 'socket.io-client';
import axios from 'axios';
import { ReactMic } from 'react-mic'; 

import styled from 'styled-components';
import { FullContainer, GoBackBtn } from '../../components/CommonStyles';

const SERVER_URL = 'http://localhost:8000/stt/';
const socket = io('http://localhost:5000', {
  transports: ['websocket']
});


const BoldText = styled.p`
  font-size: 20px;
  font-weight: bold;
  color: #CF1010;
  margin-bottom: 40px;
`;

const RecordBox = styled.div`
  width: 550px;
  height: 350px;
  display: flex;
  text-align: center;
  align-items: center;
  flex-direction: column;
  justify-content: center;
  margin-bottom: 25px;
  border-radius: 20px;
  color: #db0948;
  background-color: #f5f5f5c0;
`;

const BtnBorder = styled.button`
  width: 60px;
  height: 60px;
  border: none;
  border-radius: 50%;
  background-color: rgb(255, 255, 255, 0.5);
  cursor: pointer;
`;

const Circle = styled.div`
  width: 20px;
  height: 20px;
  margin: 0 auto;
  border-radius: 50%;
  background-color: red;
`;

const Square = styled.div`
  width: 20px;
  height: 20px;
  margin: 0 auto;
  background-color: red;
`;

const Report2 = () => {
  const [sttText, setSttText] = useState('');
  const [ttsText, setTtsText] = useState('');
  const [recording, setRecording] = useState(false);
  const [ttsFinished, setTtsFinished] = useState(false); // TTS 완료 여부 상태 추가

  const recognitionRef = useRef(null);

  const startRecording = () => {
    axios.post(SERVER_URL + 'start_recording/')
    .then((res) => {
      setRecording(true);
      console.log(res);
      recognitionRef.current.start();
    })
    .catch((error) => console.error(error))
  }

  const stopRecording = () => {
    axios.post(SERVER_URL + 'stop_recording/')
    .then((res) => {
      setRecording(false);
      console.log(res);
      recognitionRef.current.stop();
    })
    .catch((error) => console.error(error))
  }

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      console.error('Web Speech API is not supported by this browser.');
      return;
    }

    recognitionRef.current = new SpeechRecognition();
    recognitionRef.current.continuous = true;
    recognitionRef.current.interimResults = true;
    recognitionRef.current.lang = 'ko-KR';

    recognitionRef.current.onresult = (event) => {
      let interimTranscript = '';
      let finalTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript;
        } else {
          interimTranscript += event.results[i][0].transcript;
        }
      }

      setSttText(finalTranscript || interimTranscript);
    };

    recognitionRef.current.onerror = (event) => {
      console.error('Speech Recognition Error', event.error);
    };

    // 서버에서 보내주는 정보
    socket.on('audio_text', (data) => {
      console.log(data)
    })
  }, []);

return (
    <FullContainer>
      <video autoPlay muted loop id="background-video">
        <source src="/videos/firetruck.mp4" type="video/mp4" />
        Your browser does not support the video tag.
      </video>
      <GoBackBtn />
      <div>
        <RecordBox>
          <BoldText>정확한 접수를 위해 녹음버튼을 눌러주세요</BoldText>
        <div style={{ width: "300px", overflow: "hidden", margin: "0 auto" }}>
          <ReactMic
          record={recording}
          className="sound-wave"
          mimeType="audio/wav"
          strokeColor="#444445"
          backgroundColor="#d9d9d9" />
        </div>
        </RecordBox>
          <div style={{ display: "flex", justifyContent: "center" }}>
            {!recording ? 
              <BtnBorder onClick={startRecording} disabled={recording}>
                <Circle />
              </BtnBorder> :
              <BtnBorder onClick={stopRecording} disabled={!recording}>
                <Square />
              </BtnBorder>
            }
          </div>
        <p style={{color: 'white'}}>{sttText}</p>
        {ttsText && (
          <p style={{color: 'white', marginTop: '20px'}}>TTS: {ttsText}</p>
        )}
      </div>
    </FullContainer>
  );
}

export default Report2;