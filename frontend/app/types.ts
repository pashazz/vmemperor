import Redux from "redux";
import {SagaIterator, Task} from "redux-saga";

export interface IStore<T> extends Redux.Store<T> {
  runSaga?: (saga: (...args: any[]) => SagaIterator, ...args: any[]) => Task; // TODO: cleanup
  injectedReducers?: Redux.ReducersMapObject;
  injectedSagas?: object;
}
