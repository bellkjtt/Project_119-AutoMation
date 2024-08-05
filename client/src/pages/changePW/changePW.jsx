import React, { useState } from 'react';

// js
import { changepw, verifypw } from '../../apis/user';
import { isValidEmail } from '../../utils/utils';
import { errorWithoutBtn, successWithoutBtn } from '../../utils/swal';

// css
import './changePW.css';
import { BackgroundVideo1, GoBackBtn } from '../../components/CommonStyles';
import { FullContainer } from '../../components/CommonStyles';

function FindPW() {
  const [id, setId] = useState('');
  const [code, setCode] = useState('');
  const [email, setEmail] = useState('');
  const [isCode, setIsCode] = useState(false);

  // 메일 발송
  const onSend = async () => {
    if (email == '' || id == '') {
      errorWithoutBtn('모든 정보를 입력해주세요.');
      return;
    }
    if (!isValidEmail(email)) {
      errorWithoutBtn('이메일 형식이 올바르지 않습니다.');
      return;
    }

    const res = await changepw(id, email);
    if (res) {
      setIsCode(true);
      successWithoutBtn('인증번호가 발송되었습니다.', '5분 안에 인증번호를 입력해주세요.', () => {});
    }
  };

  // 인증번호 확인
  const onClick = async () => {
    const res = await verifypw(id, email, code);
    // 비밀번호 재설정 페이지로 이동
  }

  return (
    <FullContainer>
      <GoBackBtn />
      <BackgroundVideo1 />
      <div className='changepw-bg'>
        <div className='backContainer'>
          <h2 className='title'>비밀번호 변경</h2>
          <div className='formContainer'>
            <div className='description'>비밀번호 재설정을 위해 정보를 입력해 주십시오.</div>
            <div className='form'>
            <div className='changepw-inputGroup'>
                <label htmlFor="id">ID</label>
                <input 
                  id="id" 
                  value={id}
                  onChange={(e) => setId(e.target.value)}
                />
              </div>
              <div className='changepw-inputGroup'>
                <label htmlFor="email">e-mail</label>
                <input 
                  id="email" 
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
              <div className='changepw-inputGroup'>
                {isCode && <>
                  <label htmlFor="code">인증번호</label>
                  <input 
                    id="code" 
                    placeholder="인증번호" 
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                  />
                </>}
              </div>
              {isCode ? 
                <button type="button" onClick={onClick}>확인</button> :
                <button type="button" onClick={onSend}>인증메일 발송</button>
              }
            </div>
          </div>
      </div>
    </div>
    </FullContainer>
  );
}

export default FindPW;
