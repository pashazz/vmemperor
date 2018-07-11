import { createSelector } from 'reselect';
import { List, Map } from 'immutable';

/**
 * Direct selector to the createVm state domain
 */
const makeSelectCreateVmDomain = () => state => state.get('createvm', new Map());

/**
 * Other specific selectors
 */
const makeSelectPools = () => createSelector(
  makeSelectCreateVmDomain(),
  state => state.get('pools', new List())
);

const makeSelectIsos = () => createSelector(
  makeSelectCreateVmDomain(),
  state => state.get('isos', new List())
)

const makeGetModal = () => createSelector(
  makeSelectCreateVmDomain(),
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
  makeSelectCreateVmDomain,
  makeSelectPools,
  makeGetModal,
  makeSelectIsos,
};
