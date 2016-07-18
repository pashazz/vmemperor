import Reflux from 'reflux';
import VMAPI from '../api/vmemp-api';

const TemplateActions = Reflux.createActions({
  'list': { asyncResult: true },
  'enable': { asyncResult: true },
  'disable': { asyncResult: true },
  'update': { asyncResult: true }
});

TemplateActions.list.listenAndPromise( VMAPI.template.list );
TemplateActions.enable.listenAndPromise( VMAPI.template.enable );
TemplateActions.disable.listenAndPromise( VMAPI.template.disable );
TemplateActions.update.listenAndPromise( VMAPI.template.update );

export default TemplateActions;
