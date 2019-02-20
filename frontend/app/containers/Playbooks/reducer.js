/*
 *
 * Playbooks reducer
 *
 */

import { fromJS } from 'immutable';
import { combineReducers } from 'redux-immutable';
import {
  SET_PLAYBOOKS,
} from './constants';

const playbooks = (state = fromJS([]), action) =>
{
  switch (action.type) {
    case SET_PLAYBOOKS:
      return fromJS(action.data);
    default:
      return state;
  }
};

export default  combineReducers(
  {
    playbooks,
  }
)


