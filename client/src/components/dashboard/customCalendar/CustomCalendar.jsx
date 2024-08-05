import { useState, useEffect } from 'react';
import { getDayLog } from '../../../apis/report';

import './CustomCalendar.css';
import Calendar from 'react-calendar';
import 'react-calendar/dist/Calendar.css';

const CustomCalendar = () => {
  const [date, setDate] = useState(new Date());
  const [data, setData] = useState([]);

  const formatDate = (date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };
  
  const tileContent = ({ date, view }) => {
    if (view === 'month') {
      const formattedDate = formatDate(date);
      const dateEntry = data.find(entry => entry.annotated_date === formattedDate);
  
      if (dateEntry) {
        const count = dateEntry.count;
        return <p className="custom-text">{count} 건</p>;
      }
    }
    return null;
  };

  useEffect(() => {
    getDayLog().then((res) => {
      if (res) setData(res);
    })
  }, [])

  return (
    <div className='calendar-box'>
      <Calendar
        onChange={setDate}
        value={date}
        tileContent={tileContent}
      />
    </div>)
}

export default CustomCalendar;