/**
*
* BootstrapMultiselect
*
*/

import React from 'react';
import styled from 'styled-components';

const InlineBlock = styled.div`
display: inline-block;
`;


class BootstrapMultiselect extends React.Component { // eslint-disable-line react/prefer-stateless-function
  constructor(props) {
    super(props);

    this.wrapPropagation = this.wrapPropagation.bind(this);
    this.toggle = this.toggle.bind(this);
    this.close = this.close.bind(this);
    this.open = this.open.bind(this);

    this.state = {
      opened: false,
    };
  }

  componentDidMount() {
    window.addEventListener('click', this.close);
  }

  componentWillUnmount() {
    window.removeEventListener('click', this.close);
  }

  wrapPropagation(func, ...args) {
    return (event) => {
      event.stopPropagation();
      func.apply(this, args);
    };
  }

  toggle() {
    if (this.state.opened) {
      this.close();
    } else {
      this.open();
    }
  }

  close() {
    this.setState({
      opened: false,
    });
  }

  open() {
    this.setState({
      opened: true,
    });
  }

  valueItem(item, onItemToggle) {
    const { value, selected } = item;
    const classNames = `glyphicon glyphicon-${selected ? 'check' : 'unchecked'}`;

    return (
      <li key={value} onClick={this.wrapPropagation(onItemToggle, item, !selected)}>
        <a><span className={classNames}><input type="checkbox" className={styles.valueCheckbox} readOnly checked={selected} /></span> {value}</a>
      </li>
    );
  }

  render() {
    const selectedItems = this.props.data.filter(({ selected = false }) => selected);
    const mainClassName = ['dropdown', this.state.opened ? 'open' : ''].join(' ');

    return (
      <InlineBlock className={mainClassName}>
        <button type="button" className="btn btn-default" onClick={this.wrapPropagation(this.toggle)} aria-haspopup="true" aria-expanded={this.state} >
          { this.props.buttonText(selectedItems) }
          <span className="caret"></span>
        </button>
        <ul className="dropdown-menu" aria-labelledby="dLabel">
          { this.props.data.map(item => this.valueItem(item, this.props.onChange)) }
        </ul>
      </InlineBlock>
    );
  }
}

BootstrapMultiselect.propTypes = {
  data: T.arrayOf(T.shape({
    value: T.string.isRequired,
    selected: T.bool.isRequired,
  })).isRequired,
  buttonText: T.func,
  onChange: T.func.isRequired,
};

BootstrapMultiselect.defaultProps = {
  data: [],
  buttonText: selected => `${selected.length} Selected`,
  onChange: f => f,
};

export default BootstrapMultiselect;
