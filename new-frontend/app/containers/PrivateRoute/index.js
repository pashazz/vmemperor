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
  async auth(login, password) {
    response = await axios.post('api/login',
      {username: login, password});

    console.log("Auth: ", response);
    //Set up cookies?

  },

  loadFromCookie() {
    let session = null;
    const cookies = document.cookie ? document.cookie.split('; ') : [];
    for (let i = cookies.length - 1; i >= 0; i--) {
      const parts = cookies[i].split('=');
      const name = parts.shift();

      if (name === 'user') {
        session = parts.join('=');
        break;
      }

    }
    return session;
},
  getSession() {
    return (this.session !== null) ? this.session : this.loadFromCookie();
  },

  async logout()
  {
    await axios.get('api/logout');
    this.session = null;
  }

};


const PrivateRoute = ({ component: Component, ...rest }) => (
  <Route
    {...rest}
    render={props =>
      authAgent.getSession() !== null ? (
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
