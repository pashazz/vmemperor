/**
 *
 * Asynchronously loads the component for StatefulTable
 *
 */

import Loadable from 'react-loadable';

export default Loadable({
  loader: () => import('./index'),
  loading: () => null,
});
