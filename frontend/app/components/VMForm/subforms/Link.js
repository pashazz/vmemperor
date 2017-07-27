import React, { PropTypes as T } from 'react';
import classNames from 'classnames';

function validate(username, hostname) {
  if (username.length < 4) {
    return 'User name should have at least 4 symbols';
  }
  if (username.search(/[\s]/) !== -1) {
    return 'User name should have no spaces';
  }
  if (hostname.length < 4) {
    return 'Host name should have at least 4 symbols';
  }
  if (hostname.search(/[\s]/) !== -1) {
    return 'Host name should have no spaces';
  }
  return '';
}

function Link({ username, hostname, onChange, touched }) {
  const validation = validate(username, hostname);
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
        <span className="input-group-addon"><i className="icon-user"></i></span>
        <input
          type="text"
          className="form-control"
          placeholder="Your login for new VM"
          id="username"
          name="username"
          value={username}
          onChange={onChange}
        />
        <span className="input-group-addon"><i className="icon-at"></i></span>
        <input
          required
          type="text"
          className="form-control"
          placeholder="Choose hostname for your VM"
          id="hostname"
          name="hostname"
          value={hostname}
          onChange={onChange}
        />
        <span className="input-group-addon">.at.ispras.ru</span>
      </div>
      { errorText }
    </div>
  );
}

Link.propTypes = {
  username: T.string.isRequired,
  hostname: T.string.isRequired,
  touched: T.bool.isRequired,
  onChange: T.func.isRequired,
};

export default Link;
