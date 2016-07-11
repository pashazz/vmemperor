import Reflux from 'reflux';
import VMAPI from '../api/vmemp-api';

const TemplateActions = Reflux.createActions({
  'list': { asyncResult: true }
});

TemplateActions.list.listenAndPromise( VMAPI.template.list );

export default TemplateActions;
