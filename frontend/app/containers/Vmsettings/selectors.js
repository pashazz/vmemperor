import { createSelector } from 'reselect';

/**
 * Direct selector to the vmsettings state domain
 */
const selectVmsettingsDomain = (state) => state.get('vmsettings');

/**
 * Other specific selectors
 */


/**
 * Default selector used by VmSettings
 */

const makeSelectVmsettings = () => createSelector(
  selectVmsettingsDomain,
  (substate) => substate.toJS()
);

export default makeSelectVmsettings;
export {
  selectVmsettingsDomain,
};
