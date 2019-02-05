/**
*
* StartButton
*
*/

import React from 'react';
// import styled from 'styled-components';
import FontAwesomeIcon from '@fortawesome/react-fontawesome';
import faPlay from '@fortawesome/fontawesome-free-solid/faPlay';
import {Button} from 'reactstrap';


function StartButton(props) {
  return (
    <Button color="primary" {...props}>
      <FontAwesomeIcon icon={faPlay}/>
    </Button>
  );
}

StartButton.propTypes = {...Button.propTypes
};

export default StartButton;
