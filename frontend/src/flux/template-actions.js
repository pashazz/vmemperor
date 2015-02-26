var Reflux = require('reflux');

TemplateActions = Reflux.createActions([
  'list',
  'listSuccess',
  'listFail'
]);

module.exports = TemplateActions;