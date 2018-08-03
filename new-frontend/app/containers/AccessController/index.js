/**
 *
 * AccessController
 *
 */

import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { FormattedMessage } from 'react-intl';
import { createStructuredSelector } from 'reselect';
import { compose } from 'redux';

import injectSaga from 'utils/injectSaga';
import injectReducer from 'utils/injectReducer';
import makeSelectAccessController from './selectors';
import reducer from './reducer';
import saga from './saga';
import messages from './messages';

import { Nav, NavItem, Badge, NavLink, TabContent, TabPane, Row, Col, Card, CardTitle, CardText, Button} from 'reactstrap';
import classnames from 'classnames';
import NetworkController from "../NetworkController";

export class AccessController extends React.PureComponent { // eslint-disable-line react/prefer-stateless-function
  constructor(props) {
  super(props);
  this.toggle = this.toggle.bind(this);
  this.state = {
    activeTab: 'networks',
  }
  }
 toggle(tab) {
   if (this.state.activeTab !== tab) {
      this.setState({
        activeTab: tab
      });
    }


  }
  render() {
    return (
    <div>
      <Nav tabs>
        <NavItem>
          <NavLink
            className={classnames({ active: this.state.activeTab === 'networks' })}
            onClick={() => { this.toggle('networks'); }}
          >
             Networks
          </NavLink>
          </NavItem>
      </Nav>
      <TabContent activeTab={this.state.activeTab}>
        <TabPane tabId="networks">
          <NetworkController/>
        </TabPane>
      </TabContent>
    </div>
    );
  }
}

AccessController.propTypes = {
  dispatch: PropTypes.func.isRequired,
};

const mapStateToProps = createStructuredSelector({
  accesscontroller: makeSelectAccessController(),
});

function mapDispatchToProps(dispatch) {
  return {
    dispatch,
  };
}

const withConnect = connect(mapStateToProps, mapDispatchToProps);

const withReducer = injectReducer({ key: 'accessController', reducer });
const withSaga = injectSaga({ key: 'accessController', saga });

export default compose(
  withReducer,
  withSaga,
  withConnect,
)(AccessController);
