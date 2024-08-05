import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { getUser } from "../../apis/user";
import { deleteNotice, getNoticeById } from "../../apis/notification";

import './NoticePost.css'
import Header from "../../components/header/Header";
import Content from "../../components/notification/Content";


const NoticePost = () => {
  const {id} = useParams();
  const navigate = useNavigate();

  const [notice, setNotice] = useState([]);
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    getUser().then((res) =>{if (res.is_admin) setIsAdmin(true)})
    getNoticeById(id).then((res) => setNotice(res.fields));
  }, [])

  return <>
    <Header />
    <div className='notice-post-container'>
      <h2>{notice.title}</h2>
      <div className='desc' style={{marginTop: '30px'}}>
        <p>{notice.user_id}</p>
        <p>{notice.created_at && notice.created_at.slice(0, 10)}</p>
      </div>
      <div className='desc' style={{marginBottom: '30px'}}>
        {isAdmin && <>
          <button onClick={() => navigate(`/notice/write/${id}`)}>수정</button>
          <button onClick={() => deleteNotice(id)}>삭제</button>       
        </>}
      </div>
      <Content content={notice.content}/>
      <div className="list-button-container">
          <img 
            src="/images/list.png" 
            alt="목록" 
            className="toList-button" 
            onClick={() => navigate('/notice')}  
          />
          <p>목록으로</p>
        </div>
    </div>
    
  </>
}

export default NoticePost;