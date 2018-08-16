import React, {PureComponent, Fragment} from 'react';
import T from 'prop-types';
import { InputGroup, InputGroupAddon, InputGroupText, Input } from 'reactstrap';
import {AvField, AvGroup, AvInput, AvFeedback } from 'availity-reactstrap-validation';
import faPassword from '@fortawesome/fontawesome-free-solid/faKey';
import FontAwesomeIcon from '@fortawesome/react-fontawesome';
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

/**
 * Next time use validate={{match:{value:'originalId'}} and validate={{minLength: {value: 10}}
 */
class Passwords extends PureComponent {
  static propTypes = {
    password: T.string.isRequired,
    password2: T.string.isRequired,
    onChange: T.func.isRequired,
    formRef: T.any.isRequired,
  };

//function Passwords({ password, password2, onChange, formRef }) {
constructor(props)
{
  super(props);
  this.validate1 = this.validate1.bind(this);
  this.validate2 = this.validate2.bind(this);
  this.validator = this.validator.bind(this);
  this.onChange = this.onChange.bind(this);

}
validate1()
{
  this.props.formRef.validateInput('password');
}

validate2()
{
  this.props.formRef.validateInput('password2');
}

validator(value, ctx)
{
  if (ctx.password.length < 4)
  {
    return "Password should have at least 4 symbols";
  }
  if (ctx.password !== ctx.password2)
  {
    return "Passwords do not match";
  }
  return true;
}

onChange = (id) => (option) =>
{
  if (id === '1')
  {
    this.validate2();
  }
  else if (id === '2')
  {
    this.validate1();
  }
  this.props.onChange(option);
};

render()
{
  return (
    <Fragment>
    <AvGroup>
      <InputGroup>
        <InputGroupAddon style={ {"line-height": "1!important"}} addonType="prepend">
          <InputGroupText style = { { height: '100%'}}>
            <FontAwesomeIcon icon={faPassword}/>
          </InputGroupText>
        </InputGroupAddon>

      <AvInput
        type="password"
        required
        validate={{myValidation: this.validator}}
        id="password"
        placeholder="Choose password"
        name="password"
        value={this.props.password}
        onChange={this.onChange('1')}
      />
        <InputGroupAddon style={ {"line-height": "1!important"}} addonType="prepend">
          <InputGroupText style = { { height: '100%'}}>
            <FontAwesomeIcon icon={faPassword}/>
          </InputGroupText>
        </InputGroupAddon>
      <AvInput
        type="password"
        required
        validate={{myValidation: this.validator}}
        placeholder="Repeat password"
        id="password2"
        name="password2"
        value={this.props.password2}
        onChange={this.onChange('2')}
      />
        <AvFeedback>
          Passwords should match and have at least 4 symbols
        </AvFeedback>
      </InputGroup>

      </AvGroup>
    </Fragment>
  );
}


/*
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
  ); */


}


export default Passwords;
