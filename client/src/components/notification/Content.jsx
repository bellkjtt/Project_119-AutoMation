import styled from 'styled-components'
import { useEffect, useRef } from "react";

const ContentBox = styled.div`
  padding: 30px;
  border-radius: 20px;
  background-image: linear-gradient(180deg, #ffffff 0%, #ebedeed0 100%);
  box-shadow: rgba(51, 51, 51, 0.253) 0px 5px 15px;
  
  img {
    width: 100%;
  }
`

const Content = ({content}) => {
  const containerRef = useRef();

  useEffect(() => {
    if (content) {
      const parser = new DOMParser();
      const doc = parser.parseFromString(content, 'text/html');
      const fragment = document.createDocumentFragment();
      
      while (doc.body.firstChild) {
        fragment.appendChild(doc.body.firstChild);
      }
      
      if (containerRef.current) {
        containerRef.current.appendChild(fragment);
      }
    }
  }, [content])

  return (
    <ContentBox ref={containerRef}></ContentBox>
  )
}

export default Content;