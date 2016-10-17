import React, { PropTypes as T } from 'react';
import NavItem from './components/NavItem';

class Navbar extends React.Component { // eslint-disable-line react/prefer-stateless-function
  static propTypes = {
    title: T.string.isRequired,
    left: T.array,
    right: T.array,
  }

  static defaultProps = {
    title: 'App',
    left: [],
    right: [],
  }

  render() {
    const { title, left, right } = this.props;

    return (
      <nav className="navbar navbar-default">
        <div className="container">
          <div className="navbar-header">
            <a className="navbar-brand">{title}</a>;
          </div>
          <ul className="nav navbar-nav">
            {
              left.map(item => <NavItem key={item.to} {...item} />)
            }
          </ul>
          <ul className="nav navbar-nav navbar-right">
            {
              right.map(item => <NavItem key={item.to} {...item} />)
            }
          </ul>
        </div>
      </nav>
    );
  }
}

export default Navbar;
