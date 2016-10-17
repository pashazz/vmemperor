import { errorLoading, loadModule } from 'utils/asyncInjectors';

export default function route(injectReducer, injectSagas) {
  return {
    path: 'history',
    name: 'history',
    getComponent(nextState, cb) {
      const importModules = Promise.all([
        System.import('containers/History/reducer'),
        System.import('containers/History/sagas'),
        System.import('containers/History'),
      ]);

      const renderRoute = loadModule(cb);

      importModules.then(([reducer, sagas, component]) => {
        injectReducer('history', reducer.default);
        injectSagas(sagas.default);

        renderRoute(component);
      });

      importModules.catch(errorLoading);
    },
  };
}
