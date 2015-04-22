import Reflux from 'reflux';

const AlertActions = Reflux.createActions([
  'suc',
  'log',
  'warn',
  'err'
]);

export default AlertActions;
