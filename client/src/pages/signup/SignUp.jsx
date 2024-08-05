import { useNavigate } from 'react-router-dom';
import React, { useState } from 'react';

// functions
import { blockSpace } from '../../utils/keyboard';
import { isValidEmail } from '../../utils/utils';
import { checkCode, emailCheck, idCheck, sendCode, signup } from '../../apis/user';
import { errorWithoutBtn, successWithoutBtn, warningWithoutBtn } from '../../utils/swal';

// css
import './SignUp.css';
import { BackgroundVideo1, FullContainer, GoBackBtn } from '../../components/CommonStyles';

function Signup() {
  const navigate = useNavigate();

  const [id, setId] = useState('');
  const [idDuplicated, setIdDuplicated] = useState(false);

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const [code, setCode] = useState('');
  const [confirmed, setConfirmed] = useState(false); // 이메일 인증 완료 여부
  const [authNumVisible, setAuthNumVisible] = useState(false);
   
  // 아이디 중복 검사
  const onIdChange = async (e) => {
    setId(e.target.value);

    const res = await idCheck(e.target.value);
    setIdDuplicated(!res);
  };

  // 이메일 인증 버튼 클릭
  const onEmailClick = async () => {
    if (email == '') return;

    // 이메일 유효성 검사
    const valid = isValidEmail(email);
    if (!valid) {
      warningWithoutBtn('이메일 주소가 올바르지 않습니다.');
      return;
    }
    
    // 이메일 중복 검사
    const res = await emailCheck(email);
    if (res) {
      const res = await sendCode(email);
      if (res) setAuthNumVisible(true);
    } else errorWithoutBtn('이미 가입된 이메일입니다.');
  }

  // 인증 코드 확인
  const onClickAuthBtn = async () => {
    const res = await checkCode(email, code);
    if (res) {
      successWithoutBtn('인증이 완료되었습니다.', '가입하기 버튼을 눌러 가입을 완료해주세요.', () => {});
      setConfirmed(true);
    }
  }
  
  // 가입하기 버튼
  const onSubmit = async () => {
    if (!name || !id || !password || !confirmPassword || !email) {
      warningWithoutBtn('모든 정보를 입력해주세요.');
      return;
    } else if (!confirmed) {
      warningWithoutBtn('이메일 인증을 완료해주세요.');
      return;
    } else if (password !== confirmPassword) {
      errorWithoutBtn('비밀번호가 일치하지 않습니다.')
      return;
    }

    const res = await signup(id, name, email, password);
    if (res) successWithoutBtn('회원가입에 성공하였습니다.', '로그인 페이지로 이동합니다.', () => navigate('/login'));
  };

  return (
    <FullContainer>
      <div className="signupContainer">
        <GoBackBtn />
        <BackgroundVideo1 />
        <div className="backContainer">
          <h4>회원가입</h4>
            <form>
              <div>
                <div className="inlineFieldContainer">
                  <div className="fieldContainer">
                    <p><label htmlFor="name">name</label></p>
                    <input placeholder="이름" 
                      value={name} 
                      onChange={(e) => setName(e.target.value)} 
                      onKeyDown={blockSpace} 
                    />
                  </div>
                  <div className="fieldContainer">
                    <p><label htmlFor="id">id</label></p>
                    <input 
                      value={id}
                      placeholder="아이디"
                      onChange={onIdChange}
                      onKeyDown={blockSpace}
                    />
                    <div className='msg' style={{color: idDuplicated ? 'red' : 'green'}}>
                      { id && (idDuplicated ? '이미 사용중인 아이디입니다.' : '사용 가능한 아이디입니다.')}
                    </div>
                  </div>
                </div>
                <div>
                  <div className="fieldContainer">
                    <label htmlFor="password">pw</label>
                    <input type="password" 
                      placeholder="비밀번호" 
                      value={password} 
                      onChange={(e) => setPassword(e.target.value)} 
                      onKeyDown={blockSpace}
                    />
                    <input type="password" 
                      placeholder="비밀번호 재확인" 
                      value={confirmPassword} 
                      onChange={(e) => setConfirmPassword(e.target.value)} 
                      onKeyDown={blockSpace} 
                    />
                  </div>
                </div>
                <div>
                  <div style={{paddingTop: '10px'}}>
                    <label htmlFor="email">e-mail</label>
                    <div className='emailContainer'>
                      <input
                        placeholder="이메일" 
                        onChange={(e) => setEmail(e.target.value)}
                        onKeyDown={blockSpace}
                      />
                      <button type="button" onClick={onEmailClick}>인증</button>
                    </div>
                  </div>
                  {authNumVisible &&
                  <div className="emailContainer">
                    <input 
                      placeholder="인증번호" 
                      value={code} 
                      onChange={(e) => setCode(e.target.value)}
                      onKeyDown={blockSpace}
                    />
                    <button type="button" onClick={onClickAuthBtn}>확인</button>
                  </div>}
                </div>
              </div>
            </form>
          <button type="button" className="submitBtn" onClick={onSubmit}>가입하기</button>
        </div>
      </div>
    </FullContainer>
  )
}

export default Signup;
