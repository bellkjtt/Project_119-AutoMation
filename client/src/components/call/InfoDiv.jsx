import styled from 'styled-components'

const DivBox = styled.div`
  text-align: left;
  margin-bottom: 15px;
`

const Title = styled.h4`
  margin-bottom: 5px;
`

const Text = styled.p`
  font-size: 15px;
`

const InfoDiv = ({title, text}) => {
  return (
    <DivBox>
      <Title>{title}</Title>
      <Text>{text}</Text>
    </DivBox>
  )
}

export default InfoDiv;