import React from 'react';
import T from 'prop-types';

import {AvField, AvGroup, AvInput, AvFeedback } from 'availity-reactstrap-validation';
import { InputGroup, InputGroupAddon, InputGroupText, Input } from 'reactstrap';
import icon  from '@fortawesome/fontawesome-free-solid/faUser';
import FontAwesomeIcon from '@fortawesome/react-fontawesome';


function Fullname({ fullname, onChange}) {



  return (
    <AvGroup>
      <InputGroup>
          <InputGroupAddon style={ {"line-height": "1!important"}} addonType="prepend">
         <InputGroupText style = { { height: '100%'}}>
           <FontAwesomeIcon icon={icon}/>
         </InputGroupText>
          </InputGroupAddon>
        <AvInput
          type="text"
          className="form-control"
          placeholder="Your full name (e.g. John Smith, optional)"
          id="fullname"
          name="fullname"
          value={fullname}
          onChange={onChange}
        />
      </InputGroup>
    </AvGroup>
  );
}

Fullname.propTypes = {
  fullname: T.string.isRequired,
  touched: T.bool.isRequired,
  onChange: T.func.isRequired,
};

export default Fullname;
