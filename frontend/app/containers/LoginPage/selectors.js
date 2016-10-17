import { createSelector } from 'reselect';

/**
 * Direct selector to the loginPage state domain
 */
const selectLoginPageDomain = () => state => state.get('login');

/**
 * Other specific selectors
 */

/**
 * Default selector used by LoginPage
 */
const selectLoginPage = () => createSelector(
  selectLoginPageDomain(),
  (substate) => substate.toJS()
);

const selectPools = () => createSelector(
  selectLoginPage(),
  (substate) => substate.pools
);

export default selectLoginPage;
export {
  selectLoginPageDomain,
  selectPools,
};
