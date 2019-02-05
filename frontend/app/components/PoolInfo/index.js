/**
*
* PoolInfo
*
*/

import React from 'react';
import T from 'prop-types';
import { FormattedMessage, FormattedNumber } from 'react-intl';
import messages from './messages';
import HostInfo from 'components/HostInfo';

function PoolInfo({ pool }) {
  const { description, hdd_available: hdd, host_list: hosts } = pool;
  return (
    <div className="panel panel-default">
      <div className="panel-heading">
        <h3 className="panel-title">{ description }</h3>
      </div>
      <div className="panel-body">
        <div className="row">
          { hosts.map((host, idx) => <HostInfo key={idx} host={host} />) }
        </div>
        <dl className="dl-horizontal">
          <dt><FormattedMessage {...messages.hddPromt} /></dt>
          <dd><FormattedNumber value={hdd} /> GB</dd>
        </dl>
      </div>
    </div>
  );
}

PoolInfo.propTypes = {
  pool: T.shape({
    description: T.string.isRequired,
    hdd_available: T.number.isRequired,
    host_list: T.array.isRequired,
  }).isRequired,
};

export default PoolInfo;
