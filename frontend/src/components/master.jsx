import React from 'react';
import Reflux from 'reflux';
import { RouteHandler, Link } from 'react-router';

import VMStore from '../flux/vm-store';
import TemplateStore from '../flux/template-store';
import SessionStore from '../flux/session-store';
import SessionActions from '../flux/session-actions';
import AlertActions from '../flux/alert-actions';
import Snackbar from './snackbar.jsx';

const NavElem = React.createClass({
  contextTypes: {
    router: React.PropTypes.func
  },

  render() {
    return (
      <li className={this.context.router.isActive(this.props.to) ? 'active': ''}>
        <Link to={this.props.to}>{this.props.children}</Link>
      </li>
    );
  }
});

const Master = React.createClass({

  mixins: [Reflux.ListenerMixin],

  getInitialState() {
    return {
      vmcol: VMStore.length(),
      templatecol: TemplateStore.length()
    };
  },

  onChange() {
    this.setState({
      vmcol: VMStore.length(),
      templatecol: TemplateStore.length()
    });
  },

  componentDidMount() {
    this.listenTo(VMStore, this.onChange);
    this.listenTo(TemplateStore, this.onChange);
  },

  render () {
    const brand = <Link to="/" className="navbar-brand">VM Emperor</Link>;
    const vmCounter = this.state.vmcol > 0 ? <span className="badge">{this.state.vmcol}</span> : '';
    const templateCounter = this.state.templatecol > 0 ? <span className="badge">{this.state.templatecol}</span> : '';

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
              <NavElem to="history">History</NavElem>
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

  _logout(e) {
    e.preventDefault();
    if (confirm("Are you sure you want to log out?")) {
      SessionActions.logout();
    } else {
      AlertActions.err("You were NOT logged out");
    }
  }
});

export default Master;
