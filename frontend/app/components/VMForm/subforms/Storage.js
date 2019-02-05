import React from 'react';
import T from 'prop-types';
import { InputGroup, InputGroupAddon, InputGroupText } from 'reactstrap';
import Input from 'components/Input';
import {AvField, AvGroup, AvFeedback } from 'availity-reactstrap-validation';
import FontAwesomeIcon from '@fortawesome/react-fontawesome';
import faDatabase from '@fortawesome/fontawesome-free-solid/faDatabase';
function Template({ storages = [], selected, onChange }) {
  if (storages.length === 0) {
    return null;
  }
  return (
    <AvGroup>
    <InputGroup>
      <InputGroupAddon style={ {"line-height": "1!important"}} addonType="prepend">
        <InputGroupText style = { { height: '100%'}}>
          <FontAwesomeIcon icon={faDatabase}/>
        </InputGroupText>
      </InputGroupAddon>
      <Input type="select"
        required
        className="form-control"
        id="storage-select"
        name="storage-select"
        onChange={onChange}
        value={selected}
        >
        <option value="">Select storage backend for your virtual machine</option>
        {
          storages.map(storage =>
            <option key={storage.id} value={storage.id}>{storage.description}</option>)
        }
      </Input>
      <AvFeedback>Select a storage to install on</AvFeedback>
    </InputGroup>
    </AvGroup>
  );
}

Template.propTypes = {
  storages: T.any.isRequired,
  selected: T.string.isRequired,
  isValid: T.bool,
  onChange: T.func.isRequired,
};

export default Template;
