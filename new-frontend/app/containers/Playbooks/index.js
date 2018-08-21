/**
 *
 * Playbooks
 *
 */

import React from 'react';
import T from 'prop-types';
import IPT from 'react-immutable-proptypes';
import { connect } from 'react-redux';
import { FormattedMessage } from 'react-intl';
import { createStructuredSelector } from 'reselect';
import { compose } from 'redux';

import injectSaga from 'utils/injectSaga';
import injectReducer from 'utils/injectReducer';
import {makeSelectPlaybooks }from './selectors';
import reducer from './reducer';
import saga from './saga';
import messages from './messages';
import { ButtonDropdown, DropdownToggle, DropdownMenu, DropdownItem } from 'reactstrap';
import PlaybookForm from "./playbookForm";


export class Playbooks extends React.Component { // eslint-disable-line react/prefer-stateless-function

    constructor(props) {
    super(props);

    this.toggle = this.toggle.bind(this);
    this.state = {
      dropdownOpen: false,
      currentId: null,
    };
  }
 toggle() {
    this.setState({
      dropdownOpen: !this.state.dropdownOpen
    });
  }

  onClick = (id) => () => {
      this.setState( {
        currentId: id,
      });
      console.log(this.state.currentId);
  };



  render() {
    const { playbooks } = this.props;
    const { currentId } = this.state;
    console.log("Current playbook ID", this.state.currentId);
    return (
      <div>
        <ButtonDropdown size="lg" isOpen={this.state.dropdownOpen} toggle={this.toggle}>
        <DropdownToggle
          size="lg"
          caret>
          {this.props.buttonText}
        </DropdownToggle>
        <DropdownMenu>
          {
            this.props.playbooks.map((item, key) =>
              {
                return (
                  <DropdownItem
                    key={key}
                    id={item.id}
                    onClick={this.onClick(key)}
                  >
                    {item.name}
                  </DropdownItem>);
              }
            )
          }
        </DropdownMenu>
      </ButtonDropdown>
        {
          currentId !== null && (
            <PlaybookForm
              book={playbooks[currentId]}/>)
        }
      </div>
    );
  }

  static propTypes = {
      buttonText: T.string,
      playbooks: IPT.list.isRequired,
  };
   static defaultProps = {
     buttonText: "Playbooks"
   }

}



const mapStateToProps = createStructuredSelector({
  playbooks: makeSelectPlaybooks(),
});

function mapDispatchToProps(dispatch) {
  return {
    dispatch,
  };
}

const withConnect = connect(mapStateToProps, mapDispatchToProps);

const withReducer = injectReducer({ key: 'playbooks', reducer });
const withSaga = injectSaga({ key: 'playbooks', saga });

export default compose(
  withReducer,
  withSaga,
  withConnect,
)(Playbooks);
