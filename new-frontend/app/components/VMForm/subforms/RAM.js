import React from 'react';
import T from 'prop-types';

import classNames from 'classnames';

function validate(ram) {
  if (ram < 256 || ram > 100000) {
    return 'should be between 256 and 100000';
  }
  return '';
}

function RAM({ ram, onChange, className, touched }) {
  const validation = validate(ram);
  const isValid = validation === '';

  const mainClassName = classNames(className, 'form-group', {
    'has-success': touched && isValid,
    'has-error': touched && !isValid,
  });

  const errorText = touched && !isValid ?
    <span className="help-block">{ validation }</span> : null;

  return (
    <div className={mainClassName}>
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
  );
}

RAM.propTypes = {
  ram: T.any.isRequired,
  touched: T.bool,
  onChange: T.func.isRequired,
  className: T.string,
};

export default RAM;
