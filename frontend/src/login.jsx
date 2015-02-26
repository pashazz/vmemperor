var React = require('react'),
    SessionActions = require('./flux/session-actions');

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
        <div className="modal-footer">
          <button type="submit" className="btn btn-primary">Login</button>
        </div>
      </form>
    );
  }

});

var LoginModal = React.createClass({
    
    render: function () {
      return (
        <div className="modal fade in" role="dialog" aria-hidden="false" style={{ display: 'block' }}>
          <div className="modal-backdrop fade in" style={{ height: '100%' }}></div>
          
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h4 className="modal-title">VM Emperor Login</h4>
              </div>

              <LoginForm />
            </div>
          </div>
        </div>
      );
    }

});

module.exports = LoginModal;