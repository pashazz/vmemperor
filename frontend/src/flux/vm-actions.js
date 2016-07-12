import Reflux from 'reflux';
import VMAPI from '../api/vmemp-api';

const VMActions = Reflux.createActions({
  'list': { asyncResult: true },
  'start': { asyncResult: true },
  'shutdown': { asyncResult: true },
  'create': { asyncResult: true }
});

VMActions.list.listenAndPromise( VMAPI.vm.list );
VMActions.start.listenAndPromise( VMAPI.vm.start );
VMActions.shutdown.listenAndPromise( VMAPI.vm.shutdown );
VMActions.create.listenAndPromise( VMAPI.vm.create );

export default VMActions;
