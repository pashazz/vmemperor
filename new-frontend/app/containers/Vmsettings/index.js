/**
 *
 * Vmsettings
 *
 */

import React from 'react';
import T from 'prop-types';
import { connect } from 'react-redux';
import { createStructuredSelector } from 'reselect';
import { compose } from 'redux';

import injectSaga from 'utils/injectSaga';
import injectReducer from 'utils/injectReducer';
import makeSelectVmsettings from './selectors';
import reducer from './reducer';
import saga from './saga';
import VmsettingsForm from "../../components/VmsettingsForm";

export class VMSettings extends React.PureComponent { // eslint-disable-line react/prefer-stateless-function
  render() {
    return (
      <div>
        <VmsettingsForm/>
      </div>
    );
  }
}

VMSettings.propTypes = {
  dispatch: T.func.isRequired,
};

const mapStateToProps = createStructuredSelector({
  vmsettings: makeSelectVmsettings(),
});

function mapDispatchToProps(dispatch) {
  return {
    dispatch,
  };
}

const withConnect = connect(mapStateToProps, mapDispatchToProps);

const withReducer = injectReducer({ key: 'vmsettings', reducer });
const withSaga = injectSaga({ key: 'vmsettings', saga });

export default compose(
  withReducer,
  withSaga,
  withConnect,
)(VMSettings);
