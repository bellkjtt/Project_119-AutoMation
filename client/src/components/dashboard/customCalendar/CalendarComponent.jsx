import React, { useState } from 'react';
import { Calendar, momentLocalizer } from 'react-big-calendar';
import moment from 'moment';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import styled from 'styled-components';

const localizer = momentLocalizer(moment);

const CalendarWrapper = styled.div`
  width: 100%;
  height: 100%;
  z-index: 2;

  .rbc-calendar {
    background-color: #f0f0f0;
    border-radius: 10px;
    padding: 10px;
    height: 100%;
    width: 100%;
  }

  .rbc-toolbar {
    background-color: #444;
    color: white;
    border-radius: 10px;
  }

  .rbc-header {
    background-color: #333;
    color: white;
    border-radius: 10px;
  }

  .rbc-day-bg {
    background-color: #eaeaea;
  }

  .rbc-today {
    background-color: #ffeb3b;
  }

  .rbc-event {
    background-color: #3174ad;
    color: white;
  }
`;

const CalendarComponent = () => {
  const [events, setEvents] = useState([]);

  const handleSelect = ({ start, end }) => {
    const title = window.prompt('New Event name');
    if (title) {
      setEvents([
        ...events,
        {
          start,
          end,
          title,
        },
      ]);
    }
  };

  return (
    <CalendarWrapper>
      <Calendar
        localizer={localizer}
        events={events}
        selectable
        onSelectSlot={handleSelect}
        defaultView="month"
      />
    </CalendarWrapper>
  );
};

export default CalendarComponent;
