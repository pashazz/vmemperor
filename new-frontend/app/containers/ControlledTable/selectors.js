import { createSelector } from 'reselect';

/**
 * Direct selector to the controlledTable state domain
 */
const selectControlledTableDomain = (state) => state.get('controlledTable');

/**
 * Other specific selectors
 */


/**
 * Default selector used by ControlledTable
 */

const makeSelectControlledTable = () => createSelector(
  selectControlledTableDomain,
  (substate) => substate.toJS()
);

export default makeSelectControlledTable;
export {
  selectControlledTableDomain,
};
