import { createSelector } from 'reselect';

/**
 * Direct selector to the templates state domain
 */
const selectTemplatesDomain = () => state => state.get('templates');

/**
 * Other specific selectors
 */
const selectTemplateList = () => createSelector(
  selectTemplatesDomain(),
  (substate) => substate.get('list')
);

/**
 * Default selector used by Templates
 */

const selectTemplates = () => createSelector(
  selectTemplatesDomain(),
  (substate) => substate.toJS()
);

const selectTemplateFilters = () => createSelector(
  selectTemplatesDomain(),
  (substate) => substate.get('filters').toJS()
);

const selectTemplateSort = () => createSelector(
  selectTemplatesDomain(),
  (substate) => substate.get('sort').toJS()
);

export default selectTemplates;
export {
  selectTemplatesDomain,
  selectTemplateList,
  selectTemplateFilters,
  selectTemplateSort,
};
