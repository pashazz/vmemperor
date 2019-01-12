import { createSelector } from 'reselect';

/**
 * Direct selector to the createVm state domain
 */
const selectCreateVmDomain = (state) => state.get('createVm');

/**
 * Other specific selectors
 */


/**
 * Default selector used by CreateVm
 */

const makeSelectCreateVm = () => createSelector(
  selectCreateVmDomain,
  (substate) => substate.toJS()
);

export default makeSelectCreateVm;
export {
  selectCreateVmDomain,
};
