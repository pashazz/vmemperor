import React from 'react';
import SessionActions from './flux/session-actions';
import PoolStore from './flux/pool-store';
import Modal from './components/modal.jsx';
import VMAPI from'./api/vmemp-api';

class PoolLogin extends React.Component {
  render() {
    const { description, index } = this.props;
    return (
      <div className="form-inline" style={{marginBottom: '10px'}}>
        <div className="input-group">
          <div className="input-group-addon">{description}</div>
          <input type="text" className="form-control" placeholder="Login" name={`login${index}`} />
          <input type="password" className="form-control" placeholder="Password" name={`password${index}`} />
        </div>
      </div>
    );
  }
}

class LoginForm extends React.Component {
  constructor() {
    super();
    this.handleSubmit = this.handleSubmit.bind(this);
    this.handleChange = this.handleChange.bind(this);
    this.state = {
      pools: [],
      login: {}
    };
  }

  componentWillMount() {
    VMAPI.pool.index()
      .then(pools => this.setState({pools}));
  }

  handleSubmit(e) {
    e.preventDefault();
    SessionActions.auth(this.state.login);
  }

  handleChange(e) {
    let loginState = this.state.login;
    loginState[e.target.name] = e.target.value;
    this.setState({login: loginState});
  }

  render() {
    return(
      <form role="form" onChange={this.handleChange} onSubmit={this.handleSubmit}>
        <div className="modal-body">
          {
            this.state.pools.map((pool, index) =>
              <PoolLogin key={pool.id} description={pool.description} index={index} />)
          }
        </div>
        {
          this.state.pools.length > 0 ?
            <button type="submit" className="btn btn-lg btn-primary btn-block">Login</button> :
            <h4>No pools provided</h4>
        }
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
