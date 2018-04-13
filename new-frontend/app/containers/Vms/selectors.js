import { createSelector } from 'reselect';

/**
 * Direct selector to the vms state domain
 */
const selectVmsDomain = (state) => state.get('vms');

/**
 * Other specific selectors
 */


/**
 * Default selector used by Vms
 */

const makeSelectVms = () => createSelector(
  selectVmsDomain,
  (substate) => substate.toJS()
);

export default makeSelectVms;
export {
  selectVmsDomain,
};
