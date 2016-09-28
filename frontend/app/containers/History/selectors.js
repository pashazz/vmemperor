import { createSelector } from 'reselect';
import { Map } from 'immutable';
/**
 * Direct selector to the history state domain
 */
const selectHistoryDomain = () => state => state.get('history');

/**
 * Other specific selectors
 */
const selectVMs = () => createSelector(
  selectHistoryDomain(),
  (substate) => substate.get('vms', new Map())
);

const getVMList = () => createSelector(
  selectVMs(),
  (substate) => substate.map((v, k) => v.set('id', k)).valueSeq()
);

const selectVMIds = () => createSelector(
  selectVMs(),
  (substate) => substate.keySeq().toJS()
);

/**
 * Default selector used by History
 */

const selectHistory = () => createSelector(
  selectHistoryDomain(),
  (substate) => substate.toJS()
);

export default selectHistory;
export {
  selectHistoryDomain,
  selectVMIds,
  selectVMs,
  getVMList,
};
