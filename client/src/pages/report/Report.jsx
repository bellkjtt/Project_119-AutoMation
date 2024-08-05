import { ReactMic } from 'react-mic'; 
import React, { useState, useEffect, useRef } from 'react';

import './Report.css';
import io from 'socket.io-client';
import Overlay from '../../components/call/Overlay';
import CallModal from '../../components/call/CallModal';
import { GoBackBtn } from '../../components/CommonStyles';

const socket = io('http://localhost:5000', {
  transports: ['websocket']
});

const Report = () => {
  const [result, setResult] = useState('');
  const [chat, setChat] = useState([{ text: '신고 시작', isUser: false }]);
  const [recording, setRecording] = useState(false);
  const [ttsFinished, setTtsFinished] = useState(false);
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);
  const intervalRef = useRef(null);
  const recognitionRef = useRef(null);
  const silenceTimerRef = useRef(null);

  useEffect(() => {
    socket.on('audio_text', (data) => {
      console.log('Received audio_text:', data.audio_text);
      setResult(data.audio_text);
      setChat(prevChat => [...prevChat, { text: data.audio_text, isUser: true }]);
      playTts(data.audio_text);
    });

    return () => {
      socket.off('audio_text');
    };
  }, []);

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

      setResult(finalTranscript || interimTranscript);
      if (finalTranscript) {
        setChat(prevChat => [...prevChat, { text: finalTranscript, isUser: true }]);
        socket.emit('audio_text', { audio_text: finalTranscript });
      }
      resetSilenceTimer();
    };

    recognitionRef.current.onerror = (event) => {
      console.error('Speech Recognition Error', event.error);
    };
  }, []);

  useEffect(() => {
    playTts('신고 시작', () => {
      setTtsFinished(true);
    });
  }, []);

  const startRecording = () => {
    navigator.mediaDevices.getUserMedia({ audio: true })
      .then(stream => {
        mediaRecorderRef.current = new MediaRecorder(stream);
        chunksRef.current = [];

        mediaRecorderRef.current.ondataavailable = e => {
          chunksRef.current.push(e.data);
        };

        mediaRecorderRef.current.onstop = async () => {
          const blob = new Blob(chunksRef.current, { 'type': 'audio/webm' });
          const arrayBuffer = await blob.arrayBuffer();
          const audioData = new Uint8Array(arrayBuffer);
          const wavBuffer = await convertToWav(audioData);
          socket.emit('audio_data', wavBuffer);
          chunksRef.current = [];
        };

        mediaRecorderRef.current.start();
        setRecording(true);

        intervalRef.current = setInterval(() => {
          if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
            mediaRecorderRef.current.stop();
            mediaRecorderRef.current.start();
          }
        }, 5000);

        recognitionRef.current.start();
        startSilenceTimer();
      })
      .catch(err => {
        console.error('Error accessing microphone:', err);
      });
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      clearInterval(intervalRef.current);
      mediaRecorderRef.current.stop();
      recognitionRef.current.stop();
      setRecording(false);
      clearTimeout(silenceTimerRef.current);
    }
  };

  const startSilenceTimer = () => {
    silenceTimerRef.current = setTimeout(async () => {
      stopRecording();
      const ttsText = await fetchTtsText();
      setChat(prevChat => [...prevChat, { text: ttsText, isUser: false }]);
      playTts(ttsText, startRecording);
    }, 5000);
  };

  const resetSilenceTimer = () => {
    clearTimeout(silenceTimerRef.current);
    startSilenceTimer();
  };

  const fetchTtsText = async () => {
    const response = await fetch('http://localhost:5000/get-tts-text');
    const data = await response.json();
    return data.text;
  };

  const playTts = (text, callback) => {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'ko-KR';
    utterance.onend = () => {
      if (callback) callback();
    };
    window.speechSynthesis.speak(utterance);
  };

  const convertToWav = async (audioData) => {
    const audioContext = new AudioContext();
    const audioBuffer = await audioContext.decodeAudioData(audioData.buffer);
    
    const targetSampleRate = 16000;
    const numChannels = audioBuffer.numberOfChannels;
    const length = audioBuffer.length * targetSampleRate / audioBuffer.sampleRate;
    const offlineContext = new OfflineAudioContext(numChannels, length, targetSampleRate);
    
    const bufferSource = offlineContext.createBufferSource();
    bufferSource.buffer = audioBuffer;
    
    bufferSource.connect(offlineContext.destination);
    bufferSource.start(0);
    
    const resampledBuffer = await offlineContext.startRendering();
    return encodeWAV(resampledBuffer);
  };

  const encodeWAV = (audioBuffer) => {
    const numChannels = audioBuffer.numberOfChannels;
    const sampleRate = audioBuffer.sampleRate;
    const format = 1;
    const bitDepth = 16;
    const bytesPerSample = bitDepth / 8;

    let buffers = [];
    for (let i = 0; i < numChannels; i++) {
      buffers.push(audioBuffer.getChannelData(i));
    }

    const interleaved = interleave(buffers);
    const buffer = new ArrayBuffer(44 + interleaved.length * bytesPerSample);
    const view = new DataView(buffer);

    writeString(view, 0, 'RIFF');
    view.setUint32(4, 36 + interleaved.length * bytesPerSample, true);
    writeString(view, 8, 'WAVE');
    writeString(view, 12, 'fmt ');
    view.setUint32(16, 16, true);
    view.setUint16(20, format, true);
    view.setUint16(22, numChannels, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, sampleRate * numChannels * bytesPerSample, true);
    view.setUint16(32, numChannels * bytesPerSample, true);
    view.setUint16(34, bitDepth, true);
    writeString(view, 36, 'data');
    view.setUint32(40, interleaved.length * bytesPerSample, true);

    floatTo16BitPCM(view, 44, interleaved);

    return buffer;
  };

  const writeString = (view, offset, string) => {
    for (let i = 0; i < string.length; i++) {
      view.setUint8(offset + i, string.charCodeAt(i));
    }
  };

  const interleave = (buffers) => {
    const length = buffers[0].length;
    const result = new Float32Array(length * buffers.length);

    let inputIndex = 0;
    for (let i = 0; i < length; i++) {
      for (let j = 0; j < buffers.length; j++) {
        result[inputIndex++] = buffers[j][i];
      }
    }
    return result;
  };

  const floatTo16BitPCM = (output, offset, input) => {
    for (let i = 0; i < input.length; i++, offset += 2) {
      const s = Math.max(-1, Math.min(1, input[i]));
      output.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
    }
  };

  return (
    <div className="report-container">
      {/* <Overlay /> */}
      {/* <CallModal /> */}
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
          {!recording ? 
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
          </div>
        ))}
      </div>
    </div>
  );
};

export default Report;
