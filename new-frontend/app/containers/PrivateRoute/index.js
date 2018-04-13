/**
*
* PrivateRoute
*
*/
import axios from 'axios';
import React from "react";
import {
  BrowserRouter as Router,
  Route,
  Link,
  Redirect,
  withRouter
} from "react-router-dom";

export const authAgent = {
  session: null,
  auth(login, password, callback) {
    axios.post('api/login', {username: login, pasword}).
    then(data => callback(data));
  },







};


const PrivateRoute = ({ component: Component, ...rest }) => (
  <Route
    {...rest}
    render={props =>
      authAgent.session !== null ? (
        <Component {...props} />
      ) : (
        <Redirect
          to={{
            pathname: "/login",
            state: { from: props.location }
          }}
        />
      )
    }
  />
);

export default PrivateRoute;
