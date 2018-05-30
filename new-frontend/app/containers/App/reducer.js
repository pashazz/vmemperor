import { combineReducers } from 'redux-immutable';
import { fromJS } from 'immutable';

import {
  VMLIST_MESSAGE
} from "./constants";

const initialState = fromJS(
{}
);



const vm_data = (state = initialState, action) => {
  switch (action.type)
  {
    case VMLIST_MESSAGE:
      const {type, ...message} = action.message;
      switch (type)
      {
        case 'initial':
        case 'add':
          return state.set(message.uuid, message);
        case 'change':
          return state.set(message.new_val.uuid, message.new_val);
        case 'remove':
          return state.delete(message.old_val.uuid);
        default:
          console.error('Unexpected message type: ', type);
      }

      return state;
    default:
      return state;
  }

};

export default combineReducers(
  {vm_data}
);
