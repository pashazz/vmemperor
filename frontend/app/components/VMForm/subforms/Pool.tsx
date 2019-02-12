import React from 'react';
import T from 'prop-types';
import {FormGroup, InputGroup, InputGroupAddon, InputGroupText} from 'reactstrap';
import Input from '../../../components/Input';
import {AvField, AvGroup, AvFeedback } from 'availity-reactstrap-validation';
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import {faServer} from "@fortawesome/free-solid-svg-icons";
import {useQuery} from "react-apollo-hooks";
import {PoolList, PoolListFragment} from "../../../generated-models";
import {SelectionProps} from "../index";


interface Props extends SelectionProps{
  pools : PoolList.Query;
}

const Pool = ({ pools, selected, onChange } : Props) => {
  return (<AvGroup>
    <InputGroup>
      <InputGroupAddon style={{"line-height": "1!important"}} addonType="prepend">
        <InputGroupText style={{height: '100%'}}>
          <FontAwesomeIcon icon={faServer}/>
        </InputGroupText>
      </InputGroupAddon>
      <Input type="select" id="pool" name="pool" onChange={onChange} required>
        <option value="">Select where to deploy instance</option>
        {
          pools.pools.map(pool =>
            (<option key={pool.uuid} value={pool.uuid}>{pool.nameDescription || pool.nameLabel || `Pool ${pool.uuid}`}</option>))
        }
      </Input>
      <AvFeedback>Select a pool to install on</AvFeedback>
    </InputGroup>
  </AvGroup>);
};

export default Pool;
