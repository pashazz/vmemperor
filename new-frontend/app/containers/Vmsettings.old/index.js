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
import {makeSelectVminfo} from './selectors';
import { requestVMInfo} from "./actions";
import reducer from './reducer';
import saga from './saga';
import VmsettingsForm from "../../components/VmsettingsForm";
import VM from 'models/VM';

export class VMSettings extends React.PureComponent { // eslint-disable-line react/prefer-stateless-function

  render() {
    return (
      <div>
        <VmsettingsForm vm={this.props.vminfo}/>
      </div>
    );
  }
}

VMSettings.propTypes = {
  requestVMInfo: T.func.isRequired,
  vminfo: T.instanceOf(VM)
};

const mapStateToProps = createStructuredSelector({
  vminfo: makeSelectVminfo(),
});

const mapDispatchToProps = {
  requestVMInfo,
};

const withConnect = connect(mapStateToProps, mapDispatchToProps);

const withReducer = injectReducer({ key: 'vmsettings', reducer });
const withSaga = injectSaga({ key: 'vmsettings', saga });

export default compose(
  withReducer,
  withSaga,
  withConnect,
)(VMSettings);
