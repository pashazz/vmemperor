/**
 *
 * VmSettings
 *
 */

import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { FormattedMessage } from 'react-intl';
import { createStructuredSelector } from 'reselect';
import { compose } from 'redux';

import injectSaga from '../../utils/injectSaga';
import injectReducer from '../../utils/injectReducer';
import makeSelectVmsettings from './selectors';
import reducer from './reducer';
import saga from './saga';
import messages from './messages';

import { VmInfo } from "../../generated-models";
import VmsettingsForm from "../../components/VmsettingsForm";

import {RouteComponentProps} from "react-router";

interface RouterProps { //These props refer to page argument: see router.
  uuid: string //VM UUID
}

export class VmSettings extends React.PureComponent<RouteComponentProps<RouterProps>> // eslint-disable-line react/prefer-stateless-function
{
  render()
  {
    return (
      <VmInfo.Component variables={{uuid: this.props.match.params.uuid }}>
        {({ data, error, loading }) => {
        if (error)
        {
          return (<div>
          <h1>{error.message}</h1>
          </div>);
        }
        if (loading)
        {
          return '...';
        }

        return (
          <VmsettingsForm vm={data.vm}/>
        );
      }}</VmInfo.Component>
    );
  }
}




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
)(VmSettings);