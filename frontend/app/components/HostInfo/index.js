/**
*
* HostInfo
*
*/

import React, { PropTypes as T } from 'react';

import { FormattedMessage, FormattedNumber } from 'react-intl';
import messages from './messages';

import styles from './styles.css';

function HostInfo({ host }) {
  return (
    <div className="col-md-4">
      <div className="panel panel-default">
        <div className="panel-heading">
          <FormattedMessage {...messages.host} values={{ name: host.name_label }} />
        </div>
        <div className="panel-body">
          <dl className="dl-horizontal">
            <dt><FormattedMessage {...messages.memory.total} /></dt>
            <dd><FormattedNumber value={host.memory_total} /> MB</dd>
            <small>
              <dt><FormattedMessage {...messages.memory.available} /></dt>
              <dd><FormattedNumber value={host.memory_available} /> MB</dd>
              <dt><FormattedMessage {...messages.memory.free} /></dt>
              <dd><FormattedNumber value={host.memory_free} /> MB</dd>
              <hr className={styles.break} />
              <dt><FormattedMessage {...messages.xen.running} /></dt>
              <dd><span className="badge">{ host.resident_VMs.length }</span></dd>
              <dt><FormattedMessage {...messages.xen.software} /></dt>
              <dd>{ host.software_version.product_brand }</dd>
              <dt><FormattedMessage {...messages.xen.version} /></dt>
              <dd>{ host.software_version.product_version }</dd>
              <dt><FormattedMessage {...messages.xen.xenVersion} /></dt>
              <dd>{ host.software_version.xen }</dd>
              <hr className={styles.break} />
              <dt><FormattedMessage {...messages.processor.model} /></dt>
              <dd>{ host.cpu_info.modelname }</dd>
              <dt><FormattedMessage {...messages.processor.frequency} /></dt>
              <dd>{ host.cpu_info.speed }MHz</dd>
              <dt><FormattedMessage {...messages.processor.cores} /></dt>
              <dd>{ host.cpu_info.cpu_count }</dd>
            </small>
          </dl>
        </div>
      </div>
    </div>
  );
}

HostInfo.propTypes = {
  host: T.any.isRequired,
};

export default HostInfo;
