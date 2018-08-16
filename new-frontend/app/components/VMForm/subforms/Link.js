import React, {Fragment} from 'react';
import T from 'prop-types';

import {AvField, AvGroup, AvInput, AvFeedback } from 'availity-reactstrap-validation';
function validateUser(value, ctx) {
  const {username} = ctx;
  if (username.length < 4) {
    return 'User name should have at least 4 symbols';
  }
  if (username.search(/[\s]/) !== -1) {
    return 'User name should have no spaces';
  }
  return true;
}

function validateHost(value, ctx) {
  const {hostname} = ctx;

  if (hostname.length < 4) {
    return 'Host name should have at least 4 symbols';
  }
  if (hostname.search(/[\s]/) !== -1) {
    return 'Host name should have no spaces';
  }
  return true;
}

function Link({ username, hostname, onChange, }) {
return (
  <Fragment>
  <AvField label="Username"
           name="username"
           id="username"
           value={username}
           onChange={onChange}
           placeholder="Your login for a new VM"
           validate={{myValidation: validateUser}}
           />
    <AvField label="Host name"
             name="hostname"
             id="hostname"
             value={hostname}
             onChange={onChange}
             placeholder="Your hostname for a new VM"
             validate={{myValidation: validateHost}}
    />

  </Fragment>
);


/*
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
  */
}

Link.propTypes = {
  username: T.string.isRequired,
  hostname: T.string.isRequired,
  touched: T.bool.isRequired,
  onChange: T.func.isRequired,
};

export default Link;
