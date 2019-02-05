/*
 *
 * LoginPage reducer
 *
 */

import { fromJS } from 'immutable';
import {
  SET_POOLS,
} from './constants';

const initialState = fromJS({
  pools: [],
});

function loginPageReducer(state = initialState, action) {
  switch (action.type) {
    case SET_POOLS:
      return state.set('pools', action.pools);
    default:
      return state;
  }
}

export default loginPageReducer;
