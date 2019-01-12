/**
 *
 * Asynchronously loads the component for Vmsettings
 *
 */

import Loadable from 'react-loadable';

export default Loadable({
  loader: () => import('./index'),
  loading: () => null,
});
