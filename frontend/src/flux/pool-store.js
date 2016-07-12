import Reflux from 'reflux';
import PoolActions from './pool-actions';
import AlertActions from './alert-actions';
import Pool from './pool-model';

const tryParsing = function(text) {
  try {
    return JSON.parse(text);
  } catch(e) {
    return [];
  }
}

const PoolStore = Reflux.createStore({
  init() {
    this.listenToMany(PoolActions);

    this.pools = document && document.getElementById("pools-data") ? tryParsing(document.getElementById("pools-data").text) : [];
  },

  onList() {
    AlertActions.log('Getting Pool list...');
  },

  onListCompleted(response) {
    this.pools = response.map(pool => new Pool(pool));
    AlertActions.suc('Got Pool list');
    this.trigger();
  },

  onListFailed(response) {
    AlertActions.err("Coudn't get pools list");
  },

  getData() {
    return this.pools;
  }
});

export default PoolStore;
