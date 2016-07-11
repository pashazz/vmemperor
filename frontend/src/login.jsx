import React from 'react';
import SessionActions from './flux/session-actions';
import PoolStore from './flux/pool-store';
import Modal from './components/modal.jsx';

class LoginForm extends React.Component {
  constructor() {
    super();
    this.handleSubmit = this.handleSubmit.bind(this);
    this.handleChange = this.handleChange.bind(this);
    this.state = {};
  }

  handleSubmit(e) {
    e.preventDefault();
    SessionActions.auth(this.state);
  }

  handleChange(e) {
    var newState = {};
    newState[e.target.name] = e.target.value;
    this.setState(newState);
  }

  render() {
    return(
      <form role="form" onChange={this.handleChange} onSubmit={this.handleSubmit}>
        <div className="modal-body">
          <div className="form-inline">
            <div className="input-group">
              <div className="input-group-addon">Pool A</div>
              <input type="text" className="form-control" placeholder="Login" name="login0" />
              <input type="password" className="form-control" placeholder="Password" name="password0" />
            </div>
          </div>
          <br />
          <div className="form-inline">
            <div className="input-group">
              <div className="input-group-addon">Pool Z</div>
              <input type="text" className="form-control" placeholder="Login" name="login1" />
              <input type="password" className="form-control" placeholder="Password" name="password1" />
            </div>
          </div>
        </div>
        <br />
        <button type="submit" className="btn btn-lg btn-primary btn-block">Login</button>
      </form>
    );
  }
}

class LoginModal extends React.Component {
  render() {
    return (
      <Modal title="VM Emperor Login" show>
        <LoginForm />
      </Modal>
    );
  }
}

export default LoginModal;
