import styled from 'styled-components';
import { getUser } from '../../apis/user';
import { useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';

import Chart from './chart/Chart';
import UserComponent from "./UserComponent";
import NoticeComponent from './notice/NoticeComponent';
import CustomCalendar from './customCalendar/CustomCalendar';

const BodyContainer = styled.div`
  position: relative;
  width: 1200px;
  height: 800px;
  padding: 40px 0;
  margin: 0 auto;
`;

const CalendarWrapper = styled.div`
  position: absolute;
  width: 800px;
  height: 450px;
  background-color: #ffffffc0;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  border-radius: 15px;
  padding: 20px;
`;

const UserInfoContainer = styled.div`
  position: absolute;
  left: 850px;
  width: 350px;
  height: 200px;
  background-color: #ffffffc0;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  border-radius: 15px;
  padding: 20px;
`;

const StatsContainer = styled.div`
  position: absolute;
  top: 280px;
  left: 850px;
  width: 350px;
  height: 450px;
  background-color: #ffffffc0;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  border-radius: 15px;
  padding: 20px;
`;

const Body = () => {
  const navigate = useNavigate();
  const [name, setName] = useState('')

  useEffect(() => {
    getUser().then((res) => {
      if (res) setName(res.name);
      else navigate('/login');
    })
  }, [])

  return (
    <BodyContainer>
      <CalendarWrapper>
        <CustomCalendar />
      </CalendarWrapper>
      <UserInfoContainer>
        <UserComponent name={name}/>
      </UserInfoContainer>
      <NoticeComponent />
      <StatsContainer>
        <Chart />
      </StatsContainer>
    </BodyContainer>
  );
};

export default Body;
