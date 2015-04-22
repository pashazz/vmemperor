var Reflux = require('reflux'),
    PoolActions = require('./pool-actions'),
    AlertActions = require('./alert-actions');

var tryParsing = function(text) {
  try {
    return JSON.parse(text);
  } catch(e) {
    return [];
  }
}

var PoolStore = Reflux.createStore({
  init: function() {
    this.listenToMany(PoolActions);

    this.pools = document && document.getElementById("pools-data") ? tryParsing(document.getElementById("pools-data").text) : [];
  },

  onListCompleted: function(response) {
    this.pools = response;
    this.trigger();
  },

  onListFailed: function(response) {
    AlertActions.err("Coudn't get pools list");
  },

  getData: function() {
    return this.pools;
  }
});

module.exports = PoolStore;
