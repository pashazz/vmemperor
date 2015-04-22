var Reflux = require('reflux'),
    VMAPI = require('../api/vmemp-api');

var TemplateActions = Reflux.createActions({
  'list': { asyncResult: true }
});

TemplateActions.list.listenAndPromise( VMAPI.template.list );

module.exports = TemplateActions;
