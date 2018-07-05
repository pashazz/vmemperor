/*
 *
 * Vncview reducer
 *
 */

import { fromJS } from 'immutable';
import {
  VNC_URL_ACQUIRED,
} from './constants';

const initialState = fromJS({});

function urlReducer(state = initialState, action) {
  switch (action.type) {
    case VNC_URL_ACQUIRED:
      return fromJS(
        {url : action.url}
      );
    default:
      return state;
  }
}

export default urlReducer;
