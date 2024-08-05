import styled from 'styled-components'

const Background = styled.div`
  z-index: 5;
  top: 0;
  position: absolute;
  width: 100%;
  height: 100%;
  pointer-events: none;
  background-color: rgb(0, 0, 0, 0.5);
`

const Overlay = () => {
  return <Background></Background>
}

export default Overlay;