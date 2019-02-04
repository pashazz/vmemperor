import React from 'react';
import T from 'prop-types';


import Template from './subforms/Template';
import Storage from './subforms/Storage';
import Network from './subforms/Network';
import Pool from './subforms/Pool';
import Fullname from './subforms/Fullname';
import Link from './subforms/Link';
import Description from './subforms/Description';
import Passwords from './subforms/Passwords';
import CPU from './subforms/CPU';
import RAM from './subforms/RAM';
import HDD from './subforms/HDD';
import Hook from './subforms/Hook';
import Connection from './subforms/Connection';
import ISO from './subforms/ISO';
import Name from './subforms/Name';

const firstTouchWrapper = (WrappedComponent) =>
  class InputWraper extends React.Component {
    static propTypes = {
      onChange: T.func.isRequired,
    };

    constructor(props) {
      super(props);

      this.onFirstChange = this.onFirstChange.bind(this);

      this.state = {
        touched: false,
      };
    }

    onFirstChange(...args) {
      this.setState({ touched: true });
      this.props.onChange.apply(null, args);
    }

    render() {
      const { onChange, ...otherProps } = this.props;

      return (
        <WrappedComponent
          {...otherProps}
          touched={this.state.touched}
          onChange={this.state.touched ? onChange : this.onFirstChange}
        />
      );
    }
  };

const exportObject = {
  Pool: Pool,
  Template:Template,
  Storage: Storage,
  Network: Network,
  Fullname: Fullname,
  Link: Link,
  Passwords: Passwords,
  Description: Description,
  CPU: CPU,
  RAM: RAM,
  HDD: HDD,
  Hook,
  Connection: Connection,
  ISO,
  Name: Name,

};

export default exportObject;
