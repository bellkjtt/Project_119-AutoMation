import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

import { getUser } from '../../apis/user';
import { enterKey } from '../../utils/keyboard';
import { getNotice } from '../../apis/notification';

import './Notice.css'
import Header from '../../components/header/Header';
import NoticeTable from '../../components/notification/NoticeTable';

const NoticeList = () => {
  const navigate = useNavigate();

  const [isAdmin, setIsAdmin] = useState(false); 
  const [showNotice, setShowNotice] = useState([])
  const [totalNotice, setTotalNotice] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');

  // 관리자 여부 확인
  const checkIsAdmin = () => {
    getUser().then((res) => {
      const admin = res.is_admin;
      if (admin) setIsAdmin(true);
    })
  }

  // 전체 공지사항 가져오기
  const getAllNotice = () => {
    getNotice().then((res) => {
      setTotalNotice(res);
      setShowNotice(res);
    })
  }

  // 검색 버튼
  const onSearch = () => {
    const data = totalNotice.filter(item => item.fields.title.includes(searchQuery));
    setShowNotice(data);
  }

  useEffect(() => {
    checkIsAdmin();
    getAllNotice();
  }, []);

  return (
    <>
      <Header />
      <div className='notice-container'>
        <div className='notice-header'>
          <div>
            <input placeholder='검색어를 입력하세요.' 
              onKeyDown={(e) => enterKey(e, onSearch)}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <button onClick={onSearch}>검색</button>
          </div>
          {isAdmin && <button className='write' onClick={() => navigate('/notice/write')}>글쓰기</button>}
        </div>
        <div className="notice-content">
          {showNotice.length > 0 ? (
            <NoticeTable notice={showNotice} />
          ) : (
            <div style={{textAlign: 'center', margin: '40px 0'}}>
              <p>작성된 공지사항이 없습니다.</p>
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default NoticeList;