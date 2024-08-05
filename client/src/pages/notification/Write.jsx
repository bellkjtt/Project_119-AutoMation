import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { useNavigate } from "react-router-dom";

import { getUser } from "../../apis/user";
import { cancelAlert } from "../../utils/swal";
import { getNoticeById, writeNotification, editNotice } from "../../apis/notification";

import styled from 'styled-components'
import Header from "../../components/header/Header";
import Editor from "../../components/notification/Editor";

const WriteBox =  styled.div`
  width: 900px;
  margin: 0 auto;
`

const Write = () => {
  const {id} = useParams();
  const navigate = useNavigate();

  const [userid, setUserId] = useState('');
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');

  const onChangeTitle = (title) => {
    setTitle(title);
  }

  const onChangeContent = (content) => {
    setContent(content);
  }

  // 글쓰기 취소
  const cancelWriting = () => {
    cancelAlert('취소하시겠습니까?', '', '예', '아니요', () => navigate('/notice'))
  }

  useEffect(() => {
    getUser().then((res) => setUserId(res.id));

    // 수정을 위한 값 불러오기
    if (id) {
      getNoticeById(id).then((res) => {
        setTitle(res.fields.title);
        setContent(res.fields.content);
      })
    }
  }, [])

  return <>
    <Header />
    <div style={{minWidth: '1040px', marginBottom: '50px'}}>
      <WriteBox>
        <Editor title={title} content={content} onChangeTitle={onChangeTitle} onChangeContent={onChangeContent} />
        <div className='btns'>
          <button onClick={cancelWriting}>취소</button>
          {id ? 
            <button onClick={() => editNotice(id, userid, title, content)}>수정</button>  :
            <button onClick={() => writeNotification(userid, title, content)}>글쓰기</button>
          }
        </div>
      </WriteBox>
    </div>
  </>
}

export default Write;