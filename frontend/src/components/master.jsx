var React = require('react'),
    Reflux = require('reflux'),
    Router = require('react-router'),
    RouteHandler = Router.RouteHandler,
    Link = Router.Link;

var VMStore = require('../flux/vm-store')
    TemplateStore = require('../flux/template-store'),
    Snackbar = require('./snackbar.jsx');


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
    return { 
      vmcol: VMStore.length(), 
      templatecol: TemplateStore.length()
    };
  },

  onChange: function() {
    this.setState({ 
      vmcol: VMStore.length(), 
      templatecol: TemplateStore.length()
    });
  },

  componentDidMount: function() {
    this.listenTo(VMStore, this.onChange);
    this.listenTo(TemplateStore, this.onChange);
  },

  render: function () {
    var brand = <Link to="/" className="navbar-brand">VM Emperor</Link>;
    var vmCounter = this.state.vmcol > 0 ? <span className="badge">{this.state.vmcol}</span> : '';
    var templateCounter = this.state.templatecol > 0 ? <span className="badge">{this.state.templatecol}</span> : '';

    return (
      <div>
        <nav className="navbar navbar-default">
          <div className="container">
            <div className="navbar-header">
              {brand}
            </div>
            <ul className="nav navbar-nav">
              <NavElem to="vms">VMs {vmCounter}</NavElem>
              <NavElem to="templates">Templates {templateCounter}</NavElem>
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

        <Snackbar />
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