import React, { PropTypes as T } from 'react';

function displayCounter(count = 0) {
  return count > 0 ? <span className="badge">{count}</span> : '';
}

const NavItem = ({ isActive, to, text, counter, onClick }) =>
  <li className={isActive ? 'active' : ''}>
    <a href={to} onClick={onClick}>{text} {displayCounter(counter)}</a>
  </li>;

NavItem.propTypes = {
  isActive: T.bool,
  to: T.string.isRequired,
  text: T.string.isRequired,
  counter: T.number,
  onClick: T.func,
};

export default NavItem;
