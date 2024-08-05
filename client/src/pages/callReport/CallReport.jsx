import React from 'react';
import Header from '../../components/header/Header'; 
import ReportList from './ReportList';
import './CallReport.css';

const App = () => {
  return (
    <div>
      <Header />
      <div className="reportContent">
        <ReportList />
      </div>
    </div>
  );
};

export default App;
