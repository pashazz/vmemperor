import Reflux from 'reflux';
import VMAPI from '../api/vmemp-api';

const TemplateActions = Reflux.createActions({
  'list': { asyncResult: true },
  'enable': { asyncResult: true },
  'disable': { asyncResult: true }
});

TemplateActions.list.listenAndPromise( VMAPI.template.list );
TemplateActions.enable.listenAndPromise( VMAPI.template.enable );
TemplateActions.disable.listenAndPromise( VMAPI.template.disable );

export default TemplateActions;
