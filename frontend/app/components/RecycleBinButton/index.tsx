/**
*
* RecycleBinButton
*
*/

import React from 'react';
// import styled from 'styled-components';
import {ButtonProps} from "react-bootstrap-table";
import {faTrashAlt} from "@fortawesome/free-solid-svg-icons/faTrashAlt";
import AwesomeButton from "../AwesomeButton";


type  Props = Pick<ButtonProps, Exclude<keyof ButtonProps, "icon" | "color">>;


const RecycleBinButton =  (props: Props) => {
  return (
    <AwesomeButton color="danger" icon={faTrashAlt} {...props}/>
  );
};


export default RecycleBinButton;
