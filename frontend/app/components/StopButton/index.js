/**
*
* StopButton
*
*/

import React from 'react';
// import styled from 'styled-components';
import FontAwesomeIcon from '@fortawesome/react-fontawesome';
import faStop from '@fortawesome/fontawesome-free-solid/faStop';
import {Button} from 'reactstrap';


function StopButton(props) {
  return (
    <Button color="primary" {...props}>
      <FontAwesomeIcon icon={faStop}/>
    </Button>
  );
}

StopButton.propTypes = {
  ...Button.propTypes
};

export default StopButton;
