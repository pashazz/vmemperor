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
import { FormattedMessage } from 'react-intl';
import messages from './messages';
import styles from './styles.css'
import {Button} from 'reactstrap';

import PoolInfo from 'components/PoolInfo';
import { Modal } from  'reactstrap';
import VMForm from 'components/VMForm';
import Loader from 'components/Loader';
import IPT from 'react-immutable-proptypes';



interface  Props{

}
interface State {
  modal : boolean,
}


export class CreateVm extends React.Component<Props,State> { // eslint-disable-line react/prefer-stateless-function

  constructor(props)
  {
    super(props);
    this.toggleModal = this.toggleModal.bind(this);
    this.state = {
      modal: false,
    }
  }


  toggleModal(e)
  {
    const toggle = () => this.setState((prevState) => {
      return {...prevState, modal: !prevState.modal}
    });

    if (this.state.modal)
    {
      if (confirm("Do you want to leave?")) {
        toggle();
      }
      else
      {
        console.log("Prevent default...")
        e.stopPropagation();
      }

    }
    else {
      toggle();
    }
  }
  render() {
    return (
      <div>
        {/*<div className={styles.createButtonContainer}>
          <Button onClick={this.props.toggleModal}>
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
        <Modal title="VM form"
               lg
               toggle={this.toggleModal}
               isOpen={this.props.modal}>
          <VMForm  pools={this.props.pools}
                   isos={this.props.isos}
                   networks={this.props.networks}
                   templates={this.props.templates}
                   onNetworkChange={this.props.loadNetwork}
                   onSubmit={this.createVM} />
        </Modal>*/}
      </div>
    );
  }
}



export default compose(
  withRouter,
)(CreateVm);


