/**
*
* StopButton
*
*/

import React from 'react';
// import styled from 'styled-components';

import AwesomeButton, {Props as ButtonProps} from '../AwesomeButton';
import {faStop} from "@fortawesome/free-solid-svg-icons/faStop";

type  Props = Pick<ButtonProps, Exclude<keyof ButtonProps, "icon" | "color">>;


const StopButton =  (props: Props) => {
  return (
    <AwesomeButton color="primary" icon={faStop} {...props}/>
  );
};

export default StopButton;
