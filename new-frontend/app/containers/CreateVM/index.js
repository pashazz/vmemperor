/*
 *
 * CreateVm
 *
 */

import React from 'react';
import T from 'prop-types';
import { connect } from 'react-redux';
import { selectPools, getModal } from './selectors';
import { FormattedMessage } from 'react-intl';
import messages from './messages';
import { toggleModal, createVM } from './actions';
import styles from './styles.css';
import PoolInfo from 'components/PoolInfo';
import Modal from 'components/Modal';
import VMForm from 'components/VMForm';
import Loader from 'components/Loader';

export class CreateVm extends React.Component { // eslint-disable-line react/prefer-stateless-function
  static propTypes = {
    pools: T.any.isRequired,
    modal: T.bool.isRequired,
    toggleModal: T.func.isRequired,
    createVM: T.func.isRequired,
  };

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
              this.props.pools.map(pool => <PoolInfo key={pool.key()} pool={pool} />) :
              <div style={{ textAlign: 'center' }}><Loader /></div>
          }
        </div>
        <Modal title="VM form" lg close={this.props.toggleModal} show={this.props.modal}>
          <VMForm pools={this.props.pools} onSubmit={this.props.createVM} />
        </Modal>
      </div>
    );
  }
}

const mapStateToProps = createStructuredSelector({
  pools: makeSelectPools(),
  modal: makeGetModal(),
});

const mapDispatchToProps = {
  toggleModal,
  createVM,
};

export default connect(mapStateToProps, mapDispatchToProps)(CreateVm);
