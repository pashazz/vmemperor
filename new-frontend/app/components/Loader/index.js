/**
*
* Loader
*
*/

import React from 'react';
import { PacmanLoader } from 'react-spinners';


function Loader() {
  return (
    <div className='sweet-loading'>
      <PacmanLoader loading/>
    </div>
  );
}

export default Loader;
