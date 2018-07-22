/**
 *
 * App.js
 *
 * This component is the skeleton around the actual pages, and should only
 * contain code that should be seen on all pages. (e.g. navigation bar)
 *
 * NOTE: while this component should technically be a stateless functional
 * component (SFC), hot reloading does not currently support SFCs. If hot
 * reloading is not a necessity for you then you can refactor it and remove
 * the linting exception.
 */


import React from 'react';
import { Switch, Route } from 'react-router-dom';
//import { ToastContainer } from 'react-toastify';

import HomePage from 'containers/HomePage/Loadable';
import NotFoundPage from 'containers/NotFoundPage/Loadable';
import Navbar from "../../components/Navbar";
import PrivateRoute from 'containers/PrivateRoute';
import VMs from 'containers/Vms/Loadable';
import LoginPage from 'containers/LoginPage/Loadable';
import CreateVM from "../CreateVM";
import Logout from 'containers/Logout/Loadable';
import VncView from 'containers/Vncview/Loadable';


import { compose } from 'redux';
import injectReducer from 'utils/injectReducer';
import reducer from './reducer';
import VMSettings from "../Vmsettings";

function App() {
  return (
    <div>
      <Navbar/>
      <Switch>
        <Route exact path="/" component={HomePage} />
        <Route path="/login" component={LoginPage} />
        <PrivateRoute  path="/vms" component={VMs} />
        <PrivateRoute path="/vmsettings/:uuid" component={VMSettings}/>
        <PrivateRoute path="/create-vm" component={CreateVM}/>
        <PrivateRoute path="/logout" component={Logout} />
        <PrivateRoute path="/desktop/:uuid" component={VncView}/>
        <Route component={NotFoundPage} />
      </Switch>
    </div>
  );
}

const withReducer = injectReducer({ key: 'app', reducer });

export default compose(
  withReducer,
)(App);
