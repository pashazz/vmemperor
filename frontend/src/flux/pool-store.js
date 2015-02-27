var Reflux = require('reflux'),
    PoolActions = require('./pool-actions'),
    AlertActions = require('./alert-actions'),
    VMAPI = require('../api/vmemp-api');

var tryParsing = function(text) {
  try {
    return JSON.parse(text);
  } catch(e) {
    return [];
  }
}

PoolsStore = Reflux.createStore({
  init: function() {
    this.listenTo(PoolActions.list, this.list);
    this.listenTo(PoolActions.listSuccess, this.onListSuccess);

    this.pools = document && document.getElementById("pools-data") ? tryParsing(document.getElementById("pools-data").text) : [];
  },

  list: function() {
    VMAPI.pools()
      .then(this.onListSucess)
      .catch(function(response) {
        AlertActions.err("Coudn't get pools list");
      });
  },

  onListSuccess: function(response) {
    this.pools = response.data;
    this.trigger();
  },

  getData: function() {
    return this.pools;
  }
});

module.exports = PoolsStore;