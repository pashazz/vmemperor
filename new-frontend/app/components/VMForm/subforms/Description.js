import React from 'react';
import T from 'prop-types';

import classNames from 'classnames';

export function validate(val) {
  if (val.length < 10) {
    return 'Please provide meaningfull description';
  }
  return '';
}

function Description({ description, onChange, touched }) {
  const validation = validate(description);
  const isValid = validation === '';

  const mainClassName = classNames('form-group', {
    'has-success': touched && isValid,
    'has-error': touched && !isValid,
  });

  const errorText = touched ?
    <span className="help-block">{ validation }</span> : null;

  return (
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
}

Description.propTypes = {
  description: T.string.isRequired,
  onChange: T.func.isRequired,
  touched: T.bool.isRequired,
};

export default Description;
