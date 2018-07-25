/*
 *
 * Vmsettings reducer
 *
 */

import { fromJS } from 'immutable';


const initialState = fromJS({});

function vmsettingsReducer(state = initialState, action) {
  switch (action.type) {
    default:
      return state;
  }
}

export default vmsettingsReducer;
