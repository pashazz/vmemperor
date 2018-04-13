import React, { PropTypes as T } from 'react';
import classNames from 'classnames';

function validate(password, password2) {
  if (password.length < 4) {
    return 'Password should have at least 4 symbols';
  }
  if (password !== password2) {
    return 'Passwords should match';
  }
  return '';
}

function Passwords({ password, password2, onChange, touched }) {
  const validation = validate(password, password2);
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
        <span className="input-group-addon"><i className="icon-password"></i></span>
        <input
          required
          type="password"
          className="form-control input"
          placeholder="Choose password for your VM"
          data-minlength="6"
          id="password"
          name="password"
          value={password}
          onChange={onChange}
        />
        <span className="input-group-addon"><i className="icon-password"></i></span>
        <input
          required
          type="password"
          className="form-control input"
          placeholder="Confirm password"
          id="password2"
          name="password2"
          value={password2}
          onChange={onChange}
        />
      </div>
      { errorText }
    </div>
  );
}

Passwords.propTypes = {
  password: T.string.isRequired,
  password2: T.string.isRequired,
  touched: T.bool,
  onChange: T.func.isRequired,
};

export default Passwords;
