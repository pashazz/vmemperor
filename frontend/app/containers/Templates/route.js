import { errorLoading, loadModule } from 'utils/asyncInjectors';

export default function route(injectReducer, injectSagas) {
  return {
    path: 'templates',
    name: 'templates',
    getComponent(nextState, cb) {
      const importModules = Promise.all([
        System.import('containers/Templates/reducer'),
        System.import('containers/Templates/sagas'),
        System.import('containers/Templates'),
      ]);

      const renderRoute = loadModule(cb);

      importModules.then(([reducer, sagas, component]) => {
        injectReducer('templates', reducer.default);
        injectSagas(sagas.default);

        renderRoute(component);
      });

      importModules.catch(errorLoading);
    },
  };
}
