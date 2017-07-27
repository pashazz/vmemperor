/**
*
* Loader
*
*/

import React from 'react';


import styles from './styles.css';

function Loader() {
  return (
    <div className={styles.spinner}>
      <div className={styles.first}></div>
      <div className={styles.second}></div>
      <div className={styles.third}></div>
    </div>
  );
}

export default Loader;
