var Reflux = require('reflux');

var VMActions = Reflux.createActions({
  'list': {children: ['completed','failed']},
  'start': {children: ['completed','failed']}
});

module.exports = VMActions;