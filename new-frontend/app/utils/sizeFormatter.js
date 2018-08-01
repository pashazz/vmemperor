import React from "react";

export const sizeFormatter = (cell, row) => {
  const suffixes = ['b', 'Kb', 'Mb', 'Gb', 'Tb', 'Pb'];
  let number = Number(cell);
  let i = 0;
  if (number < 1) {
    number = 0;
  }
  else {
    i = Math.trunc(Math.log(number) / Math.log(1024)) + 1;
    number = number / Math.pow(1024, i);

    if (number <= 0.5) {
      number *= 1024;
      i -= 1;
    }
  }
  const newNumber = +number.toFixed(2);
  if (newNumber !== number) {
    number = "~" + newNumber;
  }
  return (
    <span>
      {number + " " + suffixes[i]}
    </span>
  );

};
