import { createSelector } from 'reselect';

const selectRouter = (state) => state.get('route');

const makeSelectLocation = () => createSelector(
  selectRouter,
  (routerState) => routerState.location
);

export {
  makeSelectLocation,
};
