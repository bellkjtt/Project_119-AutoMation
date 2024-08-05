import React, { useState, useEffect, useRef } from 'react';

import { ReactMic } from 'react-mic';
import { convertToWav } from '../../utils/report';

import './Report.css';
import io from 'socket.io-client';
import Overlay from '../../components/call/Overlay';
import CallModal from '../../components/call/CallModal';
import { GoBackBtn } from '../../components/CommonStyles';
import { getReportById } from '../../apis/report';

const socket = io('http://localhost:5000', {
  transports: ['websocket']
});

const Report4 = () => {
  const [start, setStart] = useState(false);
  const [recording, setRecording] = useState(false);
  const [chat, setChat] = useState([{ text: '녹음 버튼을 누르고 신고를 시작해주세요.', isUser: false }]);
  const [interimTranscript, setInterimTranscript] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);

  const [done, setDone] = useState(false);
  const [address, setAddress] = useState('');
  const [place, setPlace] = useState('')
  const [time, setTime] = useState('')
  const [content, setContent] = useState('');
  const [where, setWhere] = useState('');
  const [lat, setLat] = useState(0);
  const [lng, setLng] = useState(0);

  const chunksRef = useRef([]);
  const allChunksRef = useRef([]);
  const mediaRecorderRef = useRef(null);
  const recognitionRef = useRef(null);
  const silenceTimerRef = useRef(null);

  // 백 -> 프론트 소켓
  useEffect(() => {
    socket.on('audio_text', (data) => {
      console.log('Received audio_text:', data);
      setIsProcessing(false); // 처리 중 상태 해제

      let msg = '';
      if (data.log_id) {
        getReportById(data.log_id).then((res) => {
          setAddress(res.fields.address_name);
          setPlace(res.fields.place_name);
          setTime(res.fields.date);
          setContent(res.fields.details);
          setWhere(res.fields.jurisdiction);
          setLat(res.fields.lat);
          setLng(res.fields.lng);
        })
        msg = data.message;
        setDone(true);
        processChunks(true, data.log_id);
      }
      msg = data.message;
      setChat(prevChat => [...prevChat, { text: msg, isUser: false }]);
      playTts(msg);
    });

    return () => {
      socket.off('audio_text');
    };
  }, []);

  // 녹음 시작
  const startRecording = () => {
    setStart(true);

    navigator.mediaDevices.getUserMedia({ audio: true })
      .then(stream => {
        mediaRecorderRef.current = new MediaRecorder(stream);
        chunksRef.current = [];

        mediaRecorderRef.current.ondataavailable = e => {
          chunksRef.current.push(e.data);
          allChunksRef.current.push(e.data);
        };

        mediaRecorderRef.current.onstop = async () => {
          setIsProcessing(true); // 처리 중 상태 설정
          await processChunks();
        };

        mediaRecorderRef.current.start();
        recognitionRef.current.start();
        setRecording(true);
        startSilenceTimer();
      })
      .catch(err => {
        console.error('Error accessing microphone:', err);
      });
  };

  // 녹음 중지
  const pauseRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      recognitionRef.current.stop();
      setRecording(false);
      clearTimeout(silenceTimerRef.current);
    }
  }

  // 녹음 끝
  const stopRecording = () => {
    setStart(false);
    pauseRecording();
  };

  const processChunks = async (isFinal = false, id = 0) => {
    if (isFinal) {
      const allBlob = new Blob(allChunksRef.current, { 'type': 'audio/webm' });
      const allArrayBuffer = await allBlob.arrayBuffer();
      const allAudioData = new Uint8Array(allArrayBuffer);
      const allWavBuffer = await convertToWav(allAudioData);
      socket.emit('audio_full', {'wav' : allWavBuffer, 'log_id' : id});
      allChunksRef.current = [];
      socket.disconnect();
    } else {
      const blob = new Blob(chunksRef.current, { 'type': 'audio/webm' });
      const arrayBuffer = await blob.arrayBuffer();
      const audioData = new Uint8Array(arrayBuffer);
      const wavBuffer = await convertToWav(audioData);
      socket.emit('audio_data', wavBuffer);
      chunksRef.current = [];
    }
  };

  const startSilenceTimer = () => {
    silenceTimerRef.current = setTimeout(async () => {
      pauseRecording();
    }, 3000);
  };

  const resetSilenceTimer = () => {
    clearTimeout(silenceTimerRef.current);
    startSilenceTimer();
  };

  // tts
  const playTts = (text) => {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'ko-KR';
    window.speechSynthesis.speak(utterance);

    utterance.onend = () => {
      startRecording();
    };
  };

  // stt
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

      setInterimTranscript(interimTranscript); // 실시간으로 인식된 텍스트 업데이트

      if (finalTranscript) {
        setChat(prevChat => [...prevChat, { text: finalTranscript, isUser: true }]);
        setInterimTranscript(''); // 최종 텍스트가 인식되면 interim 텍스트 초기화
      }

      resetSilenceTimer();
    };

    recognitionRef.current.onerror = (event) => {
      console.error('Speech Recognition Error', event.error);
    };
  }, []);

  return (
    <div className="report-container">
      {done && <>
        <Overlay />
        <CallModal address={address} place={place} time={time} content={content} where={where} lat={lat} lng={lng} />
      </>}
      <GoBackBtn />
      <div className="recording-container">
        <div className="bold-text">정확한 접수를 위해 녹음버튼을 눌러주세요</div>
        <div className="react-mic-container">
          <ReactMic
            record={recording}
            className="sound-wave"
            mimeType="audio/wav"
            strokeColor="#444445"
            backgroundColor="#ffffff" />
        </div>
        <div className="button-container">
          {!start ? 
            <button className="btn-border" onClick={startRecording} disabled={recording}>
              <div className="circle" />
            </button> :
            <button className="btn-border" onClick={stopRecording} disabled={!recording}>
              <div className="square" />
            </button>
          }
        </div>
      </div>
      <div className="chat-container">
        {chat.map((msg, index) => (
          <div key={index} className={`chat-bubble ${msg.isUser ? 'user' : 'system'}`}>
            {msg.text}
            {isProcessing && msg.isUser && index === chat.length - 1 && (
              <div className="processing-text">처리 중입니다. 잠시만 기다려주세요.</div>
            )}
          </div>
        ))}
        {interimTranscript && (
          <div className="chat-bubble user">
            {interimTranscript}
          </div>
        )}
      </div>
    </div>
  );
}

export default Report4;
