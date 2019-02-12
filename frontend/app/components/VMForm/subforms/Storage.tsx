import React from 'react';
import T from 'prop-types';
import { InputGroup, InputGroupAddon, InputGroupText } from 'reactstrap';
import Input from '../../../components/Input';
import {AvField, AvGroup, AvFeedback } from 'availity-reactstrap-validation';
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import {faDatabase} from "@fortawesome/free-solid-svg-icons";
import {useQuery} from "react-apollo-hooks";
import {StorageList} from "../../../generated-models";
import formatBytes from "../../../utils/sizeUtils";

function Template({selected, onChange }) {
  const {data } = useQuery<StorageList.Query>(StorageList.Document);
  const storages = data.srs;

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
        id="storage"
        name="storage"
        onChange={onChange}
        value={selected}
        >
        <option value="">Select storage backend for your virtual machine</option>
        {
          storages.map(storage =>
            <option key={storage.uuid} value={storage.uuid}>{`${storage.nameLabel} (available ${formatBytes(storage.spaceAvailable, 2)}`}</option>)
        }
      </Input>
      <AvFeedback>Select a storage to install on</AvFeedback>
    </InputGroup>
    </AvGroup>
  );
}


export default Template;
