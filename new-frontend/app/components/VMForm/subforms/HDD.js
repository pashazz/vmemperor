import React from 'react';
import T from 'prop-types';
import { InputGroup, InputGroupAddon, InputGroupText } from 'reactstrap';
import Input from 'components/Input';
import {AvGroup} from 'availity-reactstrap-validation';
import faHdd from '@fortawesome/fontawesome-free-solid/faHdd';
import FontAwesomeIcon from '@fortawesome/react-fontawesome';

function HDD({ hdd, onChange })
{
  /* return (

      <div className="input-group">
        <span className="input-group-addon"><i className="icon-hdd"></i></span>
        <input
          type="number"
          className="form-control"
          id="hdd"
          name="hdd"
          min="9"
          value={hdd}
          onChange={onChange}
        />
        <span className="input-group-addon">GB</span>
      </div>
      { errorText }
    </div>
  ); */
  return (
    <AvGroup>
      <InputGroup>
        <InputGroupAddon style={{ 'line-height': '1!important' }} addonType="prepend">
          <InputGroupText style={{ height: '100%' }}>
            <FontAwesomeIcon icon={faHdd} />
          </InputGroupText>
        </InputGroupAddon>
        <Input
          type="number"
          validate={{ min: { value: 1 } }}
          id="hdd"
          name="hdd"
          value={hdd}
          onChange={onChange}
        />
        <InputGroupAddon addonType="append" style={{ 'line-height': '1!important' }} >
          <InputGroupText>
         GB
       </InputGroupText>
        </InputGroupAddon>
      </InputGroup>
    </AvGroup>
  );
}

HDD.propTypes = {
  hdd: T.any.isRequired,
  touched: T.bool.isRequired,
  onChange: T.func.isRequired,
  className: T.string,
};

export default HDD;
