import React from 'react';
import T from 'prop-types';

import classNames from 'classnames';

function validate(fullname) {
  if (fullname.length < 4) {
    return 'Full name should have at least 4 symbols';
  }
  return '';
}

function Fullname({ fullname, onChange, touched }) {
  const validation = validate(fullname);
  const isValid = validation === '';

  const mainClassName = classNames('form-group', {
    'has-success': touched && isValid,
    'has-error': touched && !isValid,
  });

  const errorText = touched && !isValid ?
    <span className="help-block">{ validation }</span> : null;

  return (
    <div className={mainClassName}>
      <div className="input-group">
        <span className="input-group-addon"><i className="icon-address"></i></span>
        <input
          type="text"
          className="form-control"
          placeholder="Your full name (e.g. John Smith)"
          id="fullname"
          name="fullname"
          required="true"
          value={fullname}
          onChange={onChange}
        />
      </div>
      { errorText }
    </div>
  );
}

Fullname.propTypes = {
  fullname: T.string.isRequired,
  touched: T.bool.isRequired,
  onChange: T.func.isRequired,
};

export default Fullname;
