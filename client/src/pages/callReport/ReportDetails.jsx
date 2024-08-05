import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

import { toKoreaTime } from '../../utils/utils';
import { getReportById } from '../../apis/report';

import './ReportContent.css';
import Header from '../../components/header/Header'; 
import KakaoMap from '../../components/call/KaKaoMap';

const ReportDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [report, setReport] = useState(null);

  useEffect(() => {
    getReportById(id).then((res) => {
      setReport(res);
    })
  }, []);

  // useEffect(() => {
  //   const allReports = [
  //     { pk: 1, fields: { date: '2023-01-01T10:00:00Z', address_name: '서울시 강남구', place_name: '강남역', largeCategory: '사고', midCategory: '교통사고', content: '신고 내용 1', lat: 37.497946, long: 127.027600, recording: '녹취록 1', recordingUrl: '/recordings/exRec.mp3'  } },
  //     { pk: 2, fields: { date: '2023-01-02T11:00:00Z', address_name: '서울시 서초구', place_name: '서초역', largeCategory: '화재', midCategory: '방화', content: '신고 내용 2', lat: 37.491899, long: 127.007917, recording: '녹취록 2', recordingUrl: '/recordings/exRec.mp3'  } },
  //     { pk: 3, fields: { date: '2023-01-03T12:00:00Z', address_name: '서울시 송파구', place_name: '잠실역', largeCategory: '응급', midCategory: '자살시도', content: '신고 내용 3', lat: 37.513276, long: 127.100199, recording: '녹취록 3', recordingUrl: '/recordings/exRec.mp3'  } },
  //     { pk: 4, fields: { date: '2023-01-01T13:00:00Z', address_name: '서울시 강남구', place_name: '강남구보건소', largeCategory: '사고', midCategory: '실종자 신고', content: '신고 내용 4', lat: 37.517408, long: 127.046367, recording: '녹취록 4', recordingUrl: '/recordings/exRec.mp3'  } },
  //     { pk: 5, fields: { date: '2023-01-02T15:00:00Z', address_name: '서울시 광진구', place_name: '스타벅스 자양역점', largeCategory: '사고', midCategory: '추락사고', content: '신고 내용 5', lat: 37.537846, long: 127.068785, recording: '녹취록 5', recordingUrl: '/recordings/exRec.mp3'  } },
  //     { pk: 6, fields: { date: '2023-01-03T15:00:00Z', address_name: '서울시 강동구', place_name: '강동도서관', largeCategory: '화재', midCategory: '화재', content: '신고 내용 6', lat: 37.548798, long: 127.145425, recording: '녹취록 6', recordingUrl: '/recordings/exRec.mp3'  } },
  //   ];

  //   const foundReport = allReports.find(report => report.pk === parseInt(id));
  //   setReport(foundReport);
  // }, [id]);

  if (!report) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <Header />
      <div className='Details'>
        <h1>{toKoreaTime(report.fields.date)}</h1>
        <div className='detail-contents'>
          <div className='detail-item'>
            <label>ID</label>
            <span>{report.pk}</span>
          </div>
          <div className='detail-item-row'>
            <div className='detail-item'>
              <label>주소</label>
              <span>{report.fields.address_name}</span>
            </div>
            <div className='detail-item'>
              <label>장소</label>
              <span>{report.fields.place_name}</span>
            </div>
          </div>
          <div className='detail-item-row'>
            <div className='detail-item'>
              <label>대분류</label>
              <span>{report.fields.category}</span>
            </div>
            <div className='detail-item'>
              <label>구급/비구급</label>
              <span>{report.fields.emergency_type}</span>
            </div>
          </div>
          <div className='detail-item'>
            <label>내용</label>
            <span>{report.fields.details}</span>
          </div>
          <div className='detail-item'>
            <label>녹취록</label>
            <span>{report.fields.full_text}</span>
          </div>
          <div className='detail-item'>
            <label>위치</label>
            <div style={{width: '700px', height: '300px'}}>
              <KakaoMap lat={report.fields.lat} lng={report.fields.lng} />
            </div>
          </div>
          <div className='detail-item'>
            <label>녹음 파일</label>
              {report.fields.audio_file &&
                <audio controls>
                  <source src={ `${process.env.REACT_APP_SERVER_URL}media/full_audio/${report.fields.audio_file.slice(17)}`} type="audio/mpeg" />
                  Your browser does not support the audio element.
                </audio>
              }
          </div>
        </div>
        <div className="list-button-container">
          <img 
            src="/images/list.png" 
            alt="목록" 
            className="toList-button" 
            onClick={() => navigate('/callreport')}  
          />
          <p>목록으로</p>
        </div>
      </div>
    </div>
  );
};

export default ReportDetails;
