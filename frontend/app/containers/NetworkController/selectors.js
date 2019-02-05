import { createSelector } from 'reselect';

/**
 * Direct selector to the networkController state domain
 */
const selectNetworkControllerDomain = (state) => state.get('networkController');

/**
 * Other specific selectors
 */


/**
 * Default selector used by NetworkController
 */

const makeSelectNetworkController = () => createSelector(
  selectNetworkControllerDomain,
  (substate) => substate.toJS()
);

export default makeSelectNetworkController;
export {
  selectNetworkControllerDomain,
};
