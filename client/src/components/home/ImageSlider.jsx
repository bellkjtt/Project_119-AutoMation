import React, { useEffect, useState } from 'react';

const images = [
  { src: '/images/homeimg1.jpg', link: 'https://www.nfa.go.kr/nfa/' },
  { src: '/images/homeimg2.jpg', link: 'https://www.police.go.kr/index.do' },
  { src: '/images/homeimg3.jpg', link: 'https://www.mois.go.kr/frt/a01/frtMain.do' },
  // 추가 이미지 경로와 링크
];

const ImageSlider = () => {
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIndex((prevIndex) => (prevIndex + 1) % images.length);
    }, 5000); // 5초마다 이미지 변경

    return () => clearInterval(interval);
  }, []);

  const handleClick = () => {
    const currentImage = images[currentIndex];
    window.open(currentImage.link, '_blank'); // 새 탭으로 링크 열기
  };

  return (
    <div style={{ width: '100%', height: '100%' }} onClick={handleClick}>
      <img src={images[currentIndex].src} alt="Slideshow" style={{ width: '100%', height: '100%', cursor: 'pointer' }} />
    </div>
  );
};

export default ImageSlider;
