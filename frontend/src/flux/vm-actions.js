var Reflux = require('reflux'),
    VMAPI = require('../api/vmemp-api');

VMActions = Reflux.createActions({
  'list': { asyncResult: true },
  'start': { asyncResult: true },
  'shutdown': { asyncResult: true }
});

VMActions.list.listenAndPromise( VMAPI.vm.list );
VMActions.start.listenAndPromise( VMAPI.vm.start );
VMActions.shutdown.listenAndPromise( VMAPI.vm.shutdown );

module.exports = VMActions;