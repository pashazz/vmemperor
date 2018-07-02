import React from 'react';
import T from 'prop-types';
import { InputGroup, InputGroupAddon, InputGroupText, Input } from 'reactstrap';
import faServer from '@fortawesome/fontawesome-free-solid/faServer';
import FontAwesomeIcon from '@fortawesome/react-fontawesome';


const Pool = ({ pools, selected, onChange }) =>
  /*
<div className="input-group" style={{ paddingBottom: '10px' }}> *
    <span className="input-group-addon"><i className="icon-servers"></i></span>
    <select
      className="form-control input"
      id="pool-select"
      name="pool-select"
      value={selected}
      onChange={onChange}
    >
      <option value="">Select where to deploy instance</option>
      {
        pools.map(pool =>
          <option key={pool.uuid} value={pool.uuid}>{pool.description}</option>)
      }
    </select>
  </div>;
*/
  <InputGroup style={ {padding: '0px 20px 0px 20px', height: '100%'}}>
    <InputGroupAddon style={ {"line-height": "1!important"}}>
      <InputGroupText style = { { height: '100%'}}>
        <FontAwesomeIcon icon={faServer}/>
      </InputGroupText>
    </InputGroupAddon>
    <Input type="select" id="pool-select" name="pool-select" onChange={onChange}>
      <option value="">Select where to deploy instance</option>
      {
        pools.map(pool =>
          <option key={pool.uuid} value={pool.uuid}>{pool.description}</option>)
      }
    </Input>
  </InputGroup>;
Pool.propTypes = {
  pools: T.any.isRequired,
  selected: T.string.isRequired,
  isValid: T.bool,
  onChange: T.func.isRequired,
};

export default Pool;
