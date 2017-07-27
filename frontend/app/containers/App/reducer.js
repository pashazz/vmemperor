import { fromJS } from 'immutable';
import { combineReducers } from 'redux-immutable';
import { NEW_MESSAGE } from './constants';

const logsInitial = fromJS([]);

function logs(state = logsInitial, action) {
  switch (action.type) {
    case NEW_MESSAGE:
      return state.push(fromJS(action.message));
    default:
      return state;
  }
}

export default combineReducers({
  logs,
});
