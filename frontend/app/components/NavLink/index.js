/**
*
* NavLink
* This enables use of reactstrap with react-router
 We will use react-router-dom.NavLink as tag for reactstrap's NavLink
 See also: https://github.com/reactstrap/reactstrap/issues/83#issue-168537815


*/

import React from 'react';
import {NavLink as RouterNavLink} from 'react-router-dom';
import {NavLink as ReactstrapNavLink} from 'reactstrap';
// import styled from 'styled-components';
import T from 'prop-types';


const NavLink = props => (
  <ReactstrapNavLink tag={RouterNavLink} to={props.to} activeClassName='active'>
    {props.children}
  </ReactstrapNavLink>);

NavLink.propTypes = {
  to : T.string.isRequired
};

export default NavLink;
