import Reflux from'reflux';
import VMAPI from'../api/vmemp-api';

const PoolActions = Reflux.createActions({
  'list': { asyncResult: true }
});

PoolActions.list.listenAndPromise( VMAPI.pool.list );

export default PoolActions;
