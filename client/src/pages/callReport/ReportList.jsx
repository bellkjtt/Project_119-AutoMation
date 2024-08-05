import { useNavigate } from 'react-router-dom';
import React, { useEffect, useState } from 'react';

import { getReport } from '../../apis/report';
import { toKoreaTime } from '../../utils/utils';

const ReportList = () => {
  const reportsPerPage = 9;
  const navigate = useNavigate();

  const [reports, setReports] = useState([]);
  const [allReports, setAllReports] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  
  const fetchReports = () => {
    const filteredReports = allReports.filter(report => 
      report.fields.address_name.includes(searchQuery) ||
      report.fields.category.includes(searchQuery) ||
      report.fields.date.includes(searchQuery) ||
      report.fields.location.includes(searchQuery)
    );

    const indexOfLastReport = currentPage * reportsPerPage;
    const indexOfFirstReport = indexOfLastReport - reportsPerPage;
    const currentReports = filteredReports.slice(indexOfFirstReport, indexOfLastReport);
    setReports(currentReports);
  };
        
  const totalPages = Math.ceil(
    allReports.filter(report => 
      report.fields.address_name.includes(searchQuery) ||
      report.fields.category.includes(searchQuery) ||
      report.fields.date.includes(searchQuery) ||
      report.fields.location.includes(searchQuery)
    ).length / reportsPerPage
  );
    
  const handleNextPage = () => {
    setCurrentPage((prevPage) => Math.min(prevPage + 1, totalPages));
  };
    
  const handlePrevPage = () => {
    setCurrentPage((prevPage) => Math.max(prevPage - 1, 1));
  };
    
  const handleSearchChange = (event) => {
    setSearchTerm(event.target.value);
  };
    
  const handleSearchClick = () => {
    setSearchQuery(searchTerm);
    setCurrentPage(1); 
  };

  useEffect(() => {
    getReport().then((res) => res && setAllReports(res))
  }, [])

  useEffect(() => {
    fetchReports();
  }, [allReports, currentPage, searchQuery]);

  return (
    <div className='report-list-container'>
      <div className="report-list">
        <div className="searchBar">
          <input
            type="text"
            placeholder="검색어를 입력하세요."
            value={searchTerm}
            onChange={handleSearchChange}
            style={{ width: '80%' }}
          />
          <button onClick={handleSearchClick} style={{ width: '20%' }}>검색</button>
        </div>
        <div className='table-container'>
          <table>
            <thead>
              <tr>
                {/* 내용,녹취록은 상세페이지에서 */}
                <th>ID</th>
                <th style={{width: '180px'}}>시간</th>
                <th>주소</th>
                <th>장소</th>
                <th>분류</th>
                <th>구급/비구급</th>
              </tr>
            </thead>
            <tbody>
              {reports.length > 0 ? reports.map((report) => (
                <tr key={report.pk} onClick={() => navigate(`/reportdetails/${report.pk}`)}>
                  <td style={{textAlign: 'center'}}>{report.pk}</td>
                  <td style={{textAlign: 'center'}}>{toKoreaTime(report.fields.date)}</td>
                  <td>{report.fields.address_name}</td>
                  <td style={{textAlign: 'center'}}>{report.fields.place_name}</td>
                  <td style={{textAlign: 'center'}}>{report.fields.category}</td>
                  <td style={{textAlign: 'center'}}>{report.fields.emergency_type}</td>
                </tr>
              )) : 
              <tr>
                <td colSpan={6} style={{textAlign: 'center'}}>
                  접수된 신고내역이 없습니다.
                </td>
              </tr>}
            </tbody>
          </table>
          <div className="pagination">
            <button onClick={handlePrevPage} disabled={currentPage === 1}>
              &lt;
            </button>
            <span>{currentPage} / {totalPages}</span>
            <button onClick={handleNextPage} disabled={currentPage === totalPages}>
              &gt;
            </button>
          </div>
        </div>
      </div>
    </div>
    
  );
};

export default ReportList;
