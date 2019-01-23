import React from 'react';
import T from 'prop-types';

import {AvField, AvGroup, AvInput, AvFeedback } from 'availity-reactstrap-validation';
import { InputGroup, InputGroupAddon, InputGroupText } from 'reactstrap';
import Input from 'components/Input';
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
        <Input
          type="number"
          validate={{max: {value: 32}, min: {value: 1}}}
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
