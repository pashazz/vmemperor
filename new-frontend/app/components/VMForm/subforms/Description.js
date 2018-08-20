import React from 'react';
import T from 'prop-types';



import {AvField, AvGroup, AvFeedback } from 'availity-reactstrap-validation';
import { InputGroup, InputGroupAddon, InputGroupText } from 'reactstrap';
import icon  from '@fortawesome/fontawesome-free-solid/faStickyNote';
import FontAwesomeIcon from '@fortawesome/react-fontawesome';
import Input from 'components/Input';
function Description({ description, onChange }) {

  return (
   <AvGroup>
     <InputGroup>
       <InputGroupAddon style={ {"line-height": "1!important"}} addonType="prepend">
         <InputGroupText style = { { height: '100%'}}>
           <FontAwesomeIcon icon={icon}/>
         </InputGroupText>
       </InputGroupAddon>
     <Input
       type="textarea"
       id="name_description"
       name="name_description"
       style={{ resize: 'vertical' }}
       value={description}
       placeholder="Provide a description (optional)"
       onChange={onChange}

     />
     </InputGroup>
   </AvGroup>
  )
  /*return (
    <div className={mainClassName} style={{ paddingBottom: '10px' }}>
      <div className="input-group">
        <span className="input-group-addon"><i className="icon-noteslist" style={{ fontSize: '28px' }}></i></span>
        <textarea
          required
          type="text"
          className="form-control input"
          placeholder="What do you want to do with this virtual machine?"
          id="name_description"
          name="name_description"
          style={{ resize: 'vertical' }}
          value={description}
          onChange={onChange}
        />
      </div>
      { errorText }
    </div>
  );
  */
}

Description.propTypes = {
  description: T.string.isRequired,
  onChange: T.func.isRequired,
  touched: T.bool.isRequired,
};

export default Description;
