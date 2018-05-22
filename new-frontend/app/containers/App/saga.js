import { take, call, put, select, all, takeEvery, takeLatest, apply, race} from 'redux-saga/effects';
import { eventChannel, END } from 'redux-saga';
import { AUTH, LOGOUT, AUTHENTICATED, LOGGED_OUT } from './constants';
import { push, LOCATION_CHANGE} from 'react-router-redux';
import { makeSelectLocation } from './selectors';
import {authAgent} from "../PrivateRoute";
import { msgVmlist } from "./actions";
import { Server } from 'mock-socket';
import axios  from 'axios';


export function* loginFlow() {
  window.beforeLogin = '/';
  let previousSession = null;
  yield take(LOCATION_CHANGE);
  while (true) { // eslint-disable-line no-constant-condition
    console.log('while true ', new Date());
    const session = authAgent.getSession();
    let location = yield select(makeSelectLocation());
    location = location.pathname;

    if (session !== null)
    {


      if (session !== previousSession) {
        yield put({type: AUTHENTICATED});
      }
      if (previousSession === null) {
        console.log('writing new session');
        previousSession = session;
      }
      console.log('Session:', session);
      if (location === '/login')
      {
        yield put(push(window.beforeLogin))
      }
      else
      {
        window.beforeLogin = location;
      }
      yield take(LOGOUT);
      try {
        yield call([authAgent,authAgent.logout]);
        yield put({type : LOGGED_OUT});
      }
      catch (e)
      {
        console.log('logout error!', e);
      }
    }
    else
    {
      if (location !== '/login') {
        window.beforeLogin = location;
        yield put(push('/login'));
      }
      const { login, password} = yield take(AUTH);

      try { //context call
        yield call([authAgent,authAgent.auth], login, password);
      }
      catch(e)
      {
        console.log('login error!',e);
      }

    }
  }
}


function socketToChannel(socket) {
  /**
   * this function converts a websocket to a redux saga event channel
   */
  return eventChannel((emit) => {
    socket.onopen = () => {
      console.log('Connection estabished');
    };
    socket.onmessage = (event) => {
      const msg = event.data;
      emit({ message : msg, error : null });
    };
    socket.onclose = (event) => {
      emit(END); //close channel
    };
    socket.onerror = (event) => {
      emit ({message : null,
        error : event.error });

    }
    //Subscriber returns an unsubscribe function
    return () => {
      socket.close();
    };
  });
}

function* channelToListenerVmlist(channel)
{
  /**
   * this function listens for VMList messages and puts an action
   */
  try {
    while (true) {
      const {message, error} = yield take(channel);
      yield put(msgVmlist(message));

    }
  }
  finally
  {
    if (yield cancelled())
    {
      channel.close();
      console.log('channel cancelled');
    }
    else {
      console.log('channel terminated');
    }
  }

}

async function connectToWebsocket() {
  const server = new Server('ws://localhost:9999');
  const res = await axios.get("vmlist-example.json");
  const jsons = res.data.split('\n');
  server.on('connection', _server => {
    jsons.map(json => {
      server.send(json);
    });
  });

}


export function* websocketFlow() {
  while (true) {
    console.log('waiting for authentication');
    console.log('authenticated');
    yield connectToWebsocket();
    console.log('starting websocket flow...');
    const sock = new WebSocket('ws://localhost:9999');
    const socketChannel = yield call(socketToChannel, sock);

    const {cancel} = yield race({ //run two effects simultaneously
        task: call(channelToListenerVmlist, socketChannel),
        cancel: take(LOGGED_OUT),
      }
    );
    if (cancel)
      socketChannel.close();
    //TODO: Bidirectional


  }
}






function* watchLoginFlow() {
  //yield takeEvery(LOCATION_CHANGE, loginFlow);
  yield loginFlow();
}

function* watchWebsocketFlow(){
  yield takeEvery(AUTHENTICATED, websocketFlow);
}
// All sagas to be loaded
export default function* rootSaga () {
  yield all([ watchLoginFlow(),
    watchWebsocketFlow() ]);

  //yield all[loginFlow()];
  //yield takeEvery(AUTH, authenticate);
  //yield takeEvery(LOGOUT, logout);
};

