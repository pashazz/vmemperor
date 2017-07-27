import { List, Map } from 'immutable';
import { createSelector } from 'reselect';

// selectLocationState expects a plain JS object for the routing state
const selectLocationState = () => {
  let prevRoutingState;
  let prevRoutingStateJS;

  return (state) => {
    const routingState = state.get('route'); // or state.route

    if (!routingState.equals(prevRoutingState)) {
      prevRoutingState = routingState;
      prevRoutingStateJS = routingState.toJS();
    }

    return prevRoutingStateJS;
  };
};

const selectRoute = state => state.get('route', new Map());
const selectGlobal = state => state.get('global', new Map());
const selectVMsDomain = state => state.get('vms', new Map());
const selectTemplatesDomain = state => state.get('templates', new Map());

const selectCurrentLocation = () => createSelector(
  selectRoute,
  state => state.getIn(['locationBeforeTransitions', 'pathname'])
);

const selectGlobalMessages = () => createSelector(
  selectGlobal,
  state => state.get('logs', new List()).toJS()
);

const getVMCounter = () => createSelector(
  selectVMsDomain,
  state => state.get('list', new List()).size
);

const getTemplatesCounter = () => createSelector(
  selectTemplatesDomain,
  state => state.get('list', new List()).size
);

export {
  selectCurrentLocation,
  selectLocationState,
  selectGlobalMessages,
  getVMCounter,
  getTemplatesCounter,
};
