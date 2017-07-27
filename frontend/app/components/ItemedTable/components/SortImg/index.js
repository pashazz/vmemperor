import ascImg from './img/asc.gif';
import descImg from './img/desc.gif';
import sortImg from './img/sort.gif';
import React, { PropTypes as T } from 'react';

const sortImgs = {
  base: sortImg,
  asc: ascImg,
  desc: descImg,
};

const SortImg = ({ isCurrent = false, order, className }) =>
  <img className={className} src={isCurrent ? sortImgs[order] : sortImgs.base} alt={`sort ${isCurrent ? order : 'none'}`} />;

SortImg.propTypes = {
  isCurrent: T.bool.isRequired,
  className: T.string,
  order: T.oneOf(['asc', 'desc']),
};

export default SortImg;
