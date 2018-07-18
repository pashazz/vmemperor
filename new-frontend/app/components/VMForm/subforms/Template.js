import React from 'react';
import T from 'prop-types';
import { InputGroup, InputGroupAddon, Input, InputGroupText } from 'reactstrap';
import faDesktop from '@fortawesome/fontawesome-free-solid/faCompactDisc';
import FontAwesomeIcon from '@fortawesome/react-fontawesome';
import SelectList from './SelectList';
import IPT from 'react-immutable-proptypes';


function Template({ templates = [], onChange }) {
  if (templates.length === 0) {
    return null;
  }
  /*
  return (
    <div className="input-group" style={{ paddingBottom: '10px' }}>
      <span className="input-group-addon"><i className="icon-ubuntu"></i></span>
      <select
        className="form-control"
        id="template-select"
        name="template-select"
        onChange={onChange}
      >
        <option value="--">Select OS template for your virtual machine</option>
        {
          templates.map(template =>
            <option key={template.id} value={template.id}>{template.description}</option>)
        }
      </select>
    </div>
  );
  */
  /* return (
    <InputGroup style={ {padding: '10px'}}>
      <InputGroupAddon>
        <InputGroupText>
          <FontAwesomeIcon icon={faDesktop}/>
        </InputGroupText>
      </InputGroupAddon>
    <SelectList
      data={templates}
      onChange={onChange}
      placeholder="Select Template..."
      name="template"
      id="template"/>
    </InputGroup>
  );
} */

  return (
    <SelectList
      data={templates}
      onChange={onChange}
      placeholder="Select Template..."
      name="template"
      id="template"/>
  )
}

Template.propTypes = {
  templates: IPT.listOf(IPT.record).isRequired,
  isValid: T.bool,
  onChange: T.func.isRequired,
};

export default Template;
