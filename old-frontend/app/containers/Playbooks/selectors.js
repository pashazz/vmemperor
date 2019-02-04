import { createSelector } from 'reselect';

/**
 * Direct selector to the playbooks state domain
 */
const selectPlaybooksDomain = (state) => state.get('playbooks').get('playbooks');

/**
 * Other specific selectors
 */


/**
 * Default selector used by Playbooks
 */

const makeSelectPlaybooks = () => createSelector(
  selectPlaybooksDomain,
  (substate) => {
    if (substate.toJS)
    {
      return substate.toJS();
    }
    else {
      return [];
    }
  }
);


export {
  makeSelectPlaybooks
};
