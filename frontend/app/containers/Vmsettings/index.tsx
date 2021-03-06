/**
 *
 * VmSettings
 *
 */

import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';
import {FormattedMessage} from 'react-intl';
import {createStructuredSelector} from 'reselect';
import {compose} from 'redux';

import injectSaga from '../../utils/injectSaga';
import injectReducer from '../../utils/injectReducer';
import makeSelectVmsettings from './selectors';
import reducer from './reducer';
import messages from './messages';

import {VmInfo, VmInfoUpdate} from "../../generated-models";
import VmsettingsForm from "../../components/VmsettingsForm";

import {RouteComponentProps} from "react-router";
import {useQuery} from "react-apollo-hooks";
import {useSubscription} from "../../hooks/subscription";

interface RouterProps { //These props refer to page argument: see router.
  uuid: string //VM UUID
}

type Props = RouteComponentProps<RouterProps>;

const VmSettings = ({match: {params: {uuid}}}: Props) => {
  const {data: {vm}} = useQuery<VmInfo.Query, VmInfo.Variables>(VmInfo.Document,
    {
      variables: {
        uuid,
      }
    });
  useSubscription<VmInfoUpdate.Subscription>(VmInfoUpdate.Document,
    {
      variables: {
        uuid,
      }
    }); //Memoization inside
  return <VmsettingsForm vm={vm}/>;
}
/*
export class VmSettings extends React.PureComponent<RouteComponentProps<RouterProps>> // eslint-disable-line react/prefer-stateless-function
{
  render()
  {
    return (
      <VmInfo.Component variables={{uuid: this.props.match.params.uuid }}>
        {({ data, error, loading, subscribeToMore }) => {

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
          <VmsettingsForm
            vm={data.vm}
            update={() =>
              subscribeToMore({
                document: VmInfoUpdate.Document,
                variables: { uuid: this.props.match.params.uuid },
                updateQuery: (prev, { subscriptionData }) =>
                {
                  if (subscriptionData.data.vm)
                    return {
                      vm: subscriptionData.data.vm
                    };
                  else {
                    prev.vm.nameLabel += " (DELETED)";
                    return prev;
                  }
                }
              })
            }
          />
        );
      }}</VmInfo.Component>
    );
  }
}
*/
export default VmSettings;
