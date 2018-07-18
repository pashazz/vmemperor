/*
 *
 * CreateVm
 *
 */

import React from 'react';
import T from 'prop-types';
import { connect } from 'react-redux';
import { compose } from 'redux';
import { withRouter } from 'react-router-dom';
import injectSaga from 'utils/injectSaga';
import injectReducer from 'utils/injectReducer';

import { createStructuredSelector } from 'reselect';
import { makeSelectPools, makeGetModal, makeSelectIsos, makeSelectNetworks,  makeSelectTemplates } from './selectors';
import { FormattedMessage } from 'react-intl';
import messages from './messages';
import { toggleModal, createVM, loadNetwork } from './actions';
import styles from './styles.css';
import saga from './saga';
import reducer from './reducer';

import PoolInfo from 'components/PoolInfo';
import { Modal } from  'reactstrap';
import VMForm from 'components/VMForm';
import Loader from 'components/Loader';
import IPT from 'react-immutable-proptypes';

export class CreateVm extends React.Component { // eslint-disable-line react/prefer-stateless-function
  static propTypes = {
    modal: T.bool.isRequired,
    toggleModal: T.func.isRequired,
    createVM: T.func.isRequired,
  };

  constructor(props)
  {
    super(props);
    this.createVM = this.createVM.bind(this);
  }

  createVM(form) {
    this.props.createVM(form);
    this.props.toggleModal();
  }
  render() {
    return (
      <div>
        <div className={styles.createButtonContainer}>
          <button className="btn btn-lg btn-primary" onClick={this.props.toggleModal}>
            <FormattedMessage {...messages.create} />
          </button>
        </div>
        <div className={styles.poolsContainer}>
          {
            this.props.pools.size > 0 ?
              this.props.pools.map(pool => <PoolInfo key={pool.key()} pool={pool.toJS()} />) :
              <div style={{ textAlign: 'center' }}><Loader /></div>
          }
        </div>
        <Modal title="VM form" lg toggle={this.props.toggleModal} isOpen={this.props.modal}>
          <VMForm  pools={this.props.pools}
                   isos={this.props.isos}
                   networks={this.props.networks}
                   templates={this.props.templates}
                   onNetworkChange={this.props.loadNetwork}
                   onSubmit={this.createVM} />
        </Modal>
      </div>
    );
  }
}

const mapStateToProps = createStructuredSelector({
  pools: makeSelectPools(),
  modal: makeGetModal(),
  isos: makeSelectIsos(),
  networks: makeSelectNetworks(),
  templates: makeSelectTemplates(),
});

const mapDispatchToProps = {
  toggleModal,
  createVM,
};

const withConnect = connect(mapStateToProps, mapDispatchToProps);

const withReducer = injectReducer({ key: 'createvm', reducer });
const withSaga = injectSaga({ key: 'createvm', saga });

export default compose(
  withRouter,
  withReducer,
  withSaga,
  withConnect,
)(CreateVm);


