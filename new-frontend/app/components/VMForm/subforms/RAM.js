import React from 'react';
import T from 'prop-types';

import Input from 'components/Input';
import {AvField, AvGroup, AvFeedback } from 'availity-reactstrap-validation';
import { InputGroup, InputGroupAddon, InputGroupText } from 'reactstrap';
import faMemory from '@fortawesome/fontawesome-free-solid/faMemory';
import FontAwesomeIcon from '@fortawesome/react-fontawesome';

function validate(ram) {
  if (ram < 256 || ram > 100000) {
    return 'should be between 256 and 100000';
  }
  return '';
}

function RAM({ ram, onChange }) {


 /* return (
    <div>
      <div className="input-group">
        <span className="input-group-addon"><i className="icon-ram"></i></span>
        <input
          type="number"
          className="form-control"
          id="ram"
          name="ram"
          min="256"
          value={ram}
          onChange={onChange}
        />
        <span className="input-group-addon">MB</span>
      </div>
      { errorText }
    </div>
  ); */

 return (
   <AvGroup>
     <InputGroup>
       <InputGroupAddon style={ {"line-height": "1!important"}} addonType="prepend">
         <InputGroupText style = { { height: '100%'}}>
           <FontAwesomeIcon icon={faMemory}/>
         </InputGroupText>
       </InputGroupAddon>
     <Input
       type="number"
       validate={{max: {value: 100000}, min: {value: 256}}}
       id="ram"
       name="ram"
       value={ram}
       onChange={onChange}
     />
     <InputGroupAddon addonType="append" style={ {"line-height": "1!important"}} >
       <InputGroupText>
         MB
       </InputGroupText>
     </InputGroupAddon>
     <AvFeedback>
       RAM size is between 256 and 100000 megabytes
     </AvFeedback>
     </InputGroup>
   </AvGroup>
 );
}

RAM.propTypes = {
  ram: T.any.isRequired,
  touched: T.bool,
  onChange: T.func.isRequired,
  className: T.string,
};

export default RAM;
