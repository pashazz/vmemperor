import React, { PropTypes as T } from 'react';

function Template({ templates = [], onChange }) {
  if (templates.length === 0) {
    return null;
  }
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
}

Template.propTypes = {
  templates: T.any.isRequired,
  isValid: T.bool,
  onChange: T.func.isRequired,
};

export default Template;
