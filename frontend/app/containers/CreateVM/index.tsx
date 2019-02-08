/*
 *
 * CreateVm
 *
 */

import React, {useState} from 'react';
import {FormattedMessage} from 'react-intl';
import messages from './messages';
import styles from './styles.css'
import {Button} from 'reactstrap';

import PoolInfo from '../../components/PoolInfo';
import {useQuery} from "react-apollo-hooks";
import {Change, PoolList, PoolListUpdate} from "../../generated-models";
import {useSubscription} from "../../hooks/subscription";
import {handleAddOfValue, handleAddRemove, handleRemoveOfValueByUuid} from "../../cacheUtils";





const CreateVM = () => {
  const { data: {pools } } = useQuery<PoolList.Query>(PoolList.Document);

  useSubscription<PoolListUpdate.Subscription>(PoolListUpdate.Document, {
    onSubscriptionData({client, subscriptionData}) {
      const change = subscriptionData.pools;
      handleAddRemove(client, PoolList.Document, 'pools', change);
    },

  });

  const [modal, setModal] = useState(false); //This is modality of CreateVM form
  const toggleModal = (e: Event) => {
    if (!modal || confirm("Do you want to leave?")){
        setModal(!modal);
      }
    else{
      e.stopPropagation();
    }
  };

  return (
    <div className={styles.poolsContainer}>
      {
        pools.length > 0 ?
          pools.map(pool => <PoolInfo key={pool.uuid} pool={pool}/>)
          : <h1>No pools available</h1>

      }
    </div>
  )



};
export default CreateVM;
/*
export class CreateVm_ extends React.Component{ // eslint-disable-line react/prefer-stateless-function

  render() {
    return (
      <div>
        <div className={styles.createButtonContainer}>
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
        </Modal>

      </div>
    );
  }
}

*/


