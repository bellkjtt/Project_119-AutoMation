import { useEffect, useState } from 'react';
import { Container, Image } from '../CommonStyles';
import { useLocation, useNavigate } from 'react-router-dom';

import './Header.css'
import styled from 'styled-components'

const CustomHeader = styled.header`
  height: 80px;
  font-size: 25px;
  font-weight: 900;
  min-width: 1200px;
  background-color: #D5D9DB62;
`

const NavContainer = styled.div`
  display: flex;
  align-items: center;
  justify-content: flex-end;
`

const Logo = styled.div`
  width: 80px;
  cursor: pointer;
`;

const Header = () => {
  const [loc, setLoc] = useState('')
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    setLoc(location.pathname);
  }, [])

  return (
    <CustomHeader>
      <Container>
        <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
          <Logo onClick={() => navigate('/')}>
            <Image src={`${process.env.PUBLIC_URL}/images/logoEX.png`} />
          </Logo>
          <NavContainer>  
            <div onClick={() => navigate('/main')} className={`menu ${loc == '/main' ? 'active' : ''}`}>대시보드</div>
            <div onClick={() => navigate('/callreport')} className={`menu ${loc == '/callreport' ? 'active' : ''}`}>신고내역</div>
            <div onClick={() => navigate('/notice')} className={`menu ${loc == '/notice' ? 'active' : ''}`}>공지사항</div>
          </NavContainer>
        </div>
      </Container>
    </CustomHeader>
  )
}

export default Header;
