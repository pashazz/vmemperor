import React from 'react';
import T from 'prop-types';

import {AvField, AvGroup, AvInput, AvFeedback } from 'availity-reactstrap-validation';
import { InputGroup, InputGroupAddon, InputGroupText, Input } from 'reactstrap';
import faMicrochip from '@fortawesome/fontawesome-free-solid/faMicrochip';
import FontAwesomeIcon from '@fortawesome/react-fontawesome';
const CPU = ({vcpus, onChange}) =>
{
  return (
    <AvGroup>
      <InputGroup>
        <InputGroupAddon style={ {"line-height": "1!important"}} addonType="prepend">
          <InputGroupText style = { { height: '100%'}}>
            <FontAwesomeIcon icon={faMicrochip}/>
          </InputGroupText>
        </InputGroupAddon>
        <AvInput
          type="number"
          validate={{max: {value: 16}, min: {value: 1}}}
          id="vcpus"
          name="vcpus"
          value={vcpus}
          onChange={onChange}
        />
         </InputGroup>
    </AvGroup>
  );
}

CPU.propTypes = {
  vcpus: T.any.isRequired,

  onChange: T.func.isRequired,
};

export default CPU;
