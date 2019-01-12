/**
*
* RecycleBinButton
*
*/

import React from 'react';
// import styled from 'styled-components';
import FontAwesomeIcon from '@fortawesome/react-fontawesome';
import faTrashAlt from '@fortawesome/fontawesome-free-solid/faTrashAlt';
import {Button} from 'reactstrap';


function RecycleBinButton(props) {
  return (
    <Button color="danger" {...props}>
      <FontAwesomeIcon icon={faTrashAlt}/>
    </Button>

  );
}

RecycleBinButton.propTypes = {...Button.propTypes

};

export default RecycleBinButton;
