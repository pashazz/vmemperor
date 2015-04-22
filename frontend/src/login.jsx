var React = require('react'),
    SessionActions = require('./flux/session-actions'),
    PoolStore = require('./flux/pool-store'),
    Modal = require('./components/modal.jsx');

var LoginForm = React.createClass({

  getInitialState: function() {
    return {};
  },

  handleSubmit: function(e) {
    e.preventDefault();
    SessionActions.auth(this.state);
  },

  handleChange: function(e) {
    var newState = {};
    newState[e.target.name] = e.target.value;
    this.setState(newState);
  },

  render: function (argument) {
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

});

var LoginModal = React.createClass({

    render: function () {
      return (
        <Modal title="VM Emperor Login" show>
          <LoginForm />
        </Modal>
      );
    }

});

module.exports = LoginModal;
