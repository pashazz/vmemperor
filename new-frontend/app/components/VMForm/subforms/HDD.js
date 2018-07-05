import React from 'react';
import T from 'prop-types';


import classNames from 'classnames';

function validate(hdd) {
  if (hdd < 9 || hdd > 500) {
    return 'should be between 9 and 500';
  }
  return '';
}

function HDD({ hdd, onChange, className, touched }) {
  const validation = validate(hdd);
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
  );
}

HDD.propTypes = {
  hdd: T.any.isRequired,
  touched: T.bool.isRequired,
  onChange: T.func.isRequired,
  className: T.string,
};

export default HDD;
