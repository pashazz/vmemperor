/**
 *
 * App.react.js
 *
 * This component is the skeleton around the actual pages, and should only
 * contain code that should be seen on all pages. (e.g. navigation bar)
 *
 * NOTE: while this component should technically be a stateless functional
 * component (SFC), hot reloading does not currently support SFCs. If hot
 * reloading is not a neccessity for you then you can refactor it and remove
 * the linting exception.
 */
import React, { PropTypes as T } from 'react';
import { connect } from 'react-redux';
import { selectCurrentLocation, selectGlobalMessages, getVMCounter, getTemplatesCounter } from './selectors';
import Snackbar from 'components/Snackbar';
import Navbar from 'components/Navbar';
import { logout } from './actions';
import { push } from 'react-router-redux';

const confirmClick = func => event => {
  event.preventDefault();
  if (confirm('Are you sure you want to log out?')) {
    func();
  }
};

const navClick = (func, to) => event => {
  event.preventDefault();
  func(to);
};

const setIsActive = current =>
  target => ({
    ...target,
    isActive: current === `/${target.to}` || current === target.to,
  });

const setOnClick = dispatch =>
  target => ({
    ...target,
    onClick: navClick(dispatch, target.to),
  });

function buildNav({ counters, location, push, logout }) { // eslint-disable-line no-shadow
  return {
    left: [
      { to: 'vms', text: 'VMs', counter: counters.vms },
      { to: 'templates', text: 'Templates', counter: counters.templates },
      { to: 'create-vm', text: 'Create VM' },
      { to: 'history', text: 'History' },
    ].map(setIsActive(location)).map(setOnClick(push)),
    right: [
      { to: 'logout', text: 'Logout', onClick: confirmClick(logout) },
    ].map(setIsActive(location)),
  };
}

const App = props =>
  <div>
    <Navbar title="VM Emperor" {...buildNav(props)} />
    <div className="container">{React.Children.toArray(props.children)}</div>
    <Snackbar logs={props.logs} />
  </div>;

App.propTypes = {
  children: T.node,
  logs: T.array,
  location: T.string.isRequired,
  logout: T.func.isRequired,
  push: T.func.isRequired,
  counters: T.objectOf(T.number),
};

function mapStateToProps(state) {
  return {
    location: selectCurrentLocation()(state),
    logs: selectGlobalMessages()(state),
    counters: {
      vms: getVMCounter()(state),
      templates: getTemplatesCounter()(state),
    },
  };
}

const mapDispatchToProps = {
  push,
  logout,
};

export default connect(mapStateToProps, mapDispatchToProps)(App);
