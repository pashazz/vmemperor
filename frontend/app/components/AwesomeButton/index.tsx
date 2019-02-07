import React, {Fragment} from "react";
import {ButtonProps, Button} from 'reactstrap';
import {FontAwesomeIcon, Props as IconProps} from "@fortawesome/react-fontawesome";


export interface  Props  extends ButtonProps, Pick<IconProps, "icon">{
  color: "primary" | "secondary" | "success" | "info" | "warning" | "danger" | "link" | string;
}

const AwesomeButton = ({icon, ...props} : Props) => {
  return (
    <Button {...props}>
      <FontAwesomeIcon icon={icon}/>
    </Button>
  )
};

export default AwesomeButton;
