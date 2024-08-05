// 이메일 유효성 검사
export const isValidEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

// 한국 시간으로 변환
export const toKoreaTime = (time) => {
  const nyDate = new Date(time);
  return nyDate.toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' }).slice(0, -3);
}