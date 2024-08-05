import './CallModal.css'
import InfoDiv from './InfoDiv';
import KakaoMap from './KaKaoMap';
import { useNavigate } from 'react-router-dom';
import { toKoreaTime } from '../../utils/utils';

const CallModal = ({address, place, time, content, where, lat, lng}) => {
  const navigate = useNavigate();

  return <>
    <div className='call-modal'>
      <div>
        <h3>신고가 정상적으로 접수되었습니다.</h3>
        <div style={{display: 'flex', gap: '15px'}}>
          <div style={{width: '50%'}}>
            <InfoDiv title='주소' text={address} />
            <InfoDiv title='장소' text={place} />
            <InfoDiv title='신고시각' text={toKoreaTime(time)} />
            <InfoDiv title='접수 내용' text={content} />
            <InfoDiv title='유관 기관' text={where} />
          </div>
          <div className='map'>
            <KakaoMap lat={lat} lng={lng} />
          </div>
        </div>
        <button onClick={() => navigate('/')}>홈 화면으로 나가기</button>
      </div>
    </div>
  </>
}

export default CallModal;