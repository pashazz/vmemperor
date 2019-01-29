/**
 *
 * Playbooks
 *
 */

import React from 'react';
//import KeyType from 'prop-types';
//import IPT from 'react-immutable-proptypes';
//import { connect } from 'react-redux';
//import { FormattedMessage } from 'react-intl';
//import { createStructuredSelector } from 'reselect';
import { compose } from 'redux';
//import injectSaga from 'utils/injectSaga';
//import injectReducer from 'utils/injectReducer';
import {makeSelectPlaybooks }from './selectors';
//import reducer from './reducer';
//import saga from './saga';
//import messages from './messages';
import { ButtonDropdown, DropdownToggle, DropdownMenu, DropdownItem } from 'reactstrap';
import PlaybookForm from "./playbookForm";
import { executePlaybook } from "./actions";
import {PlaybookList} from "../../generated-models";

interface Props {
  vms: string[]
}
interface State {
  dropdownOpen : boolean,
  currentId: number | null,
}

export class Playbooks extends React.Component<Props, State> { // eslint-disable-line react/prefer-stateless-function

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
    const { currentId } = this.state;
    console.log("Current playbook ID", this.state.currentId);
    return (
      <PlaybookList.Component>
        {({data, error, loading}) => {
          if (error) {
            return (<div>
              <h1>{error.message}</h1>
            </div>);
          }
          if (loading) {
            return '...';
          }

          return (
            <div>
              <ButtonDropdown size="lg" isOpen={this.state.dropdownOpen} toggle={this.toggle}>
                <DropdownToggle
                  size="lg"
                  caret>
                  Playbooks
                </DropdownToggle>
                <DropdownMenu>
                  {
                    data.playbooks.map((item, key) => {
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
                    book={data.playbooks[currentId]}
                    vms={this.props.vms}
                  />)
              }
            </div>);
        }
        }
      </PlaybookList.Component>
    );
  }

}


/*
const mapStateToProps = createStructuredSelector({
  playbooks: makeSelectPlaybooks(),
});
const mapDispatchToProps = {
  executePlaybook
};
*/
//const withConnect = connect(mapStateToProps, mapDispatchToProps);

//const withReducer = injectReducer({ key: 'playbooks', reducer });
//const withSaga = injectSaga({ key: 'playbooks', saga });

export default compose(
  //withReducer,
  //withSaga,
  //withConnect,
)(Playbooks);
