import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

const NoticeTable = ({notice}) => {
  const n = 9;
  const navigate = useNavigate();

  const [noticeByPage, setNoticeByPage] = useState([])
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPage, setTotalPage] = useState(Math.ceil(notice.length / n))

  const handlePrevPage = () => {
    setCurrentPage((prevPage) => Math.max(prevPage - 1, 1));
  };
  
  const handleNextPage = () => {
    setCurrentPage((prevPage) => Math.min(prevPage + 1, totalPage));
  };

  useEffect(() => {
    const indexOfLastNotice = currentPage * n;
    const indexOfFirstNotice = indexOfLastNotice - n;
    const currentNtocie = notice.slice(indexOfFirstNotice, indexOfLastNotice);
    setNoticeByPage(currentNtocie);

    setTotalPage(Math.ceil(notice.length / n));
  }, [notice, currentPage])

  return (
    <div className='container'>
      <table>
        <thead>
          <tr>
            <th style={{width: '50px'}}>ID</th>
            <th>제목</th>
            <th style={{width: '100px'}}>작성자</th>
            <th style={{width: '140px'}}>날짜</th>
          </tr>
        </thead>
        <tbody>
          {noticeByPage.map((n, index) => (
            <tr key={index} onClick={() => navigate('/notice/' + n.pk)}>
              <td style={{textAlign: 'center'}}>{n.pk}</td>
              <td>{n.fields.title}</td>
              <td style={{textAlign: 'center'}}>{n.fields.user_id}</td>
              <td style={{textAlign: 'center'}}>{n.fields.created_at.slice(0, 10)}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="pagination">
        <button onClick={handlePrevPage} disabled={currentPage === 1}>
        &lt;
        </button>
        <span>{currentPage} / {totalPage}</span>
        <button onClick={handleNextPage} disabled={currentPage === totalPage}>
        &gt;
        </button>
        </div>
    </div>
  );
};

export default NoticeTable;
