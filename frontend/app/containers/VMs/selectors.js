import { createSelector } from 'reselect';

/**
 * Direct selector to the VMs state domain
 */
const selectVMsDomain = () => state => state.get('vms');

/**
 * Other specific selectors
 */

/**
 * Default selector used by LoginPage
 */
const selectVMs = () => createSelector(
  selectVMsDomain(),
  (substate) => substate.toJS()
);

const selectVMList = () => createSelector(
  selectVMsDomain(),
  (substate) => substate.get('list')
);

const selectVMFilters = () => createSelector(
  selectVMsDomain(),
  (substate) => substate.get('filters').toJS()
);

const selectVMSort = () => createSelector(
  selectVMsDomain(),
  (substate) => substate.get('sort').toJS()
);

export default selectVMs;
export {
  selectVMsDomain,
  selectVMList,
  selectVMFilters,
  selectVMSort,
};
