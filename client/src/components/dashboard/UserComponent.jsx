import React from 'react';
import styled from 'styled-components';
import { useNavigate } from 'react-router-dom';
import { logout } from '../../apis/user';
import { warningWithoutBtn } from '../../utils/swal';

const UserComponentContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  padding: 10px;
  background-color: #ffffffc0;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  border-radius: 10px;
  width: 100%;
  height: 100%;
`;

const UserName = styled.h3`
  font-size: 20px;
  padding: 0 10px;
`;

const CenterName = styled.h3`
  color: rgb(15,15,15);
  font-size: 18px;
  padding: 0 10px;
`;

const ButtonGroupContainer = styled.div`
  display: flex;
  justify-content: center;
  gap: 10px;
  width; 100%;
  margin-bottom: 20px;
`;

const EditButton = styled.button`
  background-color: #FF5A5A;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  flex: 1;

  &:hover {
    background-color: #FF7A7A;
  }
`;

const LogoutButton = styled.button`
  background-color: #ebedee;
  color: black;
  padding: 10px 20px;
  border: none;
  border-radius: 20px;
  cursor: pointer;

  &:hover {
    background-color: #E0E0E0;
  }
`;

const UserComponent = ({name}) => {
  const onEdit = () => {
    warningWithoutBtn('이 기능은 추후 제공 예정입니다.', '개인정보 변경이 필요할 경우 관리자에게 문의 바랍니다.');
  }

  return (
    <UserComponentContainer>
      <div style={{display: 'flex', alignItems: 'center', marginTop: '10px'}}>
        <div style={{width: '180px'}}>
          <UserName>{name}</UserName> 
          <CenterName>분당 119 안전센터</CenterName> 
        </div>
        <img src="images\userIcon.png" alt="User Icon" width="60" height="60" />
      </div>
      <ButtonGroupContainer>
        <EditButton onClick={onEdit}>정보수정</EditButton>
        <LogoutButton onClick={logout}>로그아웃</LogoutButton>
      </ButtonGroupContainer>
    </UserComponentContainer>
  );
};

export default UserComponent;
