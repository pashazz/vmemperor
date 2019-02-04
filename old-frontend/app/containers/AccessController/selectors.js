import { createSelector } from 'reselect';

/**
 * Direct selector to the accessController state domain
 */
const selectAccessControllerDomain = (state) => state.get('accessController');

/**
 * Other specific selectors
 */


/**
 * Default selector used by AccessController
 */

const makeSelectAccessController = () => createSelector(
  selectAccessControllerDomain,
  (substate) => substate.toJS()
);

export default makeSelectAccessController;
export {
  selectAccessControllerDomain,
};
