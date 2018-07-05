/**
*
* ErrorCard
*
*/

import React from 'react';
// import styled from 'styled-components';
import { Card, CardImg, CardText, CardBody,
  CardTitle, CardSubtitle, Button } from 'reactstrap';



function ErrorCard({errorText, errorType, errorDetailedText, remove}) {
  return (
    <Card>
      <CardBody>
        <CardTitle>{errorText}</CardTitle>
        <CardSubtitle>{errorType}</CardSubtitle>
        <CardText>{errorDetailedText}</CardText>
        <Button onClick={remove}>Dismiss</Button>
      </CardBody>
    </Card>
  );
}

ErrorCard.propTypes = {

};

export default ErrorCard;
