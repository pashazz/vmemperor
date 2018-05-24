/**
 *
 * Vms
 *
 */

import NextTable from 'react-bootstrap-table-next';
import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { FormattedMessage } from 'react-intl';
import { createStructuredSelector } from 'reselect';
import { compose } from 'redux';

import injectSaga from 'utils/injectSaga';
import injectReducer from 'utils/injectReducer';
import { makeSelectVmDataForTable} from "../App/selectors";
import reducer from './reducer';
import saga from './saga';
import messages from './messages';
import { Server } from 'mock-socket';
import axios from 'axios';

export class Vms extends React.Component { // eslint-disable-line react/prefer-stateless-function



  render() {
    const columns = [
      {
        dataField: 'name_label',
        text: 'Name',

      },
      {
        dataField: "power_state",
        text: "Power"
      },
      {
        dataField: "start_time",
        text: "Started at..."
      }
    ];
    return (<NextTable
    columns={columns}
    data = {this.props.vm_data}
    keyField='uuid'
    striped
    hover/>);


  }



  componentDidMount(){
  }

  componentWillUnmount()
  {
  }
}


Vms.propTypes = {
  dispatch: PropTypes.func.isRequired,
};

const mapStateToProps = createStructuredSelector({
  vm_data: makeSelectVmDataForTable(),
});

function mapDispatchToProps(dispatch) {
  return {
    dispatch,
  };
}

const withConnect = connect(mapStateToProps, mapDispatchToProps);

//const withSaga = injectSaga({ key: 'vms', saga });

export default compose(
//  withReducer, /* dont need a reducer here, it's in app component */
  // withSaga,
  withConnect,
)(Vms);
