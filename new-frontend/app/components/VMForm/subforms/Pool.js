import React from 'react';
import T from 'prop-types';
import { InputGroup, InputGroupAddon, InputGroupText } from 'reactstrap';
import Input from 'components/Input';
import {AvField, AvGroup, AvFeedback } from 'availity-reactstrap-validation';
import faServer from '@fortawesome/fontawesome-free-solid/faServer';
import FontAwesomeIcon from '@fortawesome/react-fontawesome';


const Pool = ({ pools, selected, onChange }) =>
  <AvGroup>
  <InputGroup>
    <InputGroupAddon style={ {"line-height": "1!important"}} addonType="prepend">
      <InputGroupText style = { { height: '100%'}}>
        <FontAwesomeIcon icon={faServer}/>
      </InputGroupText>
    </InputGroupAddon>
    <Input type="select" id="pool-select" name="pool-select" onChange={onChange} required>
      <option value="">Select where to deploy instance</option>
      {
        pools.map(pool =>
          <option key={pool.uuid} value={pool.uuid}>{pool.description}</option>)
      }
    </Input>
    <AvFeedback>Select a pool to install on</AvFeedback>
  </InputGroup>
  </AvGroup>;

Pool.propTypes = {
  pools: T.any.isRequired,
  selected: T.string.isRequired,
  isValid: T.bool,
  onChange: T.func.isRequired,
};

export default Pool;
