var React = require('react'),
    Reflux = require('reflux'),
    Router = require('react-router'),
    RouteHandler = Router.RouteHandler,
    Link = Router.Link;

var VMStore = require('../flux/vm-store');


var NavElem = React.createClass({
  mixins: [Router.State],

  render: function() {
    return (
      <li className={this.isActive(this.props.to) ? 'active': ''}>
        <Link to={this.props.to}>{this.props.children}</Link>
      </li>
    );
  }
});

var Master = React.createClass({

  mixins: [Reflux.ListenerMixin],

  getInitialState: function() {
    return { vmcol: VMStore.length() };
  },

  onVMChange: function() {
    this.setState({ vmcol: VMStore.length() });
  },

  componentDidMount: function() {
    this.listenTo(VMStore, this.onVMChange);
  },

  render: function () {
    var brand = <Link to="/" className="navbar-brand">VM Emperor</Link>;
    var vmCounter = this.state.vmcol > 0 ? <span className="badge">{this.state.vmcol}</span> : '';

    return (
      <div>
        <nav className="navbar navbar-default">
          <div className="container">
            <div className="navbar-header">
              {brand}
            </div>
            <ul className="nav navbar-nav">
              <NavElem to="vms">VMs {vmCounter}</NavElem>
              <NavElem to="templates">Templates</NavElem>
              <NavElem to="create-vm">Create VM</NavElem>
            </ul>
            <ul className="nav navbar-nav navbar-right">
              <li><a onClick={this._logout} href="#">Logout</a></li>
            </ul>
          </div>
        </nav>

        <div className="container">
          <RouteHandler/>
        </div>
      </div>
    );
  },

  _logout: function(event) {
    if (confirm("Are you sure you want to log out?")) {
      console.log("You were logged out");
    } else {
      console.log("You were NOT logged out");
    }
  }
});

module.exports = Master;