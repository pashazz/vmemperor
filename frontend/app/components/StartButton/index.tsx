/**
*
* StartButton
*
*/

import React from 'react';
// import styled from 'styled-components';

import AwesomeButton, {Props as ButtonProps} from '../AwesomeButton';
import {faPlay} from "@fortawesome/free-solid-svg-icons";

type  Props = Pick<ButtonProps, Exclude<keyof ButtonProps, "icon" | "color">>;


const StartButton =  (props: Props) => {
  return (
    <AwesomeButton color="primary" icon={faPlay} {...props}/>
  );
};



export default StartButton;
