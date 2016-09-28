import { createSelector } from 'reselect';
import { List, Map } from 'immutable';

/**
 * Direct selector to the createVm state domain
 */
const selectCreateVmDomain = () => state => state.get('create', new Map());

/**
 * Other specific selectors
 */
const selectPools = () => createSelector(
  selectCreateVmDomain(),
  state => state.get('pools', new List())
);

const getModal = () => createSelector(
  selectCreateVmDomain(),
  state => state.get('modal', false)
);

/**
 * Default selector used by CreateVm
 */

const selectCreateVm = () => createSelector(
  selectCreateVmDomain(),
  (substate) => substate.toJS()
);

export default selectCreateVm;
export {
  selectCreateVmDomain,
  selectPools,
  getModal,
};
