import axios from 'axios';
import { cancelAlert, errorWithoutBtn, successWithoutBtn } from '../utils/swal';

const access = localStorage.getItem('access');
const SERVER_URL = process.env.REACT_APP_POST_SERVER_URL

// 전체 공지사항 가져오기
export const getNotice = () => {
  return axios.get(SERVER_URL + 'postlist/', {
    headers: {
      Authorization: access
    }
  })
  .then((res) => {return res.data})
  .catch((error) => console.log(error))
}

// 아이디에 해당하는 공지사항 가져오기
export const getNoticeById = (id) => {
  return axios.get(`${SERVER_URL}postdetail/${id}/`, {
    headers: {
      Authorization: access
    }
  })
  .then((res) => {return res.data})
  .catch((error) => console.log(error))

}

// 공지사항 글쓰기
export const writeNotification = (user_id, title, content) => {
  axios.post(SERVER_URL + 'postcreate/', {user_id, title, content}, {
    headers: {
      Authorization: access
    }
  })
  .then(() => successWithoutBtn('공지사항이 등록되었습니다.', '', () => window.location.href = '/notice'))
  .catch((error) => {
    const msg = error.response.data.message;
    if (msg.includes('DATA_UPLOAD_MAX')) errorWithoutBtn('파일 최대 용량을 초과하였습니다.');
    console.log('공지사항 글쓰기', error)
})
}

// 수정
export const editNotice = (id, user_id, title, content) => {
  axios.post(`${SERVER_URL}postedit/${id}/`, {user_id, title, content}, {
    headers: {
      Authorization: access
    }
  })
  .then((res) => successWithoutBtn('공지사항이 수정되었습니다.', '', () => window.location.href = '/notice/' + id))
  .catch((error) => console.log(error))
}

// 삭제
export const deleteNotice = (id) => {
  const onDelete = () => {
    axios.delete(`${SERVER_URL}postdelete/${id}/`, {
      headers: {
        Authorization: access
      }
    })
    .then((res) => {window.location.href = '/notice'})
    .catch((error) => console.log(error))
  }
  cancelAlert('정말 삭제하시겠습니까?', '', '예', '아니요', onDelete);
}